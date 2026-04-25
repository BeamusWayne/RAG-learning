# -*- coding: utf-8 -*-
"""
Embedding 工厂 — 统一返回 LangChain Embeddings 实例
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg


def get_embeddings():
    provider = cfg.EMBED_PROVIDER.lower()

    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(model=cfg.OLLAMA_EMBED)

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        kwargs = {"model": cfg.EMBED_MODEL, "api_key": cfg.OPENAI_API_KEY}
        if cfg.OPENAI_BASE_URL:
            kwargs["base_url"] = cfg.OPENAI_BASE_URL
        return OpenAIEmbeddings(**kwargs)

    # dashscope (default)
    from langchain_community.embeddings import DashScopeEmbeddings
    return DashScopeEmbeddings(
        model=cfg.EMBED_MODEL,
        dashscope_api_key=cfg.DASHSCOPE_API_KEY or None,
    )
