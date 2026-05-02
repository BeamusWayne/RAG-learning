"""05-VectorStore demo: FAISS Flat / IVF / HNSW 在同一份合成向量上的精度-延迟对比。

演示要点：
    - 用 5000 条随机向量模拟向量库（不需要真实 embedder）
    - Flat 当 ground truth；IVF / HNSW 与之对比 Recall@10 与 QPS
    - 调 IVF.nprobe / HNSW.efSearch，可视化"召回-速度"曲线

模型 / API 配置走仓库根 .env（本 demo 只用本地 numpy + faiss）。
运行：
    uv run python Foundations/RAG-Primer/05-VectorStore/demo.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from _common import section  # noqa: E402

N_DB = 5000
N_QUERY = 200
DIM = 128
TOPK = 10
SEED = 42


def gen_vecs(n: int, dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = rng.standard_normal((n, dim)).astype(np.float32)
    x /= np.linalg.norm(x, axis=1, keepdims=True).clip(1e-12)
    return x


def recall(pred: np.ndarray, truth: np.ndarray) -> float:
    """pred / truth shape: [Q, K]。Recall = |pred ∩ truth| / K，按 query 平均。"""
    hits = 0
    total = pred.shape[0] * pred.shape[1]
    for i in range(pred.shape[0]):
        hits += len(set(pred[i].tolist()) & set(truth[i].tolist()))
    return hits / total


def bench(query_fn, queries: np.ndarray) -> tuple[float, np.ndarray]:
    t0 = time.perf_counter()
    ids = query_fn(queries)
    dt = time.perf_counter() - t0
    qps = len(queries) / dt if dt > 0 else float("inf")
    return qps, ids


def main() -> None:
    try:
        import faiss
    except ImportError:
        print("⚠️  未安装 faiss-cpu，跳过本 demo。")
        return

    print(f"合成数据：N={N_DB} 库向量，Q={N_QUERY} 查询，dim={DIM}")
    db = gen_vecs(N_DB, DIM, SEED)
    qs = gen_vecs(N_QUERY, DIM, SEED + 1)

    section("Flat (ground truth)")
    flat = faiss.IndexFlatIP(DIM)
    flat.add(db)
    qps, gt = bench(lambda q: flat.search(q, TOPK)[1], qs)
    print(f"  Flat   QPS={qps:>8.1f}  Recall@{TOPK}=1.000 (定义)")

    section("IVF (nlist=100，调 nprobe)")
    quantizer = faiss.IndexFlatIP(DIM)
    ivf = faiss.IndexIVFFlat(quantizer, DIM, 100, faiss.METRIC_INNER_PRODUCT)
    ivf.train(db)
    ivf.add(db)
    for nprobe in (1, 4, 16, 64):
        ivf.nprobe = nprobe
        qps, ids = bench(lambda q: ivf.search(q, TOPK)[1], qs)
        r = recall(ids, gt)
        print(f"  IVF    nprobe={nprobe:>3}  QPS={qps:>8.1f}  Recall@{TOPK}={r:.3f}")

    section("HNSW (M=32，调 efSearch)")
    hnsw = faiss.IndexHNSWFlat(DIM, 32, faiss.METRIC_INNER_PRODUCT)
    hnsw.hnsw.efConstruction = 200
    hnsw.add(db)
    for ef in (16, 32, 64, 128):
        hnsw.hnsw.efSearch = ef
        qps, ids = bench(lambda q: hnsw.search(q, TOPK)[1], qs)
        r = recall(ids, gt)
        print(f"  HNSW   efSearch={ef:>4}  QPS={qps:>8.1f}  Recall@{TOPK}={r:.3f}")

    section("怎么读这张表")
    print("  - Flat 慢但 100% 准；IVF 调 nprobe、HNSW 调 efSearch 来换召回与速度")
    print("  - 5K 量级看不出差距；线上 1M+ 才会显现：HNSW 通常默认；IVF+PQ 用于内存敏感场景")
    print("  - 元数据过滤：post-filter 在 K 不够时崩；首选 Qdrant/Milvus 的 in-index 过滤")


if __name__ == "__main__":
    main()
