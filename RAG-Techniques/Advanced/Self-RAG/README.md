# Self-RAG 学习笔记（本目录）

本目录学习 **Self-RAG**（自我反思式 RAG）：让模型在生成过程中**自己决定是否检索、检索结果是否相关、答案是否被证据支持、整体是否有用**，从而显著降低幻觉。

> 论文：Asai et al., 2023.
> *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.*
> [arXiv:2310.11511](https://arxiv.org/abs/2310.11511)

---

## 一句话理解

> 普通 RAG：先检索 → 拼上下文 → 生成。
> Self-RAG：先问"要不要查"，查完后**逐段评相关性**，生成后**评是否被支持**，最后**整体打分**。

每一步都是显式的反思决策，而不是黑盒生成。

---

## 四个反思 Token

| Token | 取值 | 时机 | 作用 |
|---|---|---|---|
| **Retrieve** | `Yes / No` | 收到问题时 | 判断是否需要外部知识；常识题可直接答 |
| **IsRel** | `Relevant / Irrelevant` | 每段检索结果 | 过滤噪声段落，避免被无关内容污染 |
| **IsSup** | `Fully / Partial / No` | 每个草稿答案 | 检查回答是否真的能从段落推出来 |
| **IsUse** | `1 / 2 / 3 / 4 / 5` | 最终答案 | 给整体回答一个有用性评分 |

原论文中模型经过微调，能直接吐出这些 token；本目录的 `demo.py` 用 prompt 让通用 LLM 扮演同样角色，便于学习。

---

## 流程图

```
                ┌── No  ──→ 直接回答 ──→ IsUse 打分
   query ──→ Retrieve?
                └── Yes ──→ 检索 top-k 段落
                              │
                              ▼
                  ┌──── 对每个段落 ────┐
                  │  IsRel 相关性判断  │
                  │      │             │
                  │   Relevant?        │
                  │   ├─ No  → 丢弃    │
                  │   └─ Yes → 草稿    │
                  │           │        │
                  │      IsSup 支持度  │
                  └────────┬───────────┘
                           ▼
                聚合所有"被支持"的草稿 ──→ 最终答案 ──→ IsUse 打分
```

---

## 与相邻技术的对比

| 维度 | Naive RAG | CRAG | Self-RAG | Agentic RAG |
|---|---|---|---|---|
| 是否决定检索 | 总是检索 | 总是检索 | **自主决定** | 自主决定 |
| 段落级评估 | 无 | 有（修正 / 网搜） | **有（逐段 IsRel）** | 视实现 |
| 支持度评估 | 无 | 弱 | **有（IsSup）** | 视实现 |
| 多步推理 | 无 | 单轮纠错 | 可扩展 | **核心特性** |
| 训练成本 | 低 | 中（需评估器） | **高（反思 token 微调）** | 中高 |

> Self-RAG 与 CRAG 都属于"加一层评估"的方向：
> CRAG 偏**检索后纠错**（不行就网搜），Self-RAG 偏**全流程自评**（每步都有 token）。

---

## 本目录文件

| 文件 | 说明 |
|---|---|
| [`demo.py`](demo.py) | 最小教学实现：四个反思决策点 + 内置向量库 + 轨迹打印 |
| `README.md` | 本文件 |

---

## 快速运行

```bash
export DASHSCOPE_API_KEY=...     # 用于 embedding
export OPENAI_API_KEY=...        # 用于 chat（或兼容网关）
export OPENAI_BASE_URL=...       # 可选：第三方网关

cd RAG-Techniques/Advanced/Self-RAG
uv run python demo.py
```

输入示例：

```
请输入你的问题：Self-RAG 的核心思想是什么？
```

输出会显示完整反思轨迹：

```
问题：Self-RAG 的核心思想是什么？
[Retrieve] = Yes
  段落 1 | IsRel=Relevant | IsSup=Fully
    passage: Self-RAG 通过反思 token 动态决定是否检索 ...
    draft  : Self-RAG 的核心思想是 ...
  段落 2 | IsRel=Irrelevant | IsSup=No
    passage: 上海是中国的经济金融中心 ...
[IsUse] = 5/5
最终答案：...
```

---

## 自测清单

- [ ] 能解释为什么 `Retrieve = No` 这条分支重要（避免对常识题做无用检索）
- [ ] 能说出 `IsRel` 与 `IsSup` 的区别（前者看段落 vs 问题，后者看答案 vs 段落）
- [ ] 能说出 Self-RAG 与 CRAG 的本质差异（自评 vs 纠错）
- [ ] 能指出本 demo 与原论文的差距（prompt 模拟 vs 微调反思 token）

---

## 进一步阅读

- 原论文：[Self-RAG (Asai et al., 2023)](https://arxiv.org/abs/2310.11511)
- 官方代码：<https://github.com/AkariAsai/self-rag>
- 仓库内相关实现：[`../CRAG/`](../CRAG/)、[`../AgenticRAG/`](../AgenticRAG/)
- 仓库内范式总览：[`../../RAG范式总览.md`](../../RAG范式总览.md)

---

**作者**: Beamus Wayne
**最后更新**: 2026-04-29
