"""08-Evaluation demo: RAGAS + Recall@K 端到端评估。

骨架版本：仅打印指标列表。后续将填充：
    - 合成评估集生成器
    - RAGAS 4 指标接入
    - Recall@K / MRR / NDCG 计算
    - baseline vs +reranker 完整 A/B

运行：
    uv run python Foundations/RAG-Primer/08-Evaluation/demo.py
"""
from __future__ import annotations

RAGAS_METRICS: tuple[str, ...] = (
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
)

IR_METRICS: tuple[str, ...] = (
    "recall_at_5",
    "mrr",
    "ndcg_at_5",
    "hit_rate",
)


def main() -> None:
    print("[08-Evaluation] 骨架就位。")
    print(f"生成层指标（RAGAS）：{', '.join(RAGAS_METRICS)}")
    print(f"检索层指标：{', '.join(IR_METRICS)}")
    print("详见 ./README.md")


if __name__ == "__main__":
    main()
