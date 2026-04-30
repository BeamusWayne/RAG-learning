# RAG Primer 新手入门教程

> 给"我刚开始学 RAG，想动手"的人。
> 读完这篇 + 跑通本目录的 demo，你应该能自己解释清楚：
> **一份文档是怎么从硬盘变成 LLM 能用的"知识"的，每一步可能在哪里翻车。**

---

## 0. 你需要先知道什么

读这篇之前，你应该已经会：

- 跑 Python 脚本（会用 `pip` 或 `uv`）
- 知道"向量"和"余弦相似度"大概是什么（不会也没事，第 3 章会讲）
- 用过 ChatGPT / Claude 之类的对话 LLM

不需要：

- 机器学习数学背景
- 深度学习训练经验
- 看过任何 RAG 论文

---

## 1. 一句话讲清楚 RAG

**RAG = Retrieval-Augmented Generation = 让 LLM 答题前先翻书。**

```
你问：       "我们公司去年营收多少？"
LLM 自己：   不知道（训练数据没有）
RAG 怎么做：
  1. 先把"公司年报"切碎、做成向量、存进"知识库"
  2. 收到问题后，从知识库里找出最相关的几段
  3. 把"问题 + 相关段落"一起喂给 LLM
  4. LLM 基于真实文档回答 → 不再瞎编
```

整个流程被分成 9 个"工程动作"——这就是本目录 9 个模块的由来。

---

## 2. 流水线的 9 个动作

```
01-Loading         读 PDF / Markdown / HTML
   ↓                   把文档变成纯文本
02-Chunking        切成 chunk
   ↓                   每段大概 300-500 字
03-Chunking-Eval   验证切得好不好
   ↓                   边界泄漏？语义内聚？召回率？
04-Embedding       每个 chunk 变向量
   ↓                   用 embedding 模型
05-VectorStore     存进向量库
   ↓                   FAISS / Chroma / pgvector
06-Retrieval       查询时找相似的 chunk
   ↓                   向量 + 关键词 + 过滤
07-Reranking       精挑细选 top-K
   ↓                   bge-reranker 等
08-Evaluation      端到端打分
   ↓                   RAGAS：faithfulness / relevancy
09-Pitfalls        翻车清单
                       常见错误 Top 10
```

**你会发现**：90% 的"调 prompt"型 RAG 调优，问题其实在前面这 7 步里。

---

## 3. 三个最关键概念（不能跳）

### 3.1 chunk

> 把长文档切成的"段落卡片"，每张大概 200-800 字，是检索系统的基本单位。

**为什么不是整篇文档？** 因为 embedding 模型对长文本会"信息稀释"——一段同时讲 5 件事，向量也就同时不像那 5 件事。

**为什么不是单句？** 太碎了，召回时没上下文，LLM 看不懂"它指什么"。

### 3.2 embedding

> 把文字变成一串数字（通常 768~1024 个），让"语义相近"对应"数字向量相近"。

```
"如何申请退款"  →  [0.12, -0.84, 0.33, ..., 0.07]
"怎么把钱要回来" →  [0.11, -0.82, 0.31, ..., 0.06]   ← 几乎一样
"今天天气真好"  →  [0.91,  0.45, -0.22, ..., 0.55]   ← 差很远
```

**关键直觉**：余弦相似度 ≈ 看两个向量"指的方向"是否一致。

### 3.3 召回 vs 重排

| 阶段 | 干什么 | 模型类型 | 粗略 |
|---|---|---|---|
| **召回** (retrieval) | 从 10 万条里捞 50 条候选 | 双编码器（快） | 快但糙 |
| **重排** (reranking) | 50 条精排出 5 条 | 交叉编码器（慢） | 慢但准 |

**生产 RAG 系统几乎都是两段式**。

---

## 4. 环境准备

### 4.1 Python 依赖

仓库根的 `requirements.txt` / `pyproject.toml` 已经声明，按你的偏好：

```bash
# 推荐 uv（更快）
uv sync

# 或经典 pip
pip install -r requirements.txt
```

### 4.2 配置 `.env`

仓库根创建 `.env`（已加入 `.gitignore`，不会被推送）：

```bash
# OpenAI 兼容网关（任选其一）
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1

# 或 MiniMax（OpenAI 兼容）
MINIMAX_API_KEY=sk-...
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_CHAT_MODEL=MiniMax-M2

# 或 DashScope（阿里）—— 项目里其他 demo 在用
DASHSCOPE_API_KEY=sk-...

# Ollama 本地（可选，做 fallback）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
```

你**不需要全部都填**，只需要**一个 LLM + 一个 embedding** 即可。

### 4.3 Embedding 选型决策

如果你不知道选哪个，按下面顺序试：

```
1. 你有 OpenAI/DashScope/MiniMax API key 且账户有余额？
   → 直接用云端 embedding，最省事
2. 想完全本地？
   → 装 Ollama，pull nomic-embed-text 或 bge-m3
   （注意：Apple Silicon 老型号 / Ollama 旧版本可能有兼容问题）
3. Ollama 跑不起来？
   → pip install sentence-transformers
   → 直接 Python 加载 BAAI/bge-small-zh-v1.5
   不需要任何外部服务
```

