"""01-Loading demo: 三种格式（PDF / Markdown / HTML）的最小加载示例。

骨架版本：仅打印占位输出。后续将填充：
    - PyMuPDF / pdfplumber 双栏 PDF 对比
    - MarkdownHeaderTextSplitter 保留层级
    - BeautifulSoup 正文抽取

运行：
    uv run python Foundations/RAG-Primer/01-Loading/demo.py
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadedDoc:
    """加载后的统一文档对象。

    后续模块（02-Chunking 等）消费此结构。
    """

    text: str
    source: str
    page: int | None
    section: str | None
    doc_type: str


def main() -> None:
    print("[01-Loading] 骨架就位。")
    print("计划实现：PDF / Markdown / HTML 三种格式的最小加载示例。")
    print("详见 ./README.md")


if __name__ == "__main__":
    main()
