"""03-Chunking-Eval demo: 三大切分质量指标的最小计算。

指标：
    boundary_leak_rate  金标短语跨 chunk 边界的比例（越低越好）
    cohesion_mean/var   chunk 内邻句余弦的均值 / 方差（均值高、方差低 = 内聚好）
    recall_at_k         合成 QA 上'应命中 chunk'是否进入 top-K

模型 / API 配置全部走仓库根 .env。
运行：
    uv run python Foundations/RAG-Primer/03-Chunking-Eval/demo.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from _common import cosine, get_embedder, load_sample_text, need, section  # noqa: E402


@dataclass(frozen=True)
class EvalResult:
    strategy: str
    n_chunks: int
    boundary_leak_rate: float
    cohesion_mean: float
    cohesion_var: float
    recall_at_5: float


def split_fixed(text: str, size: int, overlap: int = 0) -> list[str]:
    step = max(1, size - overlap)
    out: list[str] = []
    for i in range(0, len(text), step):
        piece = text[i : i + size]
        if piece:
            out.append(piece)
        if i + size >= len(text):
            break
    return out


def boundary_leak_rate(chunks: list[str], golden_phrases: list[str]) -> float:
    """金标短语只要不完整出现在任一 chunk 内，就计为'被边界劈开'。"""
    if not golden_phrases:
        return 0.0
    leaked = sum(1 for ph in golden_phrases if not any(ph in c for c in chunks))
    return leaked / len(golden_phrases)


def cohesion(chunks: list[str], embedder) -> tuple[float, float]:
    """chunk 内邻句余弦。句子数<2 的 chunk 视为完美内聚 (1.0)。"""
    means: list[float] = []
    for c in chunks:
        sents = [s.strip() for s in c.replace("！", "。").replace("？", "。").split("。") if s.strip()]
        if len(sents) < 2:
            means.append(1.0)
            continue
        v = embedder(sents)
        sims = (v[:-1] * v[1:]).sum(axis=1)
        means.append(float(np.mean(sims)))
    if not means:
        return 0.0, 0.0
    return float(np.mean(means)), float(np.var(means))


def recall_at_k(chunks: list[str], qa: list[tuple[str, str]], embedder, k: int = 5) -> float:
    """qa = [(question, golden_substring), ...]"""
    if not qa:
        return 0.0
    chunk_vecs = embedder(chunks)
    q_vecs = embedder([q for q, _ in qa])
    sims = cosine(q_vecs, chunk_vecs)
    hits = 0
    for i, (_, golden) in enumerate(qa):
        topk = np.argsort(-sims[i])[:k]
        if any(golden in chunks[j] for j in topk):
            hits += 1
    return hits / len(qa)


GOLDEN_PHRASES = ["上传到知识库", "分段规则", "操作步骤"]

QA = [
    ("怎么修改已上传文件的分段规则？", "分段规则"),
    ("操作之前需要什么权限？", "编辑权限"),
    ("如何进入知识库的文件管理页面？", "文件管理"),
]


def evaluate(strategy: str, chunks: list[str], embedder) -> EvalResult:
    return EvalResult(
        strategy=strategy,
        n_chunks=len(chunks),
        boundary_leak_rate=boundary_leak_rate(chunks, GOLDEN_PHRASES),
        cohesion_mean=cohesion(chunks, embedder)[0],
        cohesion_var=cohesion(chunks, embedder)[1],
        recall_at_5=recall_at_k(chunks, QA, embedder, k=5),
    )


def main() -> None:
    embedder = get_embedder()
    need(embedder, "embedder（Ollama 或 sentence-transformers）")

    text = load_sample_text()
    print(f"原文长度：{len(text)}  embedder={embedder.backend}/{embedder.model}")

    candidates = {
        "fixed-150-overlap-0":  split_fixed(text, 150, 0),
        "fixed-300-overlap-30": split_fixed(text, 300, 30),
        "fixed-800-overlap-80": split_fixed(text, 800, 80),
    }

    section("三种切分横评")
    print(f"  {'strategy':<22}  {'N':>4}  {'leak':>5}  {'coh_mean':>9}  {'coh_var':>8}  {'R@5':>5}")
    for name, chunks in candidates.items():
        r = evaluate(name, chunks, embedder)
        print(
            f"  {name:<22}  {r.n_chunks:>4}  {r.boundary_leak_rate:>5.2f}  "
            f"{r.cohesion_mean:>9.3f}  {r.cohesion_var:>8.4f}  {r.recall_at_5:>5.2f}"
        )

    section("怎么读这张表")
    print("  - leak  ↓：越低 → 金标短语越少被切到边界")
    print("  - coh_mean ↑ / coh_var ↓：每个 chunk 内部话题越集中")
    print("  - R@5 ↑：合成 QA 上的应命中 chunk 进 top-5 的比例")
    print("  三个指标常常互相妥协，靠它们做出帕累托最优的策略选择。")


if __name__ == "__main__":
    main()
