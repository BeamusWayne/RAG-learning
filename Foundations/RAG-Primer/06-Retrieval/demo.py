"""06-Retrieval demo: Dense / BM25 / Hybrid (RRF) / MMR / Small-to-Big。

演示要点：
    - Dense（embedder）vs BM25（jieba 中文分词）在两类 query 上的差异
    - RRF 融合：不需要分数归一化，常胜过单路
    - MMR 多样性参数 λ
    - Small-to-Big 思想

模型 / API 配置全部走仓库根 .env。
运行：
    uv run python Foundations/RAG-Primer/06-Retrieval/demo.py
"""
from __future__ import annotations

import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from _common import cosine, get_embedder, need, section  # noqa: E402


DOCS = [
    "公司 2023 年度净利润为 12.4 亿元，同比增长 18.7%。",
    "公司 2022 年净利润 10.4 亿元，财报披露详见年报附注 7。",
    "去年我们赚到的钱大概是十二亿出头，主要靠云业务驱动。",
    "今年的研发投入占营收的 9.3%，主要花在大模型上。",
    "大模型团队规模从 30 人扩张到 80 人，集中在算法与基础设施。",
    "RAG 系统中的 chunk_size 通常设为 200~500 个 token。",
    "猫的体温在 38~39 摄氏度，比人类略高。",
    "BM25 是稀疏检索的代表算法，依赖词频与逆文档频率。",
]


def tokenize_zh(text: str) -> list[str]:
    try:
        import jieba

        return [t for t in jieba.lcut(text) if t.strip()]
    except ImportError:
        return list(text)


class BM25:
    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.corpus = corpus
        self.k1, self.b = k1, b
        self.N = len(corpus)
        self.doc_len = [len(d) for d in corpus]
        self.avgdl = sum(self.doc_len) / max(1, self.N)
        df: Counter = Counter()
        for d in corpus:
            for w in set(d):
                df[w] += 1
        self.idf = {w: math.log(1 + (self.N - n + 0.5) / (n + 0.5)) for w, n in df.items()}
        self.tf = [Counter(d) for d in corpus]

    def score(self, query: list[str]) -> np.ndarray:
        scores = np.zeros(self.N, dtype=np.float32)
        for i in range(self.N):
            for w in query:
                if w not in self.idf:
                    continue
                f = self.tf[i].get(w, 0)
                if f == 0:
                    continue
                denom = f + self.k1 * (1 - self.b + self.b * self.doc_len[i] / self.avgdl)
                scores[i] += self.idf[w] * f * (self.k1 + 1) / denom
        return scores


def topk(scores: np.ndarray, k: int) -> list[int]:
    return np.argsort(-scores)[:k].tolist()


def rrf_fuse(rankings: list[list[int]], k: int = 5, c: int = 60) -> list[int]:
    score: dict[int, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking):
            score[doc_id] = score.get(doc_id, 0.0) + 1.0 / (c + rank + 1)
    return sorted(score, key=lambda d: -score[d])[:k]


def mmr(query_vec: np.ndarray, doc_vecs: np.ndarray, k: int, lam: float = 0.7) -> list[int]:
    sim_q = (query_vec @ doc_vecs.T)[0]
    sim_dd = doc_vecs @ doc_vecs.T
    selected: list[int] = []
    candidates = list(range(len(doc_vecs)))
    while len(selected) < k and candidates:
        best, best_score = candidates[0], -1e9
        for c in candidates:
            relevance = sim_q[c]
            diversity = max((sim_dd[c, s] for s in selected), default=0.0)
            score = lam * relevance - (1 - lam) * diversity
            if score > best_score:
                best, best_score = c, score
        selected.append(best)
        candidates.remove(best)
    return selected


def main() -> None:
    embedder = get_embedder()
    need(embedder, "embedder（Ollama 或 sentence-transformers）")
    print(f"embedder = {embedder.backend} / {embedder.model}\n语料：{len(DOCS)} 条")

    doc_vecs = embedder(DOCS)
    bm25 = BM25([tokenize_zh(d) for d in DOCS])

    queries = [
        ("query 1（同义改写）", "去年公司赚了多少钱"),
        ("query 2（精确术语 / 数字）", "2023 年度净利润"),
    ]

    for label, q in queries:
        section(f"{label}：{q}")
        q_vec = embedder([q])
        dense_top = topk(cosine(q_vec, doc_vecs)[0], 5)
        sparse_top = topk(bm25.score(tokenize_zh(q)), 5)
        hybrid_top = rrf_fuse([dense_top, sparse_top], k=5)

        for tag, ranking in (("Dense", dense_top), ("BM25", sparse_top), ("Hybrid-RRF", hybrid_top)):
            print(f"  {tag:<11} → {ranking}")
            for rank, idx in enumerate(ranking[:3], 1):
                print(f"     {rank}. doc[{idx}] {DOCS[idx][:38]}")

    section("MMR 多样性 (query='公司业绩')")
    q_vec = embedder(["公司业绩"])
    for lam in (1.0, 0.7, 0.3):
        idx = mmr(q_vec, doc_vecs, k=4, lam=lam)
        print(f"  λ={lam}  → {idx}")
    print("  λ=1 纯相关，λ↓ 多样性增加；典型设 0.5~0.7。")

    section("Small-to-Big 思想")
    print("  索引层用'句子级 ~100 token'匹配；命中后返回它周围更大的窗口（~800 token）给 LLM。")
    print("  → 解决'chunk 小召回准但答案不全'的核心矛盾。生产用 LangChain ParentDocumentRetriever 等实现。")


if __name__ == "__main__":
    main()
