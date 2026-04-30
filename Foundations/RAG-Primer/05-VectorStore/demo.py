"""05-VectorStore demo: FAISS Flat / IVF / HNSW 精度-延迟曲线对比。

骨架版本：仅打印索引列表。后续将填充：
    - 三种 FAISS 索引在同一份向量上的召回率 vs QPS 曲线
    - HNSW efSearch 扫描
    - pgvector 100K 向量实战
    - 元数据过滤前/后实现差异

运行：
    uv run python Foundations/RAG-Primer/05-VectorStore/demo.py
"""
from __future__ import annotations

INDEX_TYPES: tuple[str, ...] = ("flat", "ivf", "hnsw", "hnsw_pq")


def main() -> None:
    print("[05-VectorStore] 骨架就位。")
    print(f"计划对比索引：{', '.join(INDEX_TYPES)}")
    print("详见 ./README.md")


if __name__ == "__main__":
    main()
