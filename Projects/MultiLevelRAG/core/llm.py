# -*- coding: utf-8 -*-
"""
LLM 工厂 — 统一返回 LangChain BaseChatModel 实例
支持 dashscope | openai | ollama
自动剥离 <think>...</think> 推理标签（MiniMax-M2.5 等 CoT 模型）
"""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _strip_think(text: str) -> str:
    return _THINK_RE.sub("", text).strip()


def get_llm(provider: str | None = None, model: str | None = None) -> BaseChatModel:
    provider = (provider or cfg.LLM_PROVIDER).lower()
    model = model or cfg.LLM_MODEL

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=cfg.OLLAMA_LLM)

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        kwargs = {"model": model, "api_key": cfg.OPENAI_API_KEY}
        if cfg.OPENAI_BASE_URL:
            kwargs["base_url"] = cfg.OPENAI_BASE_URL
        return ChatOpenAI(**kwargs)

    # dashscope (default)
    from langchain_community.chat_models.tongyi import ChatTongyi
    return ChatTongyi(model=model, dashscope_api_key=cfg.DASHSCOPE_API_KEY or None)


def get_str_chain(provider: str | None = None, model: str | None = None):
    """返回 LLM | StrOutputParser + think-tag 剥离的 Runnable"""
    llm = get_llm(provider, model)
    return llm | StrOutputParser() | RunnableLambda(_strip_think)
