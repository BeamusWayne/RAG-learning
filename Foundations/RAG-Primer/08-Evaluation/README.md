# 08 · 端到端评估（Evaluation）

> 没有评估，所有"调优"都是玄学。

03-Chunking-Eval 评的是切分本身，本模块评的是**整套 RAG 流水线**——
召回好不好、上下文给得对不对、最终回答有没有幻觉、回答了没回答到点子上。

---

## 一句话理解

> RAG 评估有两层：
> **检索层**（找得到吗、找得准吗）和**生成层**（答得对吗、答得忠实吗）。
> 两层指标分开看，混在一起看就是糊涂账。

---

## 检索层指标

| 指标 | 定义 | 何时关注 |
|---|---|---|
| **Recall@K** | top-K 中是否包含金标 | 总览召回能力 |
| **Hit Rate** | 至少命中一条 | 业务低门槛场景 |
| **MRR**（Mean Reciprocal Rank） | 第一条命中位置的倒数平均 | 关注最佳位置 |
| **NDCG@K** | 考虑相关性等级和位置 | 多级相关性场景 |
| **Precision@K** | top-K 中相关比例 | 给 LLM 上下文质量 |

---

## 生成层指标（RAGAS 框架）

| 指标 | 衡量 | 直觉 |
|---|---|---|
| **Faithfulness** | 答案是否被给定上下文支持 | 反幻觉 |
| **Answer Relevancy** | 答案是否切题 | 反跑题 |
| **Context Precision** | 召回上下文里相关比例 + 排序 | 给上下文有效性 |
| **Context Recall** | 金标答案所需信息是否都在上下文里 | 召回完整性 |

> RAGAS 4 指标天然形成 2×2 矩阵：检索（precision/recall）× 生成（faithfulness/relevancy）。

---

## 其他评估框架

| 框架 | 特点 |
|---|---|
| **RAGAS** | 主流标准，4 大指标 + 自定义 |
| **TruLens** | 可视化追踪、Feedback Functions |
| **ARES** | 用合成数据训练专用评估器 |
| **DeepEval** | pytest 风格断言式评估 |
| **G-Eval** | LLM-as-judge 通用框架 |

---

## 评估集构造（最难的一步）

```
1. 人工标注金标集（≥100 条，质量优于数量）
   或
2. LLM 合成 → 人工抽检 ≥10%
   ↓
3. 标注每条：query / golden_answer / supporting_chunks
   ↓
4. 划分 dev / test，固定 test 不再调
```

> **没有固定 test 集 → 你以为在调优，其实在过拟合。**

---

## 跑一次评估的最小循环

```
变更（改 chunk_size / 换 embedding / 加 reranker）
   ↓
跑 dev 集
   ↓
看 Recall@5 + Faithfulness + Answer Relevancy
   ↓
有提升？→ 进 test 复测 → 决定是否合并
   ↓
无提升 → 回滚，记录原因
```

---

## 本目录文件

| 文件 | 说明 |
|---|---|
| `demo.py` | RAGAS 4 指标 + Recall@K 的最小评估脚本（骨架）|
| `README.md` | 本文件 |

---

## 计划中的 demo

- [ ] 合成评估集生成器（带人工抽检入口）
- [ ] RAGAS 4 指标接入
- [ ] Recall@K / MRR / NDCG 计算器
- [ ] 一次完整 A/B（baseline vs +reranker）

---

## 自测清单

- [ ] 能区分检索层与生成层指标，不会把它们搅在一起
- [ ] 能说出 Faithfulness 和 Answer Relevancy 的差别
- [ ] 知道"没有 test 集 = 在过拟合"

---

## 上下游

- 上一步 → [`../07-Reranking/`](../07-Reranking/)
- 切分专项评估 → [`../03-Chunking-Eval/`](../03-Chunking-Eval/)
- 下一步 → [`../09-Pitfalls/`](../09-Pitfalls/)
- 索引 → [`../README.md`](../README.md)

---

**作者**: Beamus Wayne
**最后更新**: 2026-04-30
**状态**: 骨架
