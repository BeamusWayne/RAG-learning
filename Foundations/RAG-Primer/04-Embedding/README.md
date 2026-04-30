# 04 · 向量化（Embedding）

把 chunk 变成向量。embedding 模型决定了**召回的天花板**——
后面再花哨的重排和 prompt 工程也突破不了 embedding 没召回到的 chunk。

---

## 一句话理解

> embedding 选错了，整个 RAG 系统从根上就漏。
> 选对了，剩下的才是"调优"，否则只是"挣扎"。

---

## 主流模型对比（2025–2026）

| 模型 | 类型 | 长度 | 多语言 | 备注 |
|---|---|---|---|---|
| `text-embedding-3-large` | OpenAI 闭源 | 8K | ✓ | 通用强基线，价格高 |
| `BGE-M3` | 智源开源 | 8K | ✓ | 同时输出 dense + sparse + multi-vector |
| `bge-large-zh-v1.5` | 智源开源 | 512 | 中英 | **中文场景默认选** |
| `gte-Qwen2-7B-instruct` | 阿里开源 | 32K | ✓ | 大模型派 embedding，长文本强 |
| `voyage-3-large` | Voyage 闭源 | 32K | ✓ | 检索专用，长上下文性能好 |
| `jina-embeddings-v3` | Jina 开源 | 8K | ✓ | 任务可选（retrieval/clustering/...） |

---

## 选型决策树

```
是否中文为主？
├─ 是 → 是否需要长上下文（>2K）？
│      ├─ 是 → BGE-M3 / gte-Qwen2
│      └─ 否 → bge-large-zh-v1.5（性价比之王）
└─ 否 → 是否预算敏感？
       ├─ 是 → BGE-M3 / jina-v3 自托管
       └─ 否 → text-embedding-3-large / voyage-3
```

---

## 关键工程细节

### 归一化
- **几乎所有 embedding 模型都假设 L2 归一化后用 cosine**
- 不归一化直接做内积 → 长向量永远赢，污染排序

### 对称 vs 非对称
- 对称：query 和 doc 用同一编码器（句子相似度场景）
- 非对称：query 短、doc 长，分别编码（**RAG 默认场景**）
- 用错会显著掉点

### 维度
- 高维（>1024）：精度高，存储贵，索引慢
- Matryoshka embedding：训练时支持任意维度截断，推理可降维

---

## 微调入门

| 何时该微调 | 难点 |
|---|---|
| 领域术语严重偏离通用语料（医学 / 法律 / 内部黑话） | 难负例挖掘 |
| 召回率持续低于 60% 且换模型无效 | 标注成本 |
| 双编码器精度上限触顶 | 评估集设计 |

> 大多数项目**先别微调**，先把切分、混合检索、reranker 做对。

---

## 本目录文件

| 文件 | 说明 |
|---|---|
| `demo.py` | 三个 embedding 模型在同一份语料上的召回对比（骨架）|
| `README.md` | 本文件 |

---

## 计划中的 demo

- [ ] 三模型横评：bge-zh / OpenAI / BGE-M3
- [ ] 归一化 vs 不归一化效果差异
- [ ] 对称 vs 非对称编码器对比
- [ ] Matryoshka 维度截断曲线

---

## 自测清单

- [ ] 能说出归一化为什么重要
- [ ] 能解释对称/非对称的差别
- [ ] 能列出"换 embedding 模型"前应先排查的三件事

---

## 上下游

- 上一步 → [`../03-Chunking-Eval/`](../03-Chunking-Eval/)
- 下一步 → [`../05-VectorStore/`](../05-VectorStore/)
- 索引 → [`../README.md`](../README.md)

---

**作者**: Beamus Wayne
**最后更新**: 2026-04-30
**状态**: 骨架
