"""09-Pitfalls demo: 复现并修复 3 个典型 RAG 翻车场景。

骨架版本：仅打印坑位列表。后续将填充：
    - chunk 过大导致语义稀释（Pitfall #2）
    - embedding 未归一化（Pitfall #4）
    - 中文 BM25 未分词（Pitfall #6）

运行：
    uv run python Foundations/RAG-Primer/09-Pitfalls/demo.py
"""
from __future__ import annotations

PITFALLS: tuple[str, ...] = (
    "chunk_too_large",
    "embedding_not_normalized",
    "chinese_bm25_no_tokenizer",
)


def main() -> None:
    print("[09-Pitfalls] 骨架就位。")
    print(f"计划复现的坑：{', '.join(PITFALLS)}")
    print("完整 Top-10 列表见 ./README.md")


if __name__ == "__main__":
    main()
