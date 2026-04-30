# RAG 学习与实践项目

本项目为 **RAG（Retrieval-Augmented Generation，检索增强生成）** 的完整学习与实践仓库，覆盖从基础概念到生产级应用的完整技术栈，并包含多框架 Agent、图式工作流与实验性 RAG 改进（如 CRAG、GraphRAG、Agentic RAG）。

> **新增**: [MultiLevelRAG](Projects/MultiLevelRAG/) — 意图路由 × 5 种 RAG 策略 × Streamlit 对比平台（MiniMax-M2.5 驱动）
>
> **新增文档**: [RAG 技术范式总览](RAG-Techniques/RAG范式总览.md) — 面向初学者梳理 Naive RAG、CRAG、GraphRAG、Agentic RAG、RAPTOR、HyDE、RAG-Fusion 等主流 RAG 范式。
>
> **新增工程前置课**: [RAG Primer](Foundations/RAG-Primer/) — 切分 / 向量化 / 召回 / 重排 / 评估 9 大模块 + [新手 4 周教程](Foundations/RAG-Primer/TUTORIAL.md)。

---

## 目录

- [项目结构](#项目结构)
- [核心项目](#核心项目)
  - [MultiLevelRAG（新）](#1-multilevelrag新)
  - [Self-RAG（新）](#2-self-rag新)
  - [AgenticRAG](#3-agenticrag)
  - [HyDE](#4-hyde)
  - [RAGFusion](#5-ragfusion)
  - [LangChain_RAG_Proj](#6-langchain_rag_proj推荐入门)
  - [LangChain_Tutorial_Fast](#7-langchain_tutorial_fast)
  - [LangGraph](#8-langgraph)
  - [PydanticAI](#9-pydanticai)
  - [PydanticGraph](#10-pydanticgraph)
  - [Agents（多模态）](#11-agents多模态-agent)
  - [Agno](#12-agno)
  - [Experiment（实验与场景）](#13-experiment实验与场景)
- [技术栈](#技术栈)
- [安装与环境配置](#安装与环境配置)
- [学习路径与快速开始](#学习路径与快速开始)
- [文档资源](#文档资源)

---

## 项目结构

```
RAG-learning/
├── Foundations/               # 阶段一：基础入门
│   └── LangChain_Tutorial_Fast/   # LangChain 31 个循序渐进示例
├── Frameworks/                # 阶段二：框架学习（平行，无强制顺序）
│   ├── LangGraph/
│   ├── PydanticAI/
│   ├── PydanticGraph/
│   ├── Agno/
│   └── Agents/
├── RAG-Techniques/            # 阶段三：RAG 改进技术
│   ├── RAG范式总览.md          # 初学者友好的 RAG 架构范式速查
│   ├── Basic/
│   │   ├── HyDE/              # Hypothetical Document Embeddings
│   │   └── RAGFusion/         # 查询扩展 + RRF 融合检索
│   └── Advanced/
│       ├── AgenticRAG/        # 自主决策检索（多步推理）
│       ├── CRAG/              # 纠正式 RAG
│       └── Self-RAG/          # 反思式 RAG（Retrieve / IsRel / IsSup / IsUse）
├── Projects/                  # 阶段四：生产级完整项目
│   ├── LangChain_RAG_Proj/
│   └── MultiLevelRAG/         # 意图路由 × 5 种 RAG 策略 × Streamlit 对比平台
├── Experiment/                # 实验与场景
│   ├── graph-rag-agent/
│   ├── VideoCut/
│   ├── LongRuiGame/
│   ├── Obsidian/
│   ├── NanoBat/
│   └── Datawhale-LLM/
├── Archive/                   # 历史代码归档
├── Data/                      # 测试数据
├── pyproject.toml
└── requirements.txt
```

---

## 核心项目

### 1. MultiLevelRAG（新）

**[Projects/MultiLevelRAG/](Projects/MultiLevelRAG/)** — 意图感知路由 × 五种 RAG 策略 × Streamlit 交互对比平台。LLM 自动识别问题类型并分配最合适的策略，支持全策略并行对比。

| 策略 | 说明 |
|---|---|
| Baseline RAG | 向量检索 → 上下文拼接 → LLM 生成 |
| HyDE RAG | 先生成假设文档再做向量检索 |
| RAG Fusion | 多查询扩展 + RRF 融合排名 |
| CRAG | 检索结果纠正与精炼 |
| GraphRAG | NetworkX 轻量知识图谱（无需 Neo4j） |

```bash
cd Projects/MultiLevelRAG
streamlit run app.py
```

详见 [Projects/MultiLevelRAG/README.md](Projects/MultiLevelRAG/README.md)。

---

### 2. Self-RAG（新）

**[RAG-Techniques/Advanced/Self-RAG/](RAG-Techniques/Advanced/Self-RAG/)** — 反思式 RAG。模型在回答过程中**自己决定是否检索（Retrieve）**、**逐段判定相关性（IsRel）**、**判定答案是否被段落支持（IsSup）**、**给整体答案打分（IsUse）**，显著降低幻觉。

| 文件 | 说明 |
|---|---|
| [demo.py](RAG-Techniques/Advanced/Self-RAG/demo.py) | 四个反思决策点的最小教学实现，输出完整反思轨迹 |
| [README.md](RAG-Techniques/Advanced/Self-RAG/README.md) | 原理、流程图、与 CRAG/AgenticRAG 对比、自测清单 |

```bash
cd RAG-Techniques/Advanced/Self-RAG
uv run python demo.py
```

> 论文：Asai et al., 2023. *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.* [arXiv:2310.11511](https://arxiv.org/abs/2310.11511)

---

### 3. AgenticRAG

**[RAG-Techniques/Advanced/AgenticRAG/](RAG-Techniques/Advanced/AgenticRAG/)** — Agentic RAG 学习目录，探索让模型在多步推理中自主决定何时检索、检索什么、如何修正答案。

| 文件 | 说明 |
|---|---|
| [demo.py](RAG-Techniques/Advanced/AgenticRAG/demo.py) | MVP 示例：DashScope `text-embedding-v1` + `gpt-5.4`，自建向量库，单轮 Agentic 推理 |
| [AgenticRAG论文汇总.md](RAG-Techniques/Advanced/AgenticRAG/AgenticRAG论文汇总.md) | 核心论文（Self-RAG、CRAG、IRCoT 等）整理与解读 |
| [README.md](RAG-Techniques/Advanced/AgenticRAG/README.md) | 概念对比、学习路径、核心概念速查、自测清单 |

```bash
# 配置网关与密钥后直接运行
cd RAG-Techniques/Advanced/AgenticRAG
uv run python demo.py
```

---

### 4. HyDE（Hypothetical Document Embeddings）

**[RAG-Techniques/Basic/HyDE/](RAG-Techniques/Basic/HyDE/)** — 让 LLM 先生成一篇「假设文档」，再用该文档的向量做检索，从而缩小 query 与 passage 之间的语义鸿沟。

| 文件 | 说明 |
|---|---|
| [demo.py](RAG-Techniques/Basic/HyDE/demo.py) | HyDE 完整示例 |
| [README.md](RAG-Techniques/Basic/HyDE/README.md) | 原理说明与使用方式 |

```bash
cd RAG-Techniques/Basic/HyDE
python demo.py
```

---

### 5. RAGFusion

**[RAG-Techniques/Basic/RAGFusion/](RAG-Techniques/Basic/RAGFusion/)** — 通过查询扩展生成多个子查询，多路检索后用 RRF（Reciprocal Rank Fusion）算法融合排名，提升召回质量。

| 文件 | 说明 |
|---|---|
| [01_query_expansion.py](RAG-Techniques/Basic/RAGFusion/01_query_expansion.py) | 查询扩展 |
| [02_rrf_algorithm.py](RAG-Techniques/Basic/RAGFusion/02_rrf_algorithm.py) | RRF 算法实现 |
| [03_rag_fusion_pipeline.py](RAG-Techniques/Basic/RAGFusion/03_rag_fusion_pipeline.py) | 完整 pipeline |
| [04_comparison.py](RAG-Techniques/Basic/RAGFusion/04_comparison.py) | 与朴素 RAG 对比 |
| [README.md](RAG-Techniques/Basic/RAGFusion/README.md) | 原理说明 |

```bash
cd RAG-Techniques/Basic/RAGFusion
python 01_query_expansion.py
```

---

### 6. LangChain_RAG_Proj（推荐入门）

企业级 RAG 应用，包含知识库管理（上传、向量化、去重）、智能问答（RAG + 对话历史）、Streamlit Web 界面与持久化存储。

```bash
cd Projects/LangChain_RAG_Proj
streamlit run app_qa.py
streamlit run app_file_uploader.py   # 知识库上传
```

详见 [Projects/LangChain_RAG_Proj/README.md](Projects/LangChain_RAG_Proj/README.md)。

---

### 7. LangChain_Tutorial_Fast

31 个循序渐进示例：

| 编号 | 内容 |
|---|---|
| 01–10 | 基础 LLM / Embedding / 模型接入 |
| 11–16 | Prompt 模板与 Chat 模型 |
| 17–20 | Chain 与输出解析器 |
| 21–23 | 对话历史与记忆 |
| 24–31 | 完整 RAG 流程（文档加载、分块、向量检索） |

```bash
cd Foundations/LangChain_Tutorial_Fast
python 01_LLM.py
```

---

### 8. LangGraph

图式编程示例，分两个层次：

**基础练习**（根目录，`00–06_*.py`）：

| 文件 | 说明 |
|---|---|
| `00_HelloWorld_Graph.py` | 最小图 Hello World |
| `02_Multi_Inputs.py` / `04_Multi_Inputs.py` | 多输入图 |
| `05_ConditionalGraph.py` | 条件边 |
| `06_LoopingGraph.py` | 循环图 |

**官方教程**（[Offcial_Tutorial/](Frameworks/LangGraph/Offcial_Tutorial/)，`00–09_*.py`）：

| 文件 | 说明 |
|---|---|
| `00_quickstart.py` | 快速开始 |
| `01_StructedOutputSchema.py` | 结构化输出 |
| `02_Parallelization.py` | 并行节点 |
| `03_Routing.py` | 动态路由 |
| `04_Orchestrator.py` / `05_Orchestrator2.py` | 编排器模式 |
| `05_Evaluator-optimizer.py` | 评估器 + 优化器 |
| `06_Agents.py` | Agent 节点 |
| `07/08_PersonalAssistants*.py` | 个人助手（OpenAI / Ollama） |
| `09_CustomRAG.py` | 自定义 RAG 图 |

**归档课程**（[Archive/LangGraph-Course-freeCodeCamp/](Frameworks/LangGraph/Archive/LangGraph-Course-freeCodeCamp/)）：freeCodeCamp LangGraph 完整课程，含 Agents、练习 Notebooks 与 Graphs。

---

### 9. PydanticAI

类型安全 AI 应用框架实践：入门与模型接入、多工具 Agent、结构化输出与流式、ChatApp、BankSupport、SQL 生成与 RAG（pgvector）、AG-UI、复杂工作流。

详见 [Frameworks/PydanticAI/README.md](Frameworks/PydanticAI/README.md)。

---

### 10. PydanticGraph

图式状态机与 DAG：售货机、邮件反馈、问答图、Mermaid 图导出。

```bash
cd Frameworks/PydanticGraph
python vending_machine.py
```

---

### 11. Agents（多模态 Agent）

基于 Agno 的多模态 Agent（Streamlit），支持 Gemini、Ollama，处理视频、图像与文本。

---

### 12. Agno

Agno 框架入门与助手型 Agent：

- `00_Get_Started/`：HelloAgno、Learning、SQLite 持久化、Agentic / CrossUser
- `01_Assist_Agent/`：助手型 Agent

```bash
cd Frameworks/Agno/00_Get_Started
python 00_HelloAgno.py
```

---

### 13. Experiment（实验与场景）

| 子目录 | 说明 | 文档 |
|---|---|---|
| **graph-rag-agent/** | GraphRAG + DeepSearch 多 Agent 问答：知识图谱、多级检索、Plan-Execute-Report、Neo4j、FastAPI + Streamlit | [readme.md](Experiment/graph-rag-agent/readme.md) |
| **CRAG/** | 纠正式 RAG：检索评估 → Correct / Incorrect / Ambiguous → 知识精炼或网络搜索；FastAPI + Streamlit，MinerU PDF | [README.md](RAG-Techniques/Advanced/CRAG/README.md) |
| **VideoCut/** | 智能视频合成与防重复：LangGraph 状态图、分镜脚本（YAML）、素材库、FFmpeg | [README.md](Experiment/VideoCut/README.md) |
| **LongRuiGame/** | 游戏玩家智能问答：RAG（game_faq.json）+ 工具调用、模糊问题反问、问答日志 | [README.md](Experiment/LongRuiGame/README.md) |
| **Obsidian/** | Obsidian 知识库：LlamaIndex + Ollama（qwen3-vl / qwen3-embedding），增量索引与本地问答 | — |
| **NanoBat/** | Qwen 驱动轻量助手：通义千问 API，单进程 CLI，可扩展技能（Skills），SQLite 记忆 | [README.md](Experiment/NanoBat/README.md) |
| **Batnet.py** | 终端 Matrix 风格动态网络可视化演示（纯 Python，ANSI） | — |

---

## 技术栈

| 类别 | 技术 |
|---|---|
| **框架** | LangChain、LangGraph、PydanticAI、Pydantic Graph、Agno、LlamaIndex |
| **LLM** | OpenAI（gpt-5.4）、Ollama（qwen3、qwen3-vl）、阿里云百炼（DashScope）、Google Gemini |
| **Embedding** | DashScope `text-embedding-v1`、Ollama `qwen3-embedding:4b`、OpenAI `text-embedding-ada-002` |
| **向量/存储** | Chroma、pgvector、InMemoryVectorStore、自建 NumPy 向量库 |
| **Web / 服务** | Streamlit、FastAPI |
| **图数据库** | Neo4j（graph-rag-agent） |
| **其他** | MinerU（PDF）、FFmpeg（VideoCut）、SQLite（NanoBat / Agno 记忆） |
| **包管理** | `uv`（推荐） / `pip` |

---

## 安装与环境配置

### 使用 uv（推荐）

```bash
# 在仓库根目录
uv sync                      # 按 pyproject.toml 安装所有依赖
uv add <包名>                 # 添加新依赖
uv run python <脚本.py>       # 运行脚本
```

### 使用 pip

```bash
pip install langchain langchain-community langchain-openai langchain-text-splitters langgraph
pip install streamlit pydantic-ai pydantic-graph
pip install openai dashscope langchain-ollama llama-index
pip install pypdf python-docx agno numpy
```

> 子项目独立依赖见各目录的 `requirements.txt`（CRAG、VideoCut、graph-rag-agent、NanoBat 等）。

### 环境变量

| 用途 | 变量 | 说明 |
|---|---|---|
| 阿里云百炼 | `DASHSCOPE_API_KEY` | DashScope 模型（通义千问、Embedding） |
| OpenAI / 兼容网关 | `OPENAI_API_KEY` | GPT 系列；可配合 `OPENAI_BASE_URL` 使用第三方网关 |
| Ollama | 无需 Key | 本地 `http://localhost:11434`，需先 `ollama pull <model>` |
| Gemini | 应用内或环境变量配置 | 多模态示例 |

### Ollama 常用模型

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:4b   # 向量化
ollama pull qwen3-vl:4b          # 多模态（可选）
```

---

## 学习路径与快速开始

### 推荐路径

```
RAG-Techniques/RAG范式总览.md（先理解 RAG 范式地图）
       ↓
Foundations/LangChain_Tutorial_Fast (01→31)
       ↓
Projects/LangChain_RAG_Proj（生产级 RAG）
       ↓
Frameworks/LangGraph/Offcial_Tutorial (00→09)
       ↓
RAG-Techniques/Basic/HyDE
RAG-Techniques/Basic/RAGFusion
       ↓
RAG-Techniques/Advanced/AgenticRAG
RAG-Techniques/Advanced/CRAG
RAG-Techniques/Advanced/Self-RAG
       ↓
Projects/MultiLevelRAG（多策略路由 + 全策略并行对比）
       ↓
Frameworks/PydanticAI / Frameworks/Agno（多框架对比）
       ↓
Experiment/*（实验项目）
```

### 快速启动命令

| 目标 | 命令 |
|---|---|
| LangChain 教程 | `cd Foundations/LangChain_Tutorial_Fast && python 01_LLM.py` |
| RAG 问答 Web | `cd Projects/LangChain_RAG_Proj && streamlit run app_qa.py` |
| MultiLevelRAG 平台 | `cd Projects/MultiLevelRAG && streamlit run app.py` |
| LangGraph 基础 | `cd Frameworks/LangGraph && python 00_HelloWorld_Graph.py` |
| LangGraph 官方教程 | `cd Frameworks/LangGraph/Offcial_Tutorial && python 00_quickstart.py` |
| AgenticRAG Demo | `cd RAG-Techniques/Advanced/AgenticRAG && uv run python demo.py` |
| Self-RAG Demo | `cd RAG-Techniques/Advanced/Self-RAG && uv run python demo.py` |
| HyDE Demo | `cd RAG-Techniques/Basic/HyDE && python demo.py` |
| RAGFusion | `cd RAG-Techniques/Basic/RAGFusion && python 01_query_expansion.py` |
| PydanticAI | `cd Frameworks/PydanticAI/00_Preparation && python HelloPydanticAI.py` |
| PydanticGraph | `cd Frameworks/PydanticGraph && python vending_machine.py` |
| Agno | `cd Frameworks/Agno/00_Get_Started && python 00_HelloAgno.py` |
| CRAG | `cd RAG-Techniques/Advanced/CRAG && streamlit run app_streamlit.py` |
| graph-rag-agent | `cd Experiment/graph-rag-agent && uvicorn server.main:app --reload`（不变） |
| VideoCut | `cd Experiment/VideoCut && uvicorn api.main:app --reload`（不变） |
| LongRuiGame 问答 | `cd Experiment/LongRuiGame/scene1_player_qa && python player_qa_agent.py`（不变） |
| Obsidian 知识库 | 修改 vault 路径 → `python Experiment/Obsidian/obsidian_loader.py`（不变） |
| NanoBat 助手 | `cd Experiment/NanoBat && cp .env.example .env`（不变） |
| Batnet 演示 | `python Experiment/Batnet.py`（不变） |

---

## 文档资源

### 子项目文档

| 项目 | 文档 |
|---|---|
| RAG 技术范式总览 | [RAG-Techniques/RAG范式总览.md](RAG-Techniques/RAG范式总览.md) |
| MultiLevelRAG | [Projects/MultiLevelRAG/README.md](Projects/MultiLevelRAG/README.md) |
| Self-RAG | [RAG-Techniques/Advanced/Self-RAG/README.md](RAG-Techniques/Advanced/Self-RAG/README.md) |
| AgenticRAG | [RAG-Techniques/Advanced/AgenticRAG/README.md](RAG-Techniques/Advanced/AgenticRAG/README.md) |
| HyDE | [RAG-Techniques/Basic/HyDE/README.md](RAG-Techniques/Basic/HyDE/README.md) |
| RAGFusion | [RAG-Techniques/Basic/RAGFusion/README.md](RAG-Techniques/Basic/RAGFusion/README.md) |
| LangChain_RAG_Proj | [Projects/LangChain_RAG_Proj/README.md](Projects/LangChain_RAG_Proj/README.md) |
| PydanticAI | [Frameworks/PydanticAI/README.md](Frameworks/PydanticAI/README.md) |
| CRAG | [RAG-Techniques/Advanced/CRAG/README.md](RAG-Techniques/Advanced/CRAG/README.md) |
| graph-rag-agent | [Experiment/graph-rag-agent/readme.md](Experiment/graph-rag-agent/readme.md) |
| VideoCut | [Experiment/VideoCut/README.md](Experiment/VideoCut/README.md) |
| LongRuiGame | [Experiment/LongRuiGame/README.md](Experiment/LongRuiGame/README.md) |
| NanoBat | [Experiment/NanoBat/README.md](Experiment/NanoBat/README.md) |
| LangGraph freeCodeCamp | [Frameworks/LangGraph/Archive/LangGraph-Course-freeCodeCamp/README.md](Frameworks/LangGraph/Archive/LangGraph-Course-freeCodeCamp/README.md) |

### 官方文档

| 框架 | 链接 |
|---|---|
| LangChain | [python.langchain.com](https://python.langchain.com) |
| LangGraph | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph) |
| PydanticAI | [ai.pydantic.dev](https://ai.pydantic.dev) |
| Agno | [docs.agno.com](https://docs.agno.com) |
| LlamaIndex | [docs.llamaindex.ai](https://docs.llamaindex.ai) |
| OpenAI | [platform.openai.com/docs](https://platform.openai.com/docs) |
| DashScope | [help.aliyun.com/zh/dashscope](https://help.aliyun.com/zh/dashscope) |

---

## 贡献与许可

欢迎提交 Issue 与 Pull Request。本项目仅用于学习与研究。

**作者**: Beamus Wayne  
**最后更新**: 2026-04-29