> **本仓库实测**：MiniMax 余额不足时会返回 `status_code=1008`；
> Apple M5 + 旧版 Ollama 会在 ggml Metal 后端 segfault。
> 如果遇到，回到方案 3 是最稳妥的。

---

## 5. 第一次跑一个完整 RAG 是什么体验

不要从头自己写——先跑 [`Foundations/LangChain_Tutorial_Fast/`](../LangChain_Tutorial_Fast/) 里的现成例子，体会"上下游怎么连起来"。

然后回来逐模块拆开看：

### 5.1 推荐学习顺序

```
第 1 周：02-Chunking + 03-Chunking-Eval
        （切分 + 验证切分，是 RAG 工程师的"基础基础"）

第 2 周：04-Embedding + 05-VectorStore
        （选模型 + 索引结构）

第 3 周：06-Retrieval + 07-Reranking
        （混合检索 + 精排）

第 4 周：08-Evaluation
        （没有评估的 RAG 是玄学）

随时翻：09-Pitfalls
        （调不通就先翻这里）
```

### 5.2 每个模块怎么用

每个模块目录下都有：

- `README.md` — 概念、对比表、关键参数、自测清单
- `demo.py` — 最小可运行示例

跑法：

```bash
cd /path/to/RAG-learning
uv run python Foundations/RAG-Primer/02-Chunking/demo.py
```

> 当前 `demo.py` 是**骨架**——会打印模块名和计划清单。
> 真实实现会逐模块补齐，每补一个会更新对应 README 的"计划中的 demo"勾选状态。

---

## 6. 三个一定要做的练习

读懂 = 看懂；**理解 = 能动手解释 + 能找到 bug**。

### 练习 1：切分对比（30 分钟）

随便找一份长 Markdown（比如本仓库的某篇笔记），用 `02-Chunking/demo.py` 跑：

- `chunk_size=200` vs `chunk_size=800`
- `overlap=0` vs `overlap=100`

观察：哪种切法让"日期 + 数字 + 单位"这种关键信息最不容易被劈开？

### 练习 2：观察 BM25 在中文上的表现（20 分钟）

`06-Retrieval/demo.py` 里把同一个 query 分别走 dense / BM25：

- "公司 2023 年度净利润"
- "公司去年赚了多少钱"

哪个 query BM25 强？哪个 dense 强？为什么？这就是 hybrid 检索存在的原因。

### 练习 3：故意搞坏然后修好（45 分钟）

按 `09-Pitfalls/README.md` 里 Top 10 的任意一条，**主动制造**这个错误（比如把 chunk_size 调到 2000），观察召回质量怎么崩，然后修回来。

亲手把系统弄坏一次，比看 10 篇论文都记得牢。

---

## 7. 常见困惑

**Q: 我必须懂 transformer 的数学才能做 RAG 吗？**
不必。会调 API、能看懂"向量近 = 语义近"就够入门。原理可以反过来从工程实践里慢慢补。

**Q: 我应该自己微调 embedding 模型吗？**
**先不要。** 90% 的项目，先把切分、混合检索、reranker 做对，效果就上去了。微调成本高、收益不一定明显。

**Q: chunk_size 到底设多少？**
**没有标准答案，必须实测。** 起步范围 300-500 token；用 03-Chunking-Eval 跑一遍，看你的语料的最佳值。

**Q: 一定要用向量库吗？小项目能不能直接 numpy？**
小于 5 万 chunk，numpy + 暴力 cosine 完全够用。向量库是数据量上来才需要的。

**Q: RAG 系统答错了，我应该改 prompt 还是改检索？**
看 [`08-Evaluation/`](08-Evaluation/) 的 RAGAS 4 指标：
- Faithfulness 低 → prompt 问题
- Context Recall 低 → 检索没找到
- Context Precision 低 → 检索找到了但混入太多噪声 → 上 reranker

---

## 8. 下一步去哪

学完本目录后：

| 想学什么 | 去哪 |
|---|---|
| HyDE / RAG-Fusion 等查询改写 | [`../../RAG-Techniques/Basic/`](../../RAG-Techniques/Basic/) |
| Self-RAG / CRAG 反思式 RAG | [`../../RAG-Techniques/Advanced/`](../../RAG-Techniques/Advanced/) |
| Agentic RAG（多步推理） | [`../../RAG-Techniques/Advanced/AgenticRAG/`](../../RAG-Techniques/Advanced/AgenticRAG/) |
| 完整范式地图 | [`../../RAG-Techniques/RAG范式总览.md`](../../RAG-Techniques/RAG范式总览.md) |
| LangChain 工程实战 | [`../LangChain_Tutorial_Fast/`](../LangChain_Tutorial_Fast/) |

---

## 9. 一句话送给你

> **看一万行论文不如把一个最小 RAG 跑通；
> 跑通一个不如亲手把它弄崩、再亲手修好。**

祝学得开心。

---

**作者**: Beamus Wayne
**最后更新**: 2026-04-30
