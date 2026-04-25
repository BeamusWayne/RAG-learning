# -*- coding: utf-8 -*-
"""
RAG Fusion — 查询扩展 + RRF 融合排名
流程: query → LLM 生成 N 个子查询 → 多路检索 → RRF 融合 → LLM 生成答案
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg
from core.llm import get_llm, get_str_chain
from core.vector_store import similarity_search
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

_EXPAND_PROMPT = ChatPromptTemplate.from_messages([
    ("system", f"请将用户问题扩展为 {cfg.FUSION_NUM_QUERIES} 个不同角度的子查询，每行一个，不要编号。"),
    ("human", "{question}"),
])

_ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是专业问答助手。请依据参考资料回答问题。\n\n参考资料：\n{context}"),
    ("human", "{question}"),
])


def _rrf(ranked_lists: list[list], k: int = cfg.RRF_K) -> list:
    scores: dict = {}
    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked):
            key = doc.page_content[:100]
            scores[key] = scores.get(key, 0) + 1.0 / (k + rank + 1)
    # collect unique docs sorted by score
    seen, result = set(), []
    for ranked in ranked_lists:
        for doc in ranked:
            key = doc.page_content[:100]
            if key not in seen:
                seen.add(key)
                result.append((doc, scores[key]))
    result.sort(key=lambda x: x[1], reverse=True)
    return [d for d, _ in result]


def run(question: str, **_) -> dict:
    llm = get_llm()
    parser = StrOutputParser()

    # Step 1: 查询扩展
    expanded_raw = (_EXPAND_PROMPT | get_str_chain()).invoke({"question": question})
    sub_queries = [q.strip() for q in expanded_raw.strip().splitlines() if q.strip()]
    all_queries = [question] + sub_queries[:cfg.FUSION_NUM_QUERIES]

    # Step 2: 多路检索
    ranked_lists = [similarity_search(q) for q in all_queries]

    # Step 3: RRF 融合
    fused_docs = _rrf(ranked_lists)[:cfg.RETRIEVE_TOP_K]
    context = "\n\n".join(d.page_content for d in fused_docs) or "（无相关资料）"

    # Step 4: 生成答案
    answer = (_ANSWER_PROMPT | get_str_chain()).invoke({"context": context, "question": question})

    return {
        "strategy": "fusion",
        "answer": answer,
        "sources": [d.metadata for d in fused_docs],
        "context_used": context,
        "sub_queries": sub_queries,
        "steps": ["查询扩展", f"{len(all_queries)} 路向量检索", "RRF 融合排名", "LLM 生成答案"],
    }
