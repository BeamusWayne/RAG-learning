#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV=".venv"

echo "==> 当前目录: $PWD"

# 激活虚拟环境
if [ -d "$VENV" ]; then
  source "$VENV/bin/activate"
  echo "==> 虚拟环境已激活 (.venv)"
else
  echo "!! 未找到 .venv，请先运行: uv venv && uv sync"
  exit 1
fi

# 同步依赖
echo "==> 同步依赖 (uv sync)"
uv sync

# 运行基础验证：检查关键模块 import 是否正常
echo "==> 运行基础验证"
python -c "
import importlib, sys

modules = [
    ('langchain',           'LangChain'),
    ('langchain_openai',    'LangChain-OpenAI'),
    ('langchain_chroma',    'LangChain-Chroma'),
    ('fastapi',             'FastAPI'),
    ('pydantic_ai',         'PydanticAI'),
    ('dotenv',              'python-dotenv'),
]

failed = []
for mod, label in modules:
    try:
        importlib.import_module(mod)
        print(f'  OK  {label}')
    except ImportError:
        print(f'  FAIL {label} — 缺少 {mod}')
        failed.append(label)

if failed:
    print(f'\n!! {len(failed)} 个模块导入失败: {", ".join(failed)}')
    sys.exit(1)
else:
    print(f'\n  全部 {len(modules)} 个依赖模块导入正常')
"

echo ""
echo "==> 初始化完成"
echo "    启动 Streamlit 应用: streamlit run Projects/MultiLevelRAG/app.py"
echo "    启动 FastAPI 服务:   cd Experiment/graph-rag-agent && python -m server.main"
echo "    运行 RAG-Primer demo: cd Foundations/RAG-Primer/01-Loading && python demo.py"
