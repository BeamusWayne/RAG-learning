# 01 · 文档加载（Loading）

把各种格式的源文档（PDF / HTML / Markdown / 代码 / 表格 / 扫描件）读成
**统一的、带元数据的纯文本流**，作为后续切分的输入。

---

## 一句话理解

> RAG 的所有问题，**至少一半是从加载这一步就埋下的**：
> 表格被打散、双栏 PDF 串行、页眉页脚混入正文、代码缩进被破坏 ……
> 后面切得再漂亮也救不回来。

---

## 计划覆盖的内容

| 主题 | 工具 / 关键词 | 备注 |
|---|---|---|
| PDF（文本层） | `pypdf`, `pdfplumber`, `PyMuPDF` | 双栏、跨页、目录 |
| PDF（扫描件） | `tesseract`, `paddleocr`, `RapidOCR` | OCR 后处理：去噪、版面 |
| Markdown | `MarkdownHeaderTextSplitter` | 保留层级标题作元数据 |
| HTML | `BeautifulSoup`, `unstructured` | 去广告、保留正文 |
| Code | `tree-sitter`, `LanguageParser` | 函数级切分基础 |
| 表格 | `camelot`, `unstructured` | 转 markdown / JSON |
| 公式 | `mathpix`, `LaTeX-OCR` | 学术语料关键 |

---

## 元数据设计（传递给后续模块）

```python
@dataclass(frozen=True)
class LoadedDoc:
    text: str
    source: str          # 文件路径或 URL
    page: int | None     # PDF 页码
    section: str | None  # Markdown 标题路径，如 "ch1/intro"
    doc_type: str        # "pdf" | "md" | "html" | "code" | ...
    extra: dict          # 自由扩展
```

> 元数据不是装饰品——后面的元数据过滤、Parent-Child 召回都靠它。

---

## 本目录文件

| 文件 | 说明 |
|---|---|
| `demo.py` | 三种格式（PDF / Markdown / HTML）的最小加载示例（骨架）|
| `README.md` | 本文件 |

---

## 计划中的 demo

- [ ] PDF 双栏 vs 单栏，对比三种解析器的输出差异
- [ ] Markdown 按标题切分并保留层级元数据
- [ ] HTML 正文抽取（去导航/广告）
- [ ] 代码文件按函数边界切分

---

## 自测清单

- [ ] 能说出为什么不该把 PDF 直接当一个长字符串 join
- [ ] 能解释元数据在召回阶段的两种用途（过滤 / 引用）
- [ ] 能识别一份"加载就坏了"的语料的常见症状

---

## 上下游

- 下一步 → [`../02-Chunking/`](../02-Chunking/)
- 索引 → [`../README.md`](../README.md)

---

**作者**: Beamus Wayne
**最后更新**: 2026-04-30
**状态**: 骨架
