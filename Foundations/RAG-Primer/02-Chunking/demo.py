"""02-Chunking demo: 五种切分策略并排对比。

骨架版本：仅打印策略列表。后续将填充：
    - Fixed / Recursive / Markdown / Semantic / Parent-Child
    - chunk 长度分布可视化
    - chunk_size × overlap 网格扫

运行：
    uv run python Foundations/RAG-Primer/02-Chunking/demo.py
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    """切分后的最小单元。"""

    text: str
    source: str
    chunk_id: int
    parent_id: int | None  # Parent-Child 模式用
    metadata: dict


STRATEGIES: tuple[str, ...] = (
    "fixed",
    "recursive",
    "markdown",
    "semantic",
    "parent-child",
)


def main() -> None:
    print("[02-Chunking] 骨架就位。")
    print(f"计划对比策略：{', '.join(STRATEGIES)}")
    print("详见 ./README.md")


if __name__ == "__main__":
    main()
