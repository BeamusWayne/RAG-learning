# -*- coding: utf-8 -*-
"""
MultiLevelRAG - 全局配置 (自动加载 .env)
支持 DashScope(qwen) / OpenAI 兼容(MiniMax etc.) / Ollama
"""
import os
from pathlib import Path

# 自动加载同目录 .env
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path, override=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHROMA_DIR = os.path.join(BASE_DIR, ".chroma_db")
GRAPH_DIR = os.path.join(BASE_DIR, ".graph_store")

# ── LLM ──────────────────────────────────────────────────────────────────────
LLM_PROVIDER = os.environ.get("MULTI_RAG_LLM_PROVIDER", "openai")
LLM_MODEL     = os.environ.get("MULTI_RAG_LLM_MODEL",     "MiniMax-M2.5")
OLLAMA_LLM    = os.environ.get("MULTI_RAG_OLLAMA_LLM",    "qwen3:4b")

# ── Embedding ────────────────────────────────────────────────────────────────
EMBED_PROVIDER = os.environ.get("MULTI_RAG_EMBED_PROVIDER", "openai")
EMBED_MODEL    = os.environ.get("MULTI_RAG_EMBED_MODEL",    "text-embedding-3-small")
OLLAMA_EMBED   = os.environ.get("MULTI_RAG_OLLAMA_EMBED",   "nomic-embed-text")

# ── API Keys ─────────────────────────────────────────────────────────────────
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
OPENAI_API_KEY    = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL   = os.environ.get("OPENAI_BASE_URL", "https://api.minimaxi.chat/v1")

# ── Retrieval ─────────────────────────────────────────────────────────────────
RETRIEVE_TOP_K = 5
CHUNK_SIZE     = 600
CHUNK_OVERLAP  = 60

# ── RAG Fusion ────────────────────────────────────────────────────────────────
FUSION_NUM_QUERIES = 3
RRF_K              = 60

# ── CRAG ──────────────────────────────────────────────────────────────────────
CRAG_THRESHOLD_UPPER = 0.5
CRAG_THRESHOLD_LOWER = -0.9

# ── GraphRAG ──────────────────────────────────────────────────────────────────
GRAPH_MAX_HOPS     = 2
GRAPH_TOP_ENTITIES = 5

# ── Intent Router ─────────────────────────────────────────────────────────────
STRATEGIES       = ["baseline", "hyde", "fusion", "crag", "graph"]
DEFAULT_STRATEGY = "auto"

# ── Web Search ────────────────────────────────────────────────────────────────
ENABLE_WEB_SEARCH = False
