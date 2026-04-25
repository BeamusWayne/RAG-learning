# -*- coding: utf-8 -*-
"""
CRAG — Corrective RAG (纠正式 RAG)
流程: query → 检索 → 相关性评分 → Correct/Incorrect/Ambiguous 分支
  Correct   : 精炼内部知识 → 生成
  Incorrect : 网络搜索（或占位）→ 生成
  Ambiguous : 内部精炼 + 外部搜索合并 → 生成
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg
from core.llm import get_llm, get_str_chain
from core.vector_store import similarity_search_with_score
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

CORRECT = "correct"
INCORRECT = "incorrect"
AMBIGUOUS = "ambiguous"

_EVAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "请判断以下文档片段与问题的相关性，用 -1.0~1.0 之间的浮点数表示（1.0=高度相关，-1.0=完全不相关），只输出数字。"),
    ("human", "问题: {question}\n\n文档: {doc}"),
])

_REFINE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "请从以下文档中提取与问题最相关的关键句子，去掉无关内容，保留精华。\n\n文档：\n{docs}"),
    ("human", "问题: {question}"),
])

_ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是专业问答助手。请依据参考资料回答问题。\n\n参考资料：\n{context}"),
    ("human", "{question}"),
])


def _score(question: str, doc_text: str) -> float:
    try:
        llm = get_llm()
        raw = (_EVAL_PROMPT | get_str_chain()).invoke({"question": question, "doc": doc_text[:500]})
        return float(raw.strip())
    except Exception:
        return 0.0


def _trigger(scores: list[float]) -> str:
    if not scores:
        return INCORRECT
    if any(s > cfg.CRAG_THRESHOLD_UPPER for s in scores):
        return CORRECT
    if all(s < cfg.CRAG_THRESHOLD_LOWER for s in scores):
        return INCORRECT
    return AMBIGUOUS


def run(question: str, **_) -> dict:
    llm = get_llm()
    parser = StrOutputParser()

    # Step 1: 检索 + 评分
    docs_with_scores = similarity_search_with_score(question)
    docs = [d for d, _ in docs_with_scores]
    llm_scores = [_score(question, d.page_content) for d in docs]
    action = _trigger(llm_scores)

    # Step 2: 知识准备
    internal_ctx = external_ctx = ""

    if action in (CORRECT, AMBIGUOUS):
        docs_text = "\n\n".join(f"[{i+1}] {d.page_content}" for i, d in enumerate(docs))
        internal_ctx = (_REFINE_PROMPT | get_str_chain()).invoke({"docs": docs_text, "question": question})

    if action in (INCORRECT, AMBIGUOUS):
        if cfg.ENABLE_WEB_SEARCH:
            external_ctx = f"[网络搜索占位] 关于「{question}」的最新结果..."
        else:
            external_ctx = f"（网络搜索已禁用，问题「{question}」无本地知识库匹配）"

    context_parts = [p for p in [internal_ctx, external_ctx] if p.strip()]
    context = "\n\n---\n\n".join(context_parts) or "（无相关资料）"

    # Step 3: 生成
    answer = (_ANSWER_PROMPT | get_str_chain()).invoke({"context": context, "question": question})

    return {
        "strategy": "crag",
        "answer": answer,
        "sources": [d.metadata for d in docs],
        "context_used": context,
        "action": action,
        "scores": llm_scores,
        "steps": ["向量检索", "相关性评分", f"动作触发({action})", "知识精炼/外部搜索", "LLM 生成答案"],
    }
