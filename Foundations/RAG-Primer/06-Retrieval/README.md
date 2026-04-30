# 06 · 召回（Retrieval）

从"向量近邻"升级到"**真正能找到答案的检索系统**"。
召回不只是相似度排序，还包括稀疏匹配、混合融合、查询改写、多样性。

---

## 一句话理解

> dense 召回懂语义但不认死字，
> sparse 召回认死字但不懂同义，
> **混合检索是大多数 RAG 系统的最低标配**。

---

## 召回方法谱系

| 方法 | 信号 | 强项 | 弱项 |
|---|---|---|---|
| **Dense（向量）** | 语义相似 | 同义/转述/跨语言 | 罕见词、ID、人名 |
| **Sparse（BM25）** | 词频 + IDF | 精确匹配、长尾词 | 同义、改写 |
| **Hybrid (RRF)** | 二者融合 | 稳健 | 调权 |
| **MMR（最大边际相关）** | 相关 + 多样 | 防冗余 | 可能漏掉相关 |
| **Re-ranking**（见 07） | cross-encoder 精排 | 精度跃升 | 慢 |

---

## Hybrid 检索：RRF 是默认武器

```
final_score(d) = Σ_i  1 / (k + rank_i(d))
```

- `k = 60` 是经验值
- 不需要调权重，不依赖分数尺度
- LangChain `EnsembleRetriever`、Weaviate、Qdrant 都内置

---

## Query 改写

| 技术 | 时机 | 提升点 |
|---|---|---|
| **HyDE** | query → 假设答案 → 向量化 | 长 query / 短 doc 不对称 |
| **Multi-Query** | query → N 个改写 → 并查 → 合并 | 提高 recall |
| **Step-back** | 抽象成元问题再查 | 复杂多跳问题 |
| **Decomposition** | 拆成子问题 | 多事实组合题 |

> 仓库内已实现：[`../../../RAG-Techniques/Basic/HyDE/`](../../../RAG-Techniques/Basic/HyDE/)、
> [`../../../RAG-Techniques/Basic/RAGFusion/`](../../../RAG-Techniques/Basic/RAGFusion/)

---

## Small-to-Big / Window Expansion

> 用**小 chunk 做相似度匹配**，命中后**返回它周围更大的窗口**给 LLM。
> 解决"chunk 小召回准但答案不全"的核心矛盾。

```
索引层：句子级（≈100 token）→ 高精度匹配
返回层：父段落（≈800 token）→ 完整上下文
```

---

## 元数据过滤

```python
retriever.invoke(
    "公司 2023 年营收",
    filter={"year": 2023, "doc_type": "annual_report"},
)
```

> 过滤条件用得好 → 召回质量直接翻倍，比换 embedding 见效快。

---

## 本目录文件

| 文件 | 说明 |
|---|---|
| `demo.py` | Dense / BM25 / Hybrid / MMR 横评，外加元数据过滤示例（骨架）|
| `README.md` | 本文件 |

---

## 计划中的 demo

- [ ] BM25 vs Dense 在"罕见术语 / 同义改写"两类 query 上的对比
- [ ] RRF Hybrid 实现 + 召回率提升曲线
- [ ] MMR 多样性参数 λ 的可视化
- [ ] Small-to-Big 实战

---

## 自测清单

- [ ] 能解释 RRF 为什么不需要分数归一化
- [ ] 能说出 Dense 与 Sparse 各自最强 / 最弱的 query 类型
- [ ] 能在自己的项目里加上一层元数据过滤

---

## 上下游

- 上一步 → [`../05-VectorStore/`](../05-VectorStore/)
- 下一步 → [`../07-Reranking/`](../07-Reranking/)
- 进阶范式 → [`../../../RAG-Techniques/`](../../../RAG-Techniques/)
- 索引 → [`../README.md`](../README.md)

---

**作者**: Beamus Wayne
**最后更新**: 2026-04-30
**状态**: 骨架
