"""07-Reranking demo: Dense 召回 → cross-encoder 重排 → LLM-as-reranker。

演示要点：
    - 用 .env 里的 embedder 算 dense 排名
    - 用 sentence-transformers CrossEncoder（默认 bge-reranker-v2-m3，可在 .env RERANKER_MODEL 改）精排
    - 同样候选送给 LLM 做 pointwise 打分作对照
    - 三路在 NDCG-like 指标上的差异

模型 / API 配置全部走仓库根 .env。
运行：
    uv run python Foundations/RAG-Primer/07-Reranking/demo.py
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from _common import chat, cosine, get_chat_config, get_embedder, need, section  # noqa: E402


QUERY = "如何申请退款？需要哪些步骤？"

CANDIDATES = [
    "用户在订单页选择'申请退款'，上传凭证，财务在 3 个工作日内审核并原路退回。",
    "退款需要提供订单号、退款原因、银行卡或微信账号等信息。",
    "本平台的退款政策遵循《消费者权益保护法》。",
    "猫的体温在 38~39 摄氏度，比人类略高。",
    "RAG 系统中的 chunk_size 通常设为 200~500 个 token。",
    "BM25 是稀疏检索的代表算法，依赖词频与逆文档频率。",
    "公司 2023 年度净利润为 12.4 亿元。",
    "退款审核通过后，款项会在 1~5 个工作日内到账。",
]

GOLDEN_ORDER = [0, 7, 1, 2]


def ndcg(predicted: list[int], golden: list[int]) -> float:
    """简版 NDCG：金标内 id 的 rel = (len-rank)，金标外 = 0。"""
    rel = {gid: len(golden) - i for i, gid in enumerate(golden)}
    dcg = sum(rel.get(d, 0) / math.log2(i + 2) for i, d in enumerate(predicted))
    ideal = sorted(rel.values(), reverse=True)
    idcg = sum(r / math.log2(i + 2) for i, r in enumerate(ideal))
    return dcg / idcg if idcg else 0.0


def cross_encoder_rerank(query: str, docs: list[str]) -> list[float]:
    try:
        from sentence_transformers import CrossEncoder
    except ImportError:
        return []
    model_name = (os.getenv("RERANKER_MODEL") or "").strip() or "BAAI/bge-reranker-v2-m3"
    try:
        ce = CrossEncoder(model_name)
    except Exception as exc:
        print(f"  CrossEncoder 加载失败 ({model_name}): {exc}")
        return []
    return ce.predict([(query, d) for d in docs]).tolist()


def llm_pointwise_rerank(query: str, docs: list[str]) -> list[float]:
    if get_chat_config() is None:
        return []
    scores: list[float] = []
    for d in docs:
        prompt = (
            f"判断下面这段文档对回答给定问题有多相关，仅输出 0~10 的整数。\n"
            f"问题：{query}\n文档：{d}\n相关性分数 (0~10):"
        )
        out = chat(prompt, temperature=0.0)
        try:
            scores.append(float(next(t for t in out.split() if t.lstrip("-").isdigit())))
        except StopIteration:
            scores.append(0.0)
    return scores


def main() -> None:
    embedder = get_embedder()
    need(embedder, "embedder（Ollama 或 sentence-transformers）")
    print(f"embedder = {embedder.backend} / {embedder.model}")
    print(f"query = {QUERY!r}\n候选数 = {len(CANDIDATES)}\n金标排序 = {GOLDEN_ORDER}")

    section("1) Dense 排序")
    sims = cosine(embedder([QUERY]), embedder(CANDIDATES))[0]
    dense_order = np.argsort(-sims).tolist()
    for r, i in enumerate(dense_order[:5], 1):
        print(f"  {r}. id={i}  score={sims[i]:.3f}  {CANDIDATES[i][:36]}")
    print(f"  NDCG = {ndcg(dense_order, GOLDEN_ORDER):.3f}")

    section("2) Cross-Encoder 重排（默认 bge-reranker-v2-m3）")
    ce_scores = cross_encoder_rerank(QUERY, CANDIDATES)
    if not ce_scores:
        print("  cross-encoder 不可用（未装 sentence-transformers 或下载失败），跳过。")
    else:
        ce_order = np.argsort(-np.asarray(ce_scores)).tolist()
        for r, i in enumerate(ce_order[:5], 1):
            print(f"  {r}. id={i}  score={ce_scores[i]:+.2f}  {CANDIDATES[i][:36]}")
        print(f"  NDCG = {ndcg(ce_order, GOLDEN_ORDER):.3f}")

    section("3) LLM-as-Reranker（pointwise 0~10）")
    llm_scores = llm_pointwise_rerank(QUERY, CANDIDATES)
    if not llm_scores:
        print("  chat 未配置（.env），跳过。")
    else:
        llm_order = np.argsort(-np.asarray(llm_scores)).tolist()
        for r, i in enumerate(llm_order[:5], 1):
            print(f"  {r}. id={i}  score={llm_scores[i]:.0f}  {CANDIDATES[i][:36]}")
        print(f"  NDCG = {ndcg(llm_order, GOLDEN_ORDER):.3f}")

    section("性价比建议")
    print("  - 召回 K 太小 (<10) 时，reranker 几乎没用：先扩 K 到 20~50 再 rerank")
    print("  - cross-encoder 比 LLM 便宜一个数量级，效果常差不多 → 优先尝试")
    print("  - LLM-as-Reranker 适合可解释性高 / 召回 ≤ 5 的少量精排场景")


if __name__ == "__main__":
    main()
