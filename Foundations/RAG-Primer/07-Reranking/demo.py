"""07-Reranking demo: bge-reranker / LLM-as-reranker 横评。

骨架版本：仅打印 reranker 列表。后续将填充：
    - 召回 top-50 → bge-reranker → top-5 流水线
    - LLM-as-Reranker（pointwise / listwise）实现
    - 重排前后 NDCG@5 对比
    - 延迟 vs 精度曲线

运行：
    uv run python Foundations/RAG-Primer/07-Reranking/demo.py
"""
from __future__ import annotations

RERANKERS: tuple[str, ...] = (
    "bge-reranker-v2-m3",
    "cohere-rerank-v3",
    "llm-pointwise",
    "llm-listwise",
)


def main() -> None:
    print("[07-Reranking] 骨架就位。")
    print(f"计划对比 reranker：{', '.join(RERANKERS)}")
    print("详见 ./README.md")


if __name__ == "__main__":
    main()
