"""09-Pitfalls demo: 复现并修复 3 个最常见的翻车场景。

#2  chunk 过大 → 内聚度差，召回不到点
#4  embedding 未归一化 → 长向量永远赢
#6  中文 BM25 未分词 → 命中率近零

模型 / API 配置走仓库根 .env。
运行：
    uv run python Foundations/RAG-Primer/09-Pitfalls/demo.py
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


LONG_DOC = (
    "Python 是一种动态类型的高级编程语言。"
    "它强调代码的可读性，使用缩进表示代码块。"
    "Python 的标准库非常丰富，覆盖网络、并发、文件等常见任务。"
    "RAG 是一种把检索结果当作上下文喂给 LLM 的范式。"
    "RAG 系统的 chunk_size 通常设置在 200~500 token。"
    "公司 2023 年度净利润为 12.4 亿元，同比增长 18.7%。"
    "本文不讨论 OCR 与扫描件处理，那是 01-Loading 模块的话题。"
)

QUERY = "公司 2023 净利润是多少"


def split_fixed(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size) if text[i : i + size]]


def topk_idx(scores: np.ndarray, k: int) -> list[int]:
    return np.argsort(-scores)[:k].tolist()


def demo_chunk_too_large(embedder) -> None:
    section("Pitfall #2 · chunk 太大 → 关键信息被稀释")
    big = split_fixed(LONG_DOC, size=400)
    small = split_fixed(LONG_DOC, size=80)
    qv = embedder([QUERY])
    big_top = topk_idx(cosine(qv, embedder(big))[0], 1)[0]
    small_top = topk_idx(cosine(qv, embedder(small))[0], 1)[0]
    print(f"  size=400  N={len(big):>2}  top1 长度={len(big[big_top]):>3}")
    print(f"           top1 片段：{big[big_top][:60]}")
    print(f"  size=80   N={len(small):>2}  top1 长度={len(small[small_top]):>3}")
    print(f"           top1 片段：{small[small_top][:60]}")
    print("  → 大 chunk 把关键句和无关句打包，相似度被稀释；小 chunk 命中更精准。")


def demo_no_normalization(embedder) -> None:
    section("Pitfall #4 · embedding 未归一化")
    docs = [
        "公司 2023 年度净利润为 12.4 亿元",
        "猫的体温在 38~39 摄氏度，比人类略高。这段比上一段长得多，长得多，长得多……" * 3,
    ]
    raw = embedder(docs, normalize=False)
    qv_raw = embedder([QUERY], normalize=False)
    qv_norm = embedder([QUERY], normalize=True)
    norm = embedder(docs, normalize=True)

    raw_scores = (qv_raw @ raw.T)[0]
    norm_scores = (qv_norm @ norm.T)[0]
    print(f"  raw 范数: {np.linalg.norm(raw, axis=1).round(3).tolist()}")
    print(f"  未归一化（内积）: doc0={raw_scores[0]:>8.3f}  doc1={raw_scores[1]:>8.3f}  ← 噪声 doc 因为更长可能赢")
    print(f"  归一化（cosine）: doc0={norm_scores[0]:>8.3f}  doc1={norm_scores[1]:>8.3f}  ← 排名才合理")
    print("  → 入库前一律 L2 归一化，再用 cosine（= 点积）。")


def demo_chinese_bm25_no_tokenizer() -> None:
    section("Pitfall #6 · 中文 BM25 没分词")
    docs = [
        "公司 2023 年度净利润为 12.4 亿元",
        "今年的研发投入占营收的 9.3%",
        "退款审核通过后款项 1~5 个工作日到账",
    ]

    def bm25_score(corpus: list[list[str]], query: list[str]) -> np.ndarray:
        N = len(corpus)
        df: Counter = Counter()
        for d in corpus:
            for w in set(d):
                df[w] += 1
        idf = {w: math.log(1 + (N - n + 0.5) / (n + 0.5)) for w, n in df.items()}
        avgdl = sum(len(d) for d in corpus) / max(1, N)
        scores = np.zeros(N, dtype=np.float32)
        k1, b = 1.5, 0.75
        for i, d in enumerate(corpus):
            tf = Counter(d)
            for w in query:
                if w not in idf:
                    continue
                f = tf.get(w, 0)
                if f == 0:
                    continue
                denom = f + k1 * (1 - b + b * len(d) / avgdl)
                scores[i] += idf[w] * f * (k1 + 1) / denom
        return scores

    bad = [d.split() for d in docs]
    bad_q = QUERY.split()
    bad_scores = bm25_score(bad, bad_q)
    print(f"  按空格切（错的）：query tokens={bad_q}  scores={bad_scores.round(3).tolist()}")

    try:
        import jieba

        good = [jieba.lcut(d) for d in docs]
        good_q = jieba.lcut(QUERY)
        good_scores = bm25_score(good, good_q)
        print(f"  jieba 分词（对的）：query tokens={good_q}  scores={good_scores.round(3).tolist()}")
        print("  → 中文必须先分词；不然 BM25 几乎不会命中任何东西。")
    except ImportError:
        print("  未装 jieba，无法演示修复版本。pip install jieba 后再来。")


def main() -> None:
    embedder = get_embedder()
    need(embedder, "embedder（Ollama 或 sentence-transformers）")
    print(f"embedder = {embedder.backend} / {embedder.model}")
    demo_chunk_too_large(embedder)
    demo_no_normalization(embedder)
    demo_chinese_bm25_no_tokenizer()

    section("速查口诀")
    print("  改 prompt 之前先排除：加载坏？切分糟？没归一化？BM25 没分词？K 太小？")
    print("  完整 Top-10 见 ./README.md")


if __name__ == "__main__":
    main()
