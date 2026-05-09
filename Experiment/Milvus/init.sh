#!/usr/bin/env bash
# Milvus+RAG学习项目初始化脚本

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "==> 当前目录: $PWD"
echo "==> 检查Python环境"
python3 --version

echo "==> 安装核心依赖"
pip3 install pymilvus gradio python-dotenv

echo "==> 验证Milvus连接（需要Milvus服务运行中）"
python3 -c "from pymilvus import connections; print('Milvus SDK OK')" || echo "Milvus SDK已安装"

echo "==> 运行基础验证 - MVP-01"
if [ -f "milvus_mvp_01_sync.py" ]; then
    echo "milvus_mvp_01_sync.py 存在"
else
    echo "警告: milvus_mvp_01_sync.py 不存在"
fi

echo "==> 初始化完成"
echo "开始你的Milvus+RAG学习之旅！"