#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$SCRIPT_DIR"

echo "==> 子项目目录: $SCRIPT_DIR"
echo "==> 仓库根目录: $REPO_ROOT"

# 激活仓库级虚拟环境
VENV="$REPO_ROOT/.venv"
if [ -d "$VENV" ]; then
  source "$VENV/bin/activate"
  echo "==> 虚拟环境已激活 (.venv)"
else
  echo "!! 未找到 .venv，请先在仓库根目录运行: uv venv && uv sync"
  exit 1
fi

# 同步依赖（包含 ragas）
echo "==> 同步依赖 (uv sync)"
cd "$REPO_ROOT" && uv sync
cd "$SCRIPT_DIR"

# 验证 ragas 可用
echo "==> 验证 RAGAS 导入"
python << 'PYEOF'
import importlib, sys

checks = [
    ('ragas',     'RAGAS'),
    ('datasets',  'HuggingFace Datasets'),
    ('langchain', 'LangChain'),
]

failed = []
for mod, label in checks:
    try:
        m = importlib.import_module(mod)
        ver = getattr(m, '__version__', 'unknown')
        print(f'  OK  {label} ({ver})')
    except ImportError:
        print(f'  FAIL {label} — 缺少 {mod}')
        failed.append(label)

if failed:
    msg = ", ".join(failed)
    print("")
    print(f"!! {len(failed)} 个模块缺失: {msg}")
    print("   运行: uv add ragas datasets")
    sys.exit(1)
else:
    print("")
    print(f"  全部 {len(checks)} 个依赖就绪")
PYEOF

echo ""
echo "==> 初始化完成"
echo "    运行 demo: python demo_faithfulness.py"
echo "    综合评估: python demo_evaluate.py"
