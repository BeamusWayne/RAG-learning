# -*- coding: utf-8 -*-
"""
NanoBat Agent：基于通义千问（Qwen）的对话 Agent。
支持多轮对话、可选技能调用；国内直连 DashScope，亦可走 OpenAI 兼容端点（如 Ollama）。
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

# 通义默认 OpenAI 兼容 endpoint
DEFAULT_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen-max"


def _get_client():
    """获取 OpenAI 兼容客户端（通义或其它兼容端点）。"""
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    base = os.getenv("OPENAI_API_BASE") or DEFAULT_BASE
    if not api_key:
        raise RuntimeError("请设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY")
    from openai import OpenAI
    return OpenAI(api_key=api_key, base_url=base)


def _get_model() -> str:
    return os.getenv("NANOBAT_MODEL", DEFAULT_MODEL)


SYSTEM_PROMPT = """你是 NanoBat，一个轻量、友好的 AI 助手。你由通义千问驱动，擅长中文对话与任务协助。回答简洁、有条理，必要时分点说明。若用户需要执行本地操作（如查天气、读文件），可说明需要配合的技能或插件。"""


def chat(messages: list[dict[str, str]], model: str | None = None) -> str:
    """
    与 Qwen 进行一轮对话。
    messages: [{"role": "user"|"assistant"|"system", "content": "..."}, ...]
    返回助手回复文本。
    """
    client = _get_client()
    model = model or _get_model()
    full = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m.get("role") and m.get("content")
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=full,
        temperature=0.7,
        max_tokens=2048,
    )
    choice = resp.choices[0] if resp.choices else None
    if not choice or not choice.message:
        return ""
    return (choice.message.content or "").strip()


def chat_stream(messages: list[dict[str, str]], model: str | None = None):
    """流式对话：yield 每个 token 或片段。"""
    client = _get_client()
    model = model or _get_model()
    full = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m.get("role") and m.get("content")
    ]
    stream = client.chat.completions.create(
        model=model,
        messages=full,
        temperature=0.7,
        max_tokens=2048,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
