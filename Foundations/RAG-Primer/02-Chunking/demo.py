"""02-Chunking demo: 五种切分策略并排对比 + chunk 长度分布。

策略：
    fixed         按字符硬切（基线）
    recursive     RecursiveCharacterTextSplitter（多级分隔符递归）
    markdown      MarkdownHeaderTextSplitter（按标题）
    semantic      句子相似度断点（需要 embedder；缺则跳过该项）
    parent_child  父子双层（小块召回 + 大块送 LLM）

模型 / API 配置全部走仓库根 .env。
运行：
    uv run python Foundations/RAG-Primer/02-Chunking/demo.py
"""
from __future__ import annotations

import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from _common import get_embedder, load_sample_text, section  # noqa: E402


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    chunk_id: int
    parent_id: int | None
    metadata: dict = field(default_factory=dict)


def split_fixed(text: str, size: int = 300, overlap: int = 30) -> list[str]:
    out: list[str] = []
    step = max(1, size - overlap)
    for i in range(0, len(text), step):
        piece = text[i : i + size]
        if piece:
            out.append(piece)
        if i + size >= len(text):
            break
    return out


def split_recursive(text: str, size: int = 300, overlap: int = 30) -> list[str]:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        return split_fixed(text, size, overlap)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""],
    )
    return splitter.split_text(text)


def split_markdown(md_text: str) -> list[tuple[str, dict]]:
    try:
        from langchain_text_splitters import MarkdownHeaderTextSplitter
    except ImportError:
        return [(md_text, {})]
    headers = [("#", "h1"), ("##", "h2"), ("###", "h3")]
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers)
    docs = splitter.split_text(md_text)
    return [(d.page_content, dict(d.metadata)) for d in docs]


def split_semantic(text: str, embedder, threshold: float = 0.55) -> list[str]:
    """按句子嵌入余弦相似度的'谷底'切分。threshold 越低越倾向于切。"""
    sents = [s.strip() for s in text.replace("！", "。").replace("？", "。").split("。") if s.strip()]
    if len(sents) < 3:
        return ["。".join(sents) + "。"]
    vecs = embedder(sents)
    sims = (vecs[:-1] * vecs[1:]).sum(axis=1)  # 邻句余弦
    out: list[str] = []
    buf: list[str] = [sents[0]]
    for i, sim in enumerate(sims, start=1):
        if sim < threshold:
            out.append("。".join(buf) + "。")
            buf = [sents[i]]
        else:
            buf.append(sents[i])
    if buf:
        out.append("。".join(buf) + "。")
    return out


def split_parent_child(text: str) -> list[Chunk]:
    """大块作 parent，每个 parent 内部再切小块作 child。"""
    parents = split_recursive(text, size=600, overlap=40)
    chunks: list[Chunk] = []
    cid = 0
    for pid, p in enumerate(parents):
        chunks.append(
            Chunk(text=p, source="<sample>", chunk_id=cid, parent_id=None, metadata={"role": "parent"})
        )
        cid += 1
        for child in split_recursive(p, size=180, overlap=20):
            chunks.append(
                Chunk(text=child, source="<sample>", chunk_id=cid, parent_id=pid, metadata={"role": "child"})
            )
            cid += 1
    return chunks


def length_stats(pieces: list[str]) -> str:
    if not pieces:
        return "  （空）"
    lens = [len(p) for p in pieces]
    return (
        f"  N={len(lens):3}  min={min(lens):4}  max={max(lens):4}  "
        f"mean={statistics.mean(lens):6.1f}  stdev={statistics.pstdev(lens):6.1f}"
    )


SAMPLE_MD = """# 入门

Python 是动态语言，缩进表示代码块。

## 类型注解

新版 Python 支持 type hints，但运行时不强制。

## 装饰器

装饰器本质是高阶函数。
"""


def main() -> None:
    text = load_sample_text()
    print(f"原文长度：{len(text)} 字")

    section("策略 1 · fixed (size=300, overlap=30)")
    print(length_stats(split_fixed(text)))

    section("策略 2 · recursive (size=300, overlap=30)")
    print(length_stats(split_recursive(text)))

    section("策略 3 · markdown (按 H1/H2/H3)")
    for content, meta in split_markdown(SAMPLE_MD):
        print(f"  meta={meta}  len={len(content)}  片段={content[:25]!r}")

    section("策略 4 · semantic (邻句余弦阈值)")
    embedder = get_embedder()
    if embedder is None:
        print("  embedder 未就绪（参见 .env 中 OLLAMA_/ST_EMBED_*），跳过本策略")
    else:
        sem = split_semantic(text[:1500], embedder, threshold=0.6)
        print(f"  embedder={embedder.backend}/{embedder.model}")
        print(length_stats(sem))

    section("策略 5 · parent-child (大块召回 + 小块匹配)")
    pc = split_parent_child(text)
    parents = [c for c in pc if c.metadata["role"] == "parent"]
    children = [c for c in pc if c.metadata["role"] == "child"]
    print(f"  parents={len(parents)}  children={len(children)}")
    print(f"  parent 长度: {length_stats([c.text for c in parents]).strip()}")
    print(f"  child  长度: {length_stats([c.text for c in children]).strip()}")

    section("超参建议")
    print("  - chunk_size 起步 200~500；chunk_overlap 取 size 的 10~20%")
    print("  - 选定后必须用 03-Chunking-Eval 实测 Recall@K 与边界泄漏率，再决定是否上线")


if __name__ == "__main__":
    main()
