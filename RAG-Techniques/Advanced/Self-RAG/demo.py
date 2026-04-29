"""Self-RAG 最小教学实现。

复现 Asai et al. 2023《Self-RAG: Learning to Retrieve, Generate, and Critique
through Self-Reflection》中的四个反思决策点。原论文通过微调让模型直接吐
出反思 token，本 demo 用 prompt 让通用 LLM 扮演同样的角色，便于学习者
逐步体会"何时检索 / 哪段相关 / 是否被支持 / 整体是否有用"四步流程。

四类反思 token：

    Retrieve  : {Yes, No}              —— 是否需要检索
    IsRel     : {Relevant, Irrelevant} —— 当前段落是否与问题相关
    IsSup     : {Fully, Partial, No}   —— 答案是否被段落支持
    IsUse     : {1..5}                 —— 整体回答的有用性

运行：
    export DASHSCOPE_API_KEY=...
    export OPENAI_API_KEY=...        # 或兼容网关
    export OPENAI_BASE_URL=...       # 可选
    uv run python demo.py
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

import numpy as np
from langchain_community.embeddings import DashScopeEmbeddings
from openai import OpenAI

CHAT_MODEL = "gpt-5.4"

RetrieveDecision = Literal["Yes", "No"]
RelevanceLabel = Literal["Relevant", "Irrelevant"]
SupportLabel = Literal["Fully", "Partial", "No"]


@dataclass(frozen=True)
class PassageJudgement:
    """单个候选段落的反思结果。"""

    passage: str
    is_relevant: RelevanceLabel
    draft_answer: str
    is_supported: SupportLabel


@dataclass(frozen=True)
class SelfRAGResult:
    """一次完整 Self-RAG 流程的所有反思痕迹。"""

    query: str
    retrieve: RetrieveDecision
    judgements: tuple[PassageJudgement, ...]
    final_answer: str
    utility: int


def _make_client() -> OpenAI:
    kwargs: dict[str, str] = {}
    base = os.environ.get("OPENAI_BASE_URL")
    if base:
        kwargs["base_url"] = base
    return OpenAI(**kwargs)


def _chat(client: OpenAI, prompt: str) -> str:
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return (resp.choices[0].message.content or "").strip()


class SimpleVectorStore:
    """最小向量库：DashScope embedding + 余弦相似度。"""

    def __init__(self) -> None:
        self._embedder = DashScopeEmbeddings()
        self._docs: list[str] = []
        self._embs: list[list[float]] = []

    def add(self, doc: str) -> None:
        self._docs.append(doc)
        self._embs.append(self._embedder.embed_query(doc))

    def search(self, query: str, top_k: int = 3) -> list[str]:
        if not self._docs:
            return []
        q = np.asarray(self._embedder.embed_query(query))
        mat = np.asarray(self._embs)
        sims = mat @ q / (np.linalg.norm(mat, axis=1) * np.linalg.norm(q) + 1e-8)
        idx = np.argsort(-sims)[:top_k]
        return [self._docs[i] for i in idx]


class SelfRAG:
    """Self-RAG 推理器：把四个反思决策串成流水线。"""

    def __init__(self, client: OpenAI, store: SimpleVectorStore) -> None:
        self._client = client
        self._store = store

    def _decide_retrieve(self, query: str) -> RetrieveDecision:
        prompt = (
            "判断回答下面的问题是否需要外部知识。\n"
            "只输出一个词：Yes 或 No。\n"
            f"问题：{query}"
        )
        out = _chat(self._client, prompt)
        return "Yes" if out.lower().startswith("y") else "No"

    def _judge_relevance(self, query: str, passage: str) -> RelevanceLabel:
        prompt = (
            "判断下面的段落是否与问题相关。\n"
            "只输出一个词：Relevant 或 Irrelevant。\n"
            f"问题：{query}\n段落：{passage}"
        )
        out = _chat(self._client, prompt).lower()
        return "Irrelevant" if out.startswith("ir") else "Relevant"

    def _draft(self, query: str, passage: str) -> str:
        prompt = (
            "仅基于以下段落回答问题，不要引入额外知识。\n"
            f"问题：{query}\n段落：{passage}\n回答："
        )
        return _chat(self._client, prompt)

    def _judge_support(self, answer: str, passage: str) -> SupportLabel:
        prompt = (
            "判断回答是否被段落事实支持。\n"
            "只输出一个词：Fully / Partial / No。\n"
            f"段落：{passage}\n回答：{answer}"
        )
        out = _chat(self._client, prompt).lower()
        if out.startswith("full"):
            return "Fully"
        if out.startswith("part"):
            return "Partial"
        return "No"

    def _aggregate(self, query: str, judgements: tuple[PassageJudgement, ...]) -> str:
        supported = [j for j in judgements if j.is_supported in ("Fully", "Partial")]
        if not supported:
            return "知识库中没有足够支持的证据来回答该问题。"
        evidence = "\n".join(
            f"- 证据[{i + 1}]（{j.is_supported}支持）：{j.passage}\n  草稿：{j.draft_answer}"
            for i, j in enumerate(supported)
        )
        prompt = (
            "综合以下经过支持度评估的草稿，给出最终答案。\n"
            "若证据不足请坦诚说明，不要编造。\n"
            f"问题：{query}\n{evidence}\n最终答案："
        )
        return _chat(self._client, prompt)

    def _judge_utility(self, query: str, answer: str) -> int:
        prompt = (
            "对下面的回答打 1-5 分，5 分表示完整且高度有用。\n"
            "只输出一个 1-5 之间的整数。\n"
            f"问题：{query}\n回答：{answer}"
        )
        out = _chat(self._client, prompt)
        for tok in out.split():
            if tok.isdigit():
                score = int(tok)
                if 1 <= score <= 5:
                    return score
        return 3

    def answer(self, query: str, top_k: int = 3) -> SelfRAGResult:
        decision = self._decide_retrieve(query)
        if decision == "No":
            direct = _chat(self._client, query)
            return SelfRAGResult(
                query=query,
                retrieve="No",
                judgements=(),
                final_answer=direct,
                utility=self._judge_utility(query, direct),
            )

        judgements: list[PassageJudgement] = []
        for passage in self._store.search(query, top_k=top_k):
            relevance = self._judge_relevance(query, passage)
            if relevance == "Irrelevant":
                judgements.append(
                    PassageJudgement(passage, relevance, "", "No")
                )
                continue
            draft = self._draft(query, passage)
            support = self._judge_support(draft, passage)
            judgements.append(PassageJudgement(passage, relevance, draft, support))

        final = self._aggregate(query, tuple(judgements))
        return SelfRAGResult(
            query=query,
            retrieve="Yes",
            judgements=tuple(judgements),
            final_answer=final,
            utility=self._judge_utility(query, final),
        )


def _format_trace(result: SelfRAGResult) -> str:
    lines = [
        f"问题：{result.query}",
        f"[Retrieve] = {result.retrieve}",
    ]
    for i, j in enumerate(result.judgements, 1):
        lines.append(
            f"  段落 {i} | IsRel={j.is_relevant} | IsSup={j.is_supported}"
        )
        lines.append(f"    passage: {j.passage}")
        if j.draft_answer:
            lines.append(f"    draft  : {j.draft_answer}")
    lines.append(f"[IsUse] = {result.utility}/5")
    lines.append(f"最终答案：{result.final_answer}")
    return "\n".join(lines)


def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("请设置 OPENAI_API_KEY；可选 OPENAI_BASE_URL 走兼容网关。")
    if not os.environ.get("DASHSCOPE_API_KEY"):
        raise SystemExit("请设置 DASHSCOPE_API_KEY 用于向量化。")

    client = _make_client()
    store = SimpleVectorStore()
    for doc in (
        "北京是中华人民共和国的首都，位于华北平原北部。",
        "上海是中国的经济金融中心，常住人口超过 2400 万。",
        "长城是中国古代修建的军事防御工程，全长超过 2 万公里。",
        "Self-RAG 通过反思 token 动态决定是否检索，并评估检索段落的相关性与支持度。",
    ):
        store.add(doc)

    rag = SelfRAG(client, store)
    query = input("请输入你的问题：").strip() or "Self-RAG 的核心思想是什么？"
    result = rag.answer(query)
    print(_format_trace(result))


if __name__ == "__main__":
    main()
