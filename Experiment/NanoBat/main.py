# -*- coding: utf-8 -*-
"""
NanoBat 入口：启动 CLI 与 Qwen 对话。
"""

import os
import sys

# 将项目根加入 path，便于 import src
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.agent import chat
from src.channels.cli import run_cli


def main():
    run_cli(stream=False)


if __name__ == "__main__":
    main()
