"""RAG-Primer · 各 demo 共用的最小工具集。

设计原则：
    - 模型 / API key / endpoint 一律从仓库根 `.env` 读取，绝不硬编码
    - 任一可选依赖缺失或服务未配置时，给出清晰提示并跳过，不让 demo 崩
    - 默认按"Ollama → sentence-transformers"顺序自动挑 embedder
    - chat 客户端按 OPENAI → MINIMAX → DASHSCOPE 顺序匹配第一个有 key 的组
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable, Sequence

import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "Data"
SAMPLE_TEXT_PATH = DATA_DIR / "测试文本_Python基础语法.txt"

try:
    from dotenv import load_dotenv

    load_dotenv(REPO_ROOT / ".env", override=False)
except ImportError:
    pass


# ---------- chat (OpenAI 兼容) ----------

CHAT_PROVIDERS: tuple[tuple[str, str, str], ...] = (
    ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_CHAT_MODEL"),
    ("MINIMAX_API_KEY", "MINIMAX_BASE_URL", "MINIMAX_CHAT_MODEL"),
    ("DASHSCOPE_API_KEY", "DASHSCOPE_BASE_URL", "DASHSCOPE_CHAT_MODEL"),
)


def get_chat_config() -> tuple[str, str, str] | None:
    """返回 (api_key, base_url, model)，按优先级取第一个有 key 的组。无则 None。"""
    for key_name, url_name, model_name in CHAT_PROVIDERS:
        key = (os.getenv(key_name) or "").strip()
        if key:
            return key, (os.getenv(url_name) or "").strip(), (os.getenv(model_name) or "").strip()
    return None


@lru_cache(maxsize=1)
def get_chat_client():
    """惰性创建 OpenAI 兼容客户端。未配置或未装 openai 时返回 None。"""
    cfg = get_chat_config()
    if cfg is None:
        return None
    api_key, base_url, _ = cfg
    try:
        from openai import OpenAI
    except ImportError:
        return None
    return OpenAI(api_key=api_key, base_url=base_url or None)


def chat(prompt: str, system: str | None = None, temperature: float = 0.0) -> str:
    """单轮对话；未配置 chat 时返回占位串，不抛异常。"""
    client = get_chat_client()
    if client is None:
        return "[chat 未配置：请在 .env 填入 OPENAI_/MINIMAX_/DASHSCOPE_ 任一组]"
    cfg = get_chat_config()
    assert cfg is not None
    _, _, model = cfg
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as exc:
        return f"[chat 调用失败：{exc}]"


# ---------- embedding ----------

@dataclass(frozen=True)
class Embedder:
    """统一 embedder 接口。调用：embedder(["t1", "t2"]) -> np.ndarray[N, D]。"""

    backend: str
    model: str
    encode: Callable[[list[str]], list[list[float]]]
    dim: int | None = None

    def __call__(self, texts: Sequence[str], normalize: bool = True) -> np.ndarray:
        vecs = self.encode(list(texts))
        arr = np.asarray(vecs, dtype=np.float32)
        if normalize:
            norms = np.linalg.norm(arr, axis=1, keepdims=True)
            arr = arr / np.clip(norms, 1e-12, None)
        return arr


def _try_ollama_embedder() -> Embedder | None:
    base_url = (os.getenv("OLLAMA_BASE_URL") or "").strip()
    model = (os.getenv("OLLAMA_EMBED_MODEL") or "").strip()
    if not base_url or not model:
        return None
    try:
        import requests

        ping = requests.get(f"{base_url}/api/tags", timeout=2)
        if not ping.ok:
            return None
    except Exception:
        return None

    def _encode(texts: list[str]) -> list[list[float]]:
        import requests

        out: list[list[float]] = []
        for t in texts:
            r = requests.post(
                f"{base_url}/api/embeddings",
                json={"model": model, "prompt": t},
                timeout=60,
            )
            r.raise_for_status()
            out.append(r.json()["embedding"])
        return out

    return Embedder("ollama", model, _encode)


def _try_st_embedder() -> Embedder | None:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None
    model_name = (os.getenv("ST_EMBED_MODEL") or "").strip() or "BAAI/bge-small-zh-v1.5"
    try:
        st_model = SentenceTransformer(model_name)
    except Exception:
        return None

    def _encode(texts: list[str]) -> list[list[float]]:
        arr = st_model.encode(texts, normalize_embeddings=False, show_progress_bar=False)
        return arr.tolist()

    return Embedder("sentence-transformers", model_name, _encode)


@lru_cache(maxsize=1)
def get_embedder() -> Embedder | None:
    """按 Ollama → sentence-transformers 顺序拿 embedder；都不行返回 None。"""
    return _try_ollama_embedder() or _try_st_embedder()


# ---------- 数据 ----------

def load_sample_text() -> str:
    """读取仓库根 Data/ 下的中文示例文本；缺文件时退化为内置短文。"""
    if SAMPLE_TEXT_PATH.exists():
        return SAMPLE_TEXT_PATH.read_text(encoding="utf-8")
    return (
        "Python 是一种高级编程语言。\n"
        "它强调代码的可读性，使用缩进表示代码块。\n"
        "Python 的类型系统是动态的，但近年来支持类型注解。\n"
    )


# ---------- 通用工具 ----------

def cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """两组向量的余弦相似矩阵；自动归一化。"""
    a = a / np.clip(np.linalg.norm(a, axis=-1, keepdims=True), 1e-12, None)
    b = b / np.clip(np.linalg.norm(b, axis=-1, keepdims=True), 1e-12, None)
    return a @ b.T


def section(title: str) -> None:
    bar = "─" * max(4, 60 - len(title))
    print(f"\n── {title} {bar}")


def need(value, label: str) -> None:
    """缺依赖时友好退出，不打 traceback。"""
    if value is None:
        print(f"\n⚠️  {label} 未就绪，跳过本 demo。提示：检查 .env 或安装相关依赖。\n")
        sys.exit(0)
