# -*- coding: utf-8 -*-
"""
Baseline RAG — 标准检索增强生成
流程: query → vector search → prompt → LLM → answer
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.llm import get_llm, get_str_chain
from core.vector_store import similarity_search
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的问答助手。请严格依据下方参考资料回答问题，若资料不足请明确说明。\n\n参考资料：\n{context}"),
    ("human", "{question}"),
])


def run(question: str, **_) -> dict:
    docs = similarity_search(question)
    context = "\n\n".join(d.page_content for d in docs) or "（无相关资料）"
    chain = _PROMPT | get_str_chain()
    answer = chain.invoke({"context": context, "question": question})
    return {
        "strategy": "baseline",
        "answer": answer,
        "sources": [d.metadata for d in docs],
        "context_used": context,
        "steps": ["向量检索", "Prompt 构建", "LLM 生成"],
    }
