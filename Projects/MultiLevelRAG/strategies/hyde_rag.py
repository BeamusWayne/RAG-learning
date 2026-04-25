# -*- coding: utf-8 -*-
"""
HyDE RAG — Hypothetical Document Embeddings
流程: query → LLM 生成假设文档 → 用假设文档向量检索 → LLM 生成答案
缩小 query 与 passage 的语义鸿沟
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.llm import get_llm, get_str_chain
from core.vector_store import similarity_search
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

_HYDE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "请根据以下问题，生成一段详细的假设性回答文档（200字左右），即使你不确定答案也要尽力生成一段相关文本。"),
    ("human", "{question}"),
])

_ANSWER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是专业问答助手。请依据参考资料回答问题。\n\n参考资料：\n{context}"),
    ("human", "{question}"),
])


def run(question: str, **_) -> dict:
    llm = get_llm()
    parser = StrOutputParser()

    # Step 1: 生成假设文档
    hypo_doc = (_HYDE_PROMPT | get_str_chain()).invoke({"question": question})

    # Step 2: 用假设文档做向量检索（比原始 query 语义更丰富）
    docs = similarity_search(hypo_doc)
    context = "\n\n".join(d.page_content for d in docs) or "（无相关资料）"

    # Step 3: 用检索结果回答原始问题
    answer = (_ANSWER_PROMPT | get_str_chain()).invoke({"context": context, "question": question})

    return {
        "strategy": "hyde",
        "answer": answer,
        "sources": [d.metadata for d in docs],
        "context_used": context,
        "hypothetical_doc": hypo_doc,
        "steps": ["生成假设文档", "HyDE 向量检索", "LLM 生成答案"],
    }
