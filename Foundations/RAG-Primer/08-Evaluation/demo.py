"""08-Evaluation demo: 检索层 (Recall@K / MRR / NDCG@K) + 生成层 (LLM faithfulness)。

演示要点：
    - 用一个迷你评估集，给 (query, golden_chunk_id, golden_answer)
    - 模拟两套召回：baseline、+reranker
    - 算 Recall@5 / MRR / NDCG@5 并打印对照
    - 用 LLM 做 pointwise faithfulness 检查（chat 未配则跳过）

模型 / API 配置全部走仓库根 .env。
运行：
    uv run python Foundations/RAG-Primer/08-Evaluation/demo.py
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from _common import chat, get_chat_config, section  # noqa: E402


@dataclass(frozen=True)
class EvalCase:
    query: str
    golden_chunk_id: int
    golden_answer: str
    chunks: tuple[str, ...]


CHUNKS = (
    "公司 2023 年度净利润为 12.4 亿元，同比增长 18.7%。",     # 0
    "公司 2022 年净利润 10.4 亿元，财报披露详见年报附注 7。",  # 1
    "今年的研发投入占营收的 9.3%，主要花在大模型上。",         # 2
    "RAG 系统的 chunk_size 通常设为 200~500 token。",         # 3
    "退款审核通过后，款项会在 1~5 个工作日内到账。",           # 4
)

EVAL_SET: tuple[EvalCase, ...] = (
    EvalCase("公司去年净利润多少？", 0, "12.4 亿元", CHUNKS),
    EvalCase("研发投入占比是多少？", 2, "9.3%", CHUNKS),
    EvalCase("退款多久能到账？", 4, "1~5 个工作日", CHUNKS),
)

# 手工构造两套排名以演示指标（不依赖外部模型）
BASELINE_RANKINGS = [
    [3, 1, 0, 2, 4],
    [3, 0, 1, 2, 4],
    [4, 1, 0, 3, 2],
]
PLUS_RERANKER_RANKINGS = [
    [0, 1, 3, 2, 4],
    [2, 0, 3, 1, 4],
    [4, 0, 1, 2, 3],
]


def recall_at_k(rankings: list[list[int]], golden: list[int], k: int) -> float:
    return sum(1 for r, g in zip(rankings, golden) if g in r[:k]) / len(golden)


def mrr(rankings: list[list[int]], golden: list[int]) -> float:
    s = 0.0
    for r, g in zip(rankings, golden):
        if g in r:
            s += 1.0 / (r.index(g) + 1)
    return s / len(golden)


def ndcg_at_k(rankings: list[list[int]], golden: list[int], k: int) -> float:
    """单金标版本：rel=1 if id==golden else 0；IDCG = 1。"""
    s = 0.0
    for r, g in zip(rankings, golden):
        if g in r[:k]:
            s += 1.0 / math.log2(r.index(g) + 2)
    return s / len(golden)


def report(label: str, rankings: list[list[int]], golden: list[int]) -> None:
    print(
        f"  {label:<14}  Recall@5 = {recall_at_k(rankings, golden, 5):.2f}  "
        f"MRR = {mrr(rankings, golden):.3f}  NDCG@5 = {ndcg_at_k(rankings, golden, 5):.3f}"
    )


def faithfulness(question: str, answer: str, context: str) -> float | None:
    if get_chat_config() is None:
        return None
    prompt = (
        "判断给定答案是否完全由给定上下文支持（无外加事实、无幻觉）。"
        "仅输出 0~10 的整数（10=完全支持，0=完全无关或幻觉）。\n"
        f"问题：{question}\n上下文：{context}\n答案：{answer}\n忠实度 (0~10):"
    )
    out = chat(prompt, temperature=0.0)
    try:
        return float(next(t for t in out.split() if t.lstrip("-").isdigit())) / 10
    except StopIteration:
        return None


def main() -> None:
    section("检索层指标对照（baseline vs +reranker）")
    golden = [c.golden_chunk_id for c in EVAL_SET]
    report("baseline", BASELINE_RANKINGS, golden)
    report("+reranker", PLUS_RERANKER_RANKINGS, golden)
    print("  → 上 reranker 后三项指标全面提升，符合预期。")

    section("生成层 · LLM Faithfulness (RAGAS 思路简版)")
    if get_chat_config() is None:
        print("  chat 未配置（.env），跳过本节。")
    else:
        samples = [
            ("公司去年净利润多少？", "公司 2023 年净利润 12.4 亿元，增长 18.7%。", CHUNKS[0]),
            ("公司去年净利润多少？", "公司 2023 年净利润 50 亿元，是行业第一。", CHUNKS[0]),
        ]
        for q, a, ctx in samples:
            score = faithfulness(q, a, ctx)
            tag = "忠实" if (score or 0) >= 0.7 else "可疑"
            print(f"  [{tag}] score={score}  answer={a}")

    section("评估闭环建议")
    print("  - 固定 test 集，调优只在 dev 上跑；不固定 = 在过拟合")
    print("  - 检索 vs 生成指标分开看：Faithfulness 低 → prompt；Context Recall 低 → 检索")
    print("  - 任何'优化'必须能在指标上量化提升，否则只是直觉")


if __name__ == "__main__":
    main()
