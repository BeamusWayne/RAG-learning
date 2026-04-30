"""06-Retrieval demo: Dense / BM25 / Hybrid / MMR 横评。

骨架版本：仅打印方法列表。后续将填充：
    - BM25 vs Dense 在罕见词 / 同义改写两类 query 上的对比
    - RRF Hybrid 实现
    - MMR 多样性 λ 可视化
    - Small-to-Big 实战

运行：
    uv run python Foundations/RAG-Primer/06-Retrieval/demo.py
"""
from __future__ import annotations

METHODS: tuple[str, ...] = ("dense", "bm25", "hybrid_rrf", "mmr", "small_to_big")


def main() -> None:
    print("[06-Retrieval] 骨架就位。")
    print(f"计划对比召回方法：{', '.join(METHODS)}")
    print("详见 ./README.md")


if __name__ == "__main__":
    main()
