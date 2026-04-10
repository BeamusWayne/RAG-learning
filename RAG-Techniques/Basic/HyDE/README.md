# HyDE — Hypothetical Document Embeddings

> **一句话**：不用问题的 embedding 检索，而是先让 LLM 生成一个"假设答案"，再用假设答案的 embedding 去检索真实知识库。

---

## 为什么需要 HyDE？

Naive RAG 有一个隐藏问题：**问题和文档在向量空间里天然不对齐**。

```
用户问："怎么选向量数据库？"       ← 疑问句，口语化
知识库："Chroma 是一个开源的本地向量数据库..." ← 陈述句，文档风格
```

两者语义相近，但 embedding 距离可能并不近——因为它们的**语言风格和句式结构**差异太大。

HyDE 的思路：先把问题"翻译"成文档语言，再去检索。

---

## 原理对比

```
Naive RAG
─────────────────────────────────────────────────────
用户问题 ──embed──▶ 向量检索 ──▶ 相关文档 ──▶ LLM ──▶ 答案


HyDE RAG
─────────────────────────────────────────────────────
用户问题 ──LLM──▶ 假设文档 ──embed──▶ 向量检索 ──▶ 相关文档 ──▶ LLM ──▶ 答案
           （Step 1）           （Step 2）             （Step 3）
```

**关键洞察**：假设文档就算内容不准确，它的 embedding 也比问题本身更接近知识库里真实文档的 embedding。检索靠的是"语言风格对齐"，不是内容正确性。

---

## 三步拆解

### Step 1 — 生成假设文档

```python
prompt = "请为下面的问题写一段技术文档片段（2-4句话）..."
hypothesis = llm(question)
# 例："向量数据库的选择应考虑数据规模、部署方式和生态集成。
#      小型项目推荐 Chroma（本地，开源），生产环境可考虑 Pinecone..."
```

这步不看知识库，纯粹靠模型内部知识生成。内容可能有幻觉，**没关系**。

### Step 2 — 用假设文档检索

```python
retrieved_docs = vector_store.search(hypothesis, top_k=3)
# 假设文档的 embedding 更接近知识库文档风格 → 命中更准
```

### Step 3 — 用真实文档生成最终答案

```python
answer = llm(question, context=retrieved_docs)
# 最终答案基于真实知识库，不是假设文档
```

假设文档只是"检索的跳板"，不会出现在最终答案里。

---

## 效果最显著的场景

| 场景 | 原因 |
|---|---|
| 问题是口语化问句 | 文档是陈述风格，风格差距最大 |
| 知识库是技术文档/论文 | 专业术语密集，问题难以命中 |
| 用户问题很模糊/宽泛 | 假设文档能"具象化"用户意图 |
| 多语言跨语检索 | 假设文档可对齐目标语言风格 |

---

## 效果不明显的场景

- 问题本身已经是文档风格（如复制粘贴的技术描述）
- 知识库很小（<100 条），向量差异不关键
- 问题极短（1-2 词关键词搜索）——此时 BM25 更合适

---

## 代码结构

```
HyDE/
├── demo.py      # MVP：Naive RAG vs HyDE 对比演示
└── README.md    # 本文件
```

### 运行 demo

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=...   # 可选，兼容第三方网关

cd HyDE
uv run python demo.py
```

运行后会打印：
1. Naive RAG 检索到的文档 + 答案
2. HyDE 生成的假设文档 + 检索到的文档 + 答案
3. 两者检索结果差异对比（最直观看出 HyDE 额外命中了什么）

---

## 与其他 RAG 技术的关系

```
Naive RAG
    └── 加上假设文档生成 ──▶ HyDE
    └── 加上多查询扩展   ──▶ RAG Fusion（下一步可学）
    └── 加上检索评估修正 ──▶ CRAG（见 Experiment/CRAG/）
    └── 加上多步推理决策 ──▶ Agentic RAG（见 AgenticRAG/）
```

HyDE 和 RAG Fusion 可以叠加使用：先生成多个假设文档，分别检索，再融合排序。

---

## 论文来源

**Precise Zero-Shot Dense Retrieval without Relevance Labels**
Gao et al., 2022 — [arxiv.org/abs/2212.10496](https://arxiv.org/abs/2212.10496)

提出 HyDE，在多个 zero-shot 检索基准上超越 BM25 和有监督 dense retrieval。

---

## 学习检查清单

- [ ] 能解释为什么问题和文档 embedding 不对齐
- [ ] 能说明假设文档的内容不准确为何不影响检索效果
- [ ] 能画出 HyDE 三步流程图
- [ ] 运行 demo，观察 HyDE 相比 Naive RAG 额外命中了哪些文档
- [ ] 思考：什么场景下 HyDE 反而不如 Naive RAG？

---

## 延伸阅读

- RAG Fusion — 多查询 + RRF 融合排序
- Step-Back Prompting — 先"退一步"抽象问题再检索
- Query Rewriting — 改写查询而非生成假设文档（更轻量的思路）
