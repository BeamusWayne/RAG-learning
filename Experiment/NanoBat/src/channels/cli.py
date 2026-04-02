# -*- coding: utf-8 -*-
"""
NanoBat CLI 通道：在终端与 Qwen 多轮对话。
"""

from __future__ import annotations

import sys

# 确保可导入上层 src
try:
    from src.agent import chat, chat_stream
except ImportError:
    from agent import chat
    chat_stream = None


def run_cli(stream: bool = False):
    """运行 CLI 对话循环。stream 为 True 时流式打印回复。"""
    history: list[dict[str, str]] = []
    print("NanoBat (Qwen) 已就绪。输入内容对话，输入 exit / quit 退出。\n")

    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            break
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("再见。")
            break

        history.append({"role": "user", "content": user_input})

        if stream and chat_stream:
            print("NanoBat: ", end="", flush=True)
            full_reply: list[str] = []
            for token in chat_stream(history):
                print(token, end="", flush=True)
                full_reply.append(token)
            print()
            reply = "".join(full_reply)
        else:
            reply = chat(history)
            print("NanoBat:", reply)

        if reply:
            history.append({"role": "assistant", "content": reply})

        # 简单限制轮数，避免上下文过长（可按需改为持久化）
        if len(history) > 20:
            history = history[-20:]


if __name__ == "__main__":
    run_cli(stream=False)
