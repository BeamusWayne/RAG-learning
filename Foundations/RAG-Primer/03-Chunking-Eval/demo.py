"""03-Chunking-Eval demo: 三大切分质量指标的最小计算。

骨架版本：仅打印指标列表。后续将填充：
    - 边界泄漏检测
    - chunk 内聚度（句对相似度均值/方差）
    - chunk 召回率 Recall@K

运行：
    uv run python Foundations/RAG-Primer/03-Chunking-Eval/demo.py
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalResult:
    """单次切分策略的评估结果。"""

    strategy: str
    boundary_leak_rate: float
    cohesion_mean: float
    cohesion_var: float
    chunk_recall_at_5: float


METRICS: tuple[str, ...] = (
    "boundary_leak_rate",
    "cohesion_mean",
    "cohesion_var",
    "chunk_recall_at_5",
)


def main() -> None:
    print("[03-Chunking-Eval] 骨架就位。")
    print(f"计划指标：{', '.join(METRICS)}")
    print("详见 ./README.md")


if __name__ == "__main__":
    main()
