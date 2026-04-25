# -*- coding: utf-8 -*-
"""
知识库加载器 — 支持 .txt / .pdf / .md 文件，带去重
"""
import os, hashlib
import config as cfg
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader
from core.vector_store import add_documents, collection_count


def _hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def load_file(path: str) -> list[Document]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(path)
    elif ext in (".md", ".markdown"):
        loader = UnstructuredMarkdownLoader(path)
    else:
        loader = TextLoader(path, encoding="utf-8")
    docs = loader.load()
    for doc in docs:
        doc.metadata.setdefault("source", os.path.basename(path))
    return docs


def load_directory(directory: str = cfg.DATA_DIR) -> int:
    """加载目录下所有支持文件，返回新增 chunk 数"""
    if not os.path.isdir(directory):
        return 0
    total = 0
    for fname in os.listdir(directory):
        fpath = os.path.join(directory, fname)
        if os.path.isfile(fpath) and fname.lower().endswith((".txt", ".pdf", ".md")):
            try:
                docs = load_file(fpath)
                total += add_documents(docs)
            except Exception as e:
                print(f"[loader] 跳过 {fname}: {e}")
    return total


def load_text(text: str, source: str = "manual_input") -> int:
    doc = Document(page_content=text, metadata={"source": source})
    return add_documents([doc])
