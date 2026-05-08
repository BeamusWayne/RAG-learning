#!/usr/bin/env bash
# MultiLevelRAG — 环境初始化与 smoke test
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== MultiLevelRAG init ==="

# 检查 .env
if [ ! -f .env ]; then
    echo "[WARN] .env 不存在，复制 .env.example → .env"
    cp .env.example .env
fi

# 检查依赖
echo "[1/4] 检查 Python 包..."
uv run python3 -c "import streamlit, langchain, chromadb, networkx, dotenv" 2>/dev/null \
    || { echo "[WARN] 缺少依赖，运行 uv sync..."; cd "$REPO_ROOT" && uv sync -q; }

# 检查 data 目录
echo "[2/4] 检查知识库..."
if [ -d data ] && [ "$(ls -A data 2>/dev/null)" ]; then
    echo "  data/ 目录已有文件"
else
    echo "  [WARN] data/ 目录为空"
fi

# 检查 Chroma 索引
echo "[3/4] 检查向量库..."
if [ -d .chroma_db ]; then
    echo "  .chroma_db/ 已存在"
else
    echo "  .chroma_db/ 不存在（首次运行会自动创建）"
fi

# Smoke test: import 检查
echo "[4/4] Import smoke test..."
uv run python3 -c "
import sys; sys.path.insert(0, '.')
import config
from core.llm import get_llm, get_str_chain
from core.embeddings import get_embeddings
from core.vector_store import similarity_search, collection_count
from knowledge_loader import load_directory
from strategies.baseline_rag import run as baseline_run
from router import route, dispatch, STRATEGY_META
print('  所有模块导入成功')
print(f'  向量库文档数: {collection_count()}')
print(f'  LLM: {config.LLM_PROVIDER}/{config.LLM_MODEL}')
print(f'  Embed: {config.EMBED_PROVIDER}/{config.EMBED_MODEL}')
" && echo "=== init 完成 ===" || echo "=== init 失败，请检查错误 ==="
