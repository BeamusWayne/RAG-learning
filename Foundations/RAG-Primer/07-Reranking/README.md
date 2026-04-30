# 07 · 重排（Reranking）

召回的 top-K 通常**精度不够直接喂给 LLM**——里面混着相关、半相关、纯噪声。
Reranker 用更贵的精排模型重新打分，**把真相关的几条提到最前**。

---

## 一句话理解

> 召回 = "宽撒网，求 recall"；
> 重排 = "精挑细选，求 precision"。
> **一个完整的 RAG 系统两步都不能少**。

---

## 召回 → 重排 的两段式

```
       query
         │
         ▼
   ┌──────────┐    top-50         ┌──────────┐    top-5
   │  召回器   │ ─────────────► │  重排器   │ ──────►  LLM
   │ (双编码) │   bi-encoder    │ (交叉编码)│   cross
   └──────────┘   快 / 粗略      └──────────┘   慢 / 精
```

- 双编码（bi-encoder）：query 和 doc **分开编码**再算相似度，可索引
- 交叉编码（cross-encoder）：query 和 doc **拼接进同一模型**输出分数，**精度高一档但不可索引**

---

## 主流 Reranker

| 模型 | 类型 | 特点 |
|---|---|---|
| `bge-reranker-v2-m3` | 开源（智源） | 多语言，中文强，免费 |
| `Cohere Rerank v3` | 闭源 API | 商用稳定，支持多语言 |
| `Jina Reranker v2` | 开源 | 速度优 |
| `mxbai-rerank-large` | 开源 | 英文强 |
| **LLM-as-Reranker** | 调用 LLM 直接打分 | 灵活、可解释、贵且慢 |

---

## 性价比经验

| 场景 | 建议 |
|---|---|
| 召回 top-20 → 给 LLM 5 条 | **强烈建议上 reranker**，10ms-100ms 成本，召回精度大幅提升 |
| 召回 top-3 直接给 LLM | 不需要 reranker，省成本 |
| 已用 hybrid 混合 + RRF | 仍可叠加 reranker，提升明显 |
| LLM 上下文窗超长（>32K） | 仍建议 reranker，避免 lost-in-the-middle |

---

## LLM-as-Reranker

- **Pointwise**：让 LLM 给每个 chunk 打 0–10 分
- **Pairwise**：两两比较哪个更相关
- **Listwise**：一次性输出排序好的 id 列表（如 RankGPT）

> Listwise 精度最高但 prompt 复杂；Pointwise 最简单可并发。

---

## 本目录文件

| 文件 | 说明 |
|---|---|
| `demo.py` | bge-reranker / LLM-as-reranker 在同一份召回结果上的对比（骨架）|
| `README.md` | 本文件 |

---

## 计划中的 demo

- [ ] 召回 top-50 → bge-reranker → top-5 流水线
- [ ] LLM-as-Reranker（pointwise / listwise）实现
- [ ] 重排前后 NDCG@5 对比
- [ ] 延迟 vs 精度曲线

---

## 自测清单

- [ ] 能解释为什么 cross-encoder 不能直接做召回
- [ ] 能说出何时该 / 不该上 reranker
- [ ] 能在自己的项目里加一层 bge-reranker 并量化提升

---

## 上下游

- 上一步 → [`../06-Retrieval/`](../06-Retrieval/)
- 下一步 → [`../08-Evaluation/`](../08-Evaluation/)
- 索引 → [`../README.md`](../README.md)

---

**作者**: Beamus Wayne
**最后更新**: 2026-04-30
**状态**: 骨架
