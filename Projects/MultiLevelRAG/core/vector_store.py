# -*- coding: utf-8 -*-
"""
向量库管理 — Chroma 持久化，支持增量索引与检索
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg
from core.embeddings import get_embeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


_store: Chroma | None = None


def _get_store(collection: str = "multi_rag") -> Chroma:
    global _store
    if _store is None:
        os.makedirs(cfg.CHROMA_DIR, exist_ok=True)
        _store = Chroma(
            collection_name=collection,
            embedding_function=get_embeddings(),
            persist_directory=cfg.CHROMA_DIR,
        )
    return _store


def reset_store():
    global _store
    _store = None


def add_documents(docs: list[Document], collection: str = "multi_rag") -> int:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.CHUNK_SIZE,
        chunk_overlap=cfg.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    store = _get_store(collection)
    store.add_documents(chunks)
    return len(chunks)


def get_retriever(collection: str = "multi_rag", k: int | None = None):
    store = _get_store(collection)
    return store.as_retriever(search_kwargs={"k": k or cfg.RETRIEVE_TOP_K})


def similarity_search(query: str, k: int | None = None, collection: str = "multi_rag") -> list[Document]:
    store = _get_store(collection)
    return store.similarity_search(query, k=k or cfg.RETRIEVE_TOP_K)


def similarity_search_with_score(query: str, k: int | None = None, collection: str = "multi_rag"):
    store = _get_store(collection)
    return store.similarity_search_with_relevance_scores(query, k=k or cfg.RETRIEVE_TOP_K)


def collection_count(collection: str = "multi_rag") -> int:
    try:
        store = _get_store(collection)
        return store._collection.count()
    except Exception:
        return 0
