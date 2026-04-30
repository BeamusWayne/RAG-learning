# RAG Primer：RAG 工程基本功

> 在玩 HyDE / RAG-Fusion / CRAG / Self-RAG 这些花式范式之前，
> 你需要先把"切分 → 向量化 → 召回 → 重排 → 评估"这条流水线的每一段单独搞懂。

本目录是 RAG 的**工程前置课**，不绑定任何具体范式，所有 RAG 系统都会踩这些坑。

> 🆕 **新手从这里开始** → [`TUTORIAL.md`](TUTORIAL.md)：写给"刚学 RAG，想动手"的人，带你 4 周走完全流水线。

---

## 学习路径

```
01-Loading        文档加载（PDF/HTML/Markdown/代码/表格/OCR）
   ↓
02-Chunking       切分策略（定长 / Recursive / Semantic / Parent-Child / Late）
   ↓
03-Chunking-Eval  切分质量验证（边界泄漏、内聚度、chunk 召回率）
   ↓
04-Embedding      向量化（模型选型、归一化、相似度度量）
   ↓
05-VectorStore    向量库与索引（FAISS/Chroma/Milvus/Qdrant，HNSW vs IVF）
   ↓
06-Retrieval      召回（dense / BM25 / hybrid / MMR / 元数据过滤）
   ↓
07-Reranking      重排（cross-encoder / LLM-as-reranker）
   ↓
08-Evaluation     端到端评估（Recall@K、MRR、RAGAS、合成评估集）
   ↓
09-Pitfalls       常见踩坑速查
```

---

## 模块一览

| # | 模块 | 一句话定位 |
|---|---|---|
| 01 | [Loading](01-Loading/) | 把各种文档读成统一的、带元数据的纯文本流 |
| 02 | [Chunking](02-Chunking/) | 把长文档切成检索友好的 chunk，**RAG 工程师 30% 的工作量** |
| 03 | [Chunking-Eval](03-Chunking-Eval/) | 量化判断切分策略好坏，最容易被跳过的一环 |
| 04 | [Embedding](04-Embedding/) | 选对 embedding 模型 = 召回上限的天花板 |
| 05 | [VectorStore](05-VectorStore/) | 索引结构决定延迟-精度曲线 |
| 06 | [Retrieval](06-Retrieval/) | dense + sparse + 过滤 + MMR，召回不只是相似度 |
| 07 | [Reranking](07-Reranking/) | 上 reranker 是性价比最高的精度提升 |
| 08 | [Evaluation](08-Evaluation/) | 没有评估，所有"调优"都是玄学 |
| 09 | [Pitfalls](09-Pitfalls/) | RAG 翻车 Top 10，避坑速查 |

---

## 与本仓库其他目录的关系

| 目录 | 关系 |
|---|---|
| [`../LangChain_Tutorial_Fast/`](../LangChain_Tutorial_Fast/) | 同为基础课。LangChain 教 API，本目录教 RAG 流水线工程 |
| [`../../RAG-Techniques/`](../../RAG-Techniques/) | 进阶范式（HyDE / Fusion / CRAG / Self-RAG / Agentic）都假设你已掌握本目录内容 |
| [`../../RAG-Techniques/RAG范式总览.md`](../../RAG-Techniques/RAG范式总览.md) | 范式地图。本目录补的是范式之下的工程地基 |

---

## 共享数据

所有模块共用仓库根的 [`../../Data/`](../../Data/) 作为语料，方便横向对比同一份数据下不同策略的差异。

---

**作者**: Beamus Wayne
**最后更新**: 2026-04-30
**状态**: 骨架就位，demo 持续补齐中
