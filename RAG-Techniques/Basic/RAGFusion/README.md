# RAG Fusion

> **一句话**：把一个问题扩展成多个子查询，分别检索，再用 RRF 算法把多路结果融合成一个排序，最后生成答案。

---

## 为什么需要 RAG Fusion？

单次检索有两个根本问题：

1. **覆盖盲区**：一个问题只有一种表述，向量检索只能命中语义最近的方向，其他相关文档被漏掉
2. **表述偏差**：用户措辞和知识库措辞不对齐，导致相关文档排名靠后

RAG Fusion 的解法：用 LLM 把问题翻译成多种表述，每种表述检索一次，再把多路结果用 **RRF 算法**智能合并。

---

## 完整流程

```
用户问题
   │
   ▼
LLM 查询扩展
   ├── 子查询 1 ──▶ 向量检索 ──▶ [doc_a #1, doc_b #2, doc_c #3]
   ├── 子查询 2 ──▶ 向量检索 ──▶ [doc_b #1, doc_d #2, doc_a #3]
   └── 子查询 3 ──▶ 向量检索 ──▶ [doc_e #1, doc_a #2, doc_b #3]
                                        │
                                   RRF 融合
                                        │
                              [doc_a, doc_b, doc_e, ...]
                                        │
                                    LLM 生成
                                        │
                                      答案
```

---

## RRF 算法

互惠排名融合（Reciprocal Rank Fusion）的得分公式：

```
score(doc) = Σ  1 / (k + rank_i(doc))
             i
```

- **rank_i** 是文档在第 i 路结果中的排名（从 1 开始）
- **k = 60**（原论文推荐值，平滑常数，防止第1名权重过高）

核心性质：**奖励"多路一致认可"的文档**，而非单路排名很高。

```
例：doc_a 在三路结果中分别排 #1, #3, #2
   score = 1/(60+1) + 1/(60+3) + 1/(60+2) = 0.0164 + 0.0157 + 0.0161 = 0.0482

   doc_x 只在一路排 #1
   score = 1/(60+1) = 0.0164
```

doc_a 三次出现，RRF 得分远高于只出现一次的 doc_x。

---

## 文件说明

| 文件 | 内容 | LLM 调用 |
|---|---|---|
| `01_query_expansion.py` | 只演示查询扩展这一步 | 1 次 |
| `02_rrf_algorithm.py` | 纯 RRF 算法，无需 API | 0 次 |
| `03_rag_fusion_pipeline.py` | 完整 RAG Fusion 流程，打印每步中间结果 | 2 次 |
| `04_comparison.py` | Naive RAG vs HyDE vs RAG Fusion 三方对比 | 共 5 次 |

**建议按顺序学习**：先理解各步骤（01→02），再看完整流程（03），最后对比效果（04）。

---

## 快速运行

```bash
export OPENAI_API_KEY=...
export OPENAI_BASE_URL=...   # 可选，兼容第三方网关

cd RAGFusion

# 从简单到复杂
uv run python 01_query_expansion.py   # 无需向量库
uv run python 02_rrf_algorithm.py     # 无需 API Key
uv run python 03_rag_fusion_pipeline.py
uv run python 04_comparison.py        # 三方完整对比
```

---

## 与 HyDE 的区别

| | HyDE | RAG Fusion |
|---|---|---|
| 核心思路 | 改写问题风格 | 扩展问题角度 |
| 检索次数 | 1 次 | N 次（默认 4） |
| LLM 额外调用 | 1 次（生成假设文档） | 1 次（查询扩展） |
| 适合场景 | 问题与文档风格差距大 | 问题角度单一、覆盖不足 |
| 可组合 | ✅ 可以生成 N 个假设文档再 RRF | — |

两者可以叠加：生成多个假设文档 → 每个分别检索 → RRF 融合。

---

## 成本考量

| 方法 | LLM 调用次数 | embedding 调用次数 |
|---|---|---|
| Naive RAG | 1 | 1（查询） |
| HyDE | 2 | 1（假设文档） |
| RAG Fusion (N=4) | 2 | 4（每路子查询） |

RAG Fusion 的主要成本在于 embedding 调用次数是 N 倍，LLM 成本与 HyDE 相同。

---

## 论文来源

**RAG-Fusion: A New Take on Retrieval-Augmented Generation**
Raudaschl, 2023 — 提出将 RAG 与 RRF 结合的方案

**Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods**
Cormack et al., 2009 — RRF 原论文

---

## 学习检查清单

- [ ] 能解释为什么单次检索存在"覆盖盲区"
- [ ] 能手算一个简单的 RRF 得分（3个文档 × 2路）
- [ ] 运行 `02_rrf_algorithm.py`，理解 k 值变化对排序的影响
- [ ] 运行 `04_comparison.py`，观察三种方法的检索文档差异
- [ ] 思考：问题 "redis" 这样的单词查询，RAG Fusion 有帮助吗？

---

## 延伸阅读

- Hybrid Search（BM25 + 向量）— 从检索器层面扩展覆盖，与 RAG Fusion 正交
- Reranking — RAG Fusion 后再加一层精排，效果更好
- HyDE — 本项目 `HyDE/` 目录
