"""01-Loading demo: 三种格式（Markdown / HTML / 纯文本）的最小加载示例。

演示要点：
    - 把不同格式读成统一的 LoadedDoc(text, source, page, section, doc_type, extra)
    - Markdown 按标题路径自动写入 section 元数据
    - HTML 用 BeautifulSoup 抽正文、丢导航
    - 模型 / API 配置全部走仓库根 .env，本 demo 不需要任何 LLM 调用

运行：
    uv run python Foundations/RAG-Primer/01-Loading/demo.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from _common import SAMPLE_TEXT_PATH, section  # noqa: E402


@dataclass(frozen=True)
class LoadedDoc:
    """加载后的统一文档对象，下游 02-Chunking 直接消费。"""

    text: str
    source: str
    page: int | None
    section: str | None
    doc_type: str
    extra: dict = field(default_factory=dict)


def load_plain_text(path: Path) -> list[LoadedDoc]:
    raw = path.read_text(encoding="utf-8")
    return [LoadedDoc(text=raw, source=str(path), page=None, section=None, doc_type="text")]


def load_markdown(md_text: str, source: str) -> list[LoadedDoc]:
    """按一级 / 二级标题切分，section 字段写'上一级/当前'路径。"""
    docs: list[LoadedDoc] = []
    cur_h1: str | None = None
    cur_h2: str | None = None
    buf: list[str] = []

    def flush() -> None:
        if not buf:
            return
        path = "/".join(p for p in (cur_h1, cur_h2) if p)
        docs.append(
            LoadedDoc(
                text="\n".join(buf).strip(),
                source=source,
                page=None,
                section=path or None,
                doc_type="md",
            )
        )

    for line in md_text.splitlines():
        if line.startswith("# "):
            flush()
            buf.clear()
            cur_h1, cur_h2 = line[2:].strip(), None
            continue
        if line.startswith("## "):
            flush()
            buf.clear()
            cur_h2 = line[3:].strip()
            continue
        buf.append(line)
    flush()
    return docs


def load_html(html: str, source: str) -> list[LoadedDoc]:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return [
            LoadedDoc(
                text=html,
                source=source,
                page=None,
                section=None,
                doc_type="html",
                extra={"warning": "未安装 beautifulsoup4，未做正文抽取"},
            )
        ]
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    text = soup.get_text(separator="\n", strip=True)
    return [LoadedDoc(text=text, source=source, page=None, section=title, doc_type="html")]


SAMPLE_MD = """# Python 笔记

## 基础

Python 是一种动态类型的高级语言。

## 进阶

装饰器、上下文管理器、生成器是三大语言级特性。
"""

SAMPLE_HTML = """<html><head><title>示例文章</title></head>
<body>
  <nav>导航 · 首页 · 关于</nav>
  <article>
    <h1>RAG 是什么</h1>
    <p>检索增强生成在回答前先翻书，避免 LLM 凭空乱答。</p>
  </article>
  <footer>© 2026</footer>
</body></html>
"""


def main() -> None:
    section("纯文本加载")
    if SAMPLE_TEXT_PATH.exists():
        docs = load_plain_text(SAMPLE_TEXT_PATH)
        d = docs[0]
        print(f"  source={Path(d.source).name}  doc_type={d.doc_type}  长度={len(d.text)} 字")
        print(f"  首 80 字: {d.text[:80]!r}")
    else:
        print(f"  未找到示例文本：{SAMPLE_TEXT_PATH}（跳过）")

    section("Markdown 加载（按标题切，保留 section 路径）")
    md_docs = load_markdown(SAMPLE_MD, source="<inline-md>")
    for d in md_docs:
        print(f"  section={d.section!r:20}  长度={len(d.text):3}  片段={d.text[:30]!r}")

    section("HTML 加载（去导航 / 广告）")
    html_docs = load_html(SAMPLE_HTML, source="<inline-html>")
    for d in html_docs:
        print(f"  title={d.section!r}")
        print(f"  正文：{d.text}")

    section("元数据下游用途")
    print("  - 引用：source / page / section 直接拼成可点击的'出处'")
    print("  - 过滤：05-VectorStore / 06-Retrieval 可按 doc_type / section 做元数据筛选")


if __name__ == "__main__":
    main()
