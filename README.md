# RAG 学习与实践项目

本项目为 **RAG（Retrieval-Augmented Generation，检索增强生成）** 的完整学习与实践仓库，覆盖从基础概念到生产级应用的完整技术栈，并包含多框架 Agent、图式工作流与实验性 RAG 改进（如 CRAG、GraphRAG）。

---

## 目录

- [项目结构](#-项目结构)
- [核心项目](#-核心项目)
- [技术栈](#️-技术栈)
- [安装与配置](#-安装依赖与环境配置)
- [学习路径与快速开始](#-学习路径与快速开始)
- [项目特点与文档资源](#-项目特点与文档资源)

---

## 项目结构

```
RAG/
├── Agents/                    # 多模态 Agent（Agno + Gemini / Ollama）
│   └── multimodal_agent/      # 多模态推理、视频理解等
├── Agno/                      # Agno 框架入门与助手
│   ├── 00_Get_Started/        # HelloAgno、First Agent、Learning、Agentic/CrossUser
│   └── 01_Assist_Agent/       # 助手型 Agent
├── LangChain_Tutorial_Fast/   # LangChain 快速教程（31 个示例）
├── LangChain_RAG_Proj/        # 完整 RAG 项目（生产级）
├── LangGraph/                 # LangGraph 图式编程与练习
├── PydanticAI/                 # PydanticAI 框架实践（Agent、工具、流式、RAG、AG-UI、工作流）
├── PydanticGraph/              # Pydantic Graph 图式工作流（售货机、邮件反馈、问答图）
├── Experiment/                # 实验与场景示例
│   ├── graph-rag-agent/       # GraphRAG + DeepSearch 多 Agent 问答（Neo4j、Plan-Execute-Report）
│   ├── CRAG/                  # 纠正式 RAG（论文实现，FastAPI + Streamlit，MinerU PDF）
│   ├── VideoCut/              # 智能视频合成与防重复（LangGraph、分镜脚本、FFmpeg）
│   ├── LongRuiGame/           # 游戏玩家智能问答（RAG + 工具调用、模糊反问、日志）
│   ├── Obsidian/              # Obsidian 知识库（LlamaIndex + Ollama 增量索引与问答）
│   ├── NanoBat/               # Qwen 驱动轻量助手（参考 NanoClaw，国内友好、通义 API）
│   └── 其他示例               # weather_agent、stream_whales、quantqmt 等
├── Archive/                   # 历史代码归档
└── Data/                      # 测试数据（JSON、TXT）
```

---

## 核心项目

### 1. LangChain_RAG_Proj（推荐入门）

企业级 RAG 应用，包含知识库管理（上传、向量化、去重）、智能问答（RAG + 对话历史）、Streamlit Web 界面与持久化存储。

```bash
cd LangChain_RAG_Proj
streamlit run app_qa.py
streamlit run app_file_uploader.py   # 知识库上传
```

详见 [LangChain_RAG_Proj/README.md](LangChain_RAG_Proj/README.md)。

### 2. LangChain_Tutorial_Fast

31 个示例：01–10 基础 LLM/Embedding，11–16 Prompt 与 Chat 模型，17–20 Chain 与解析器，21–23 对话历史，24–31 完整 RAG 流程（DocumentLoaders、TextSplitter、VectorStores）。

### 3. LangGraph

图式编程示例：Hello World 图、多输入图、课程笔记（Archive）。用于理解状态图、条件边与多节点编排。

### 4. PydanticAI

类型安全 AI 应用：入门与模型接入、多工具 Agent、结构化输出与流式、ChatApp、BankSupport、SQL 生成与 RAG（pgvector）、AG-UI、复杂工作流。详见 [PydanticAI/README.md](PydanticAI/README.md)。

### 5. PydanticGraph

图式状态机与 DAG：售货机、邮件反馈、问答图、Mermaid 图导出。依赖 `pydantic-graph`、`pydantic-ai`、`rich`。

### 6. Agents（多模态 Agent）

基于 Agno 的多模态 Agent（Streamlit），支持 Gemini、Ollama，处理视频、图像与文本。

### 7. Agno

Agno 框架入门与助手型 Agent：Get_Started（HelloAgno、Learning、SQLite 持久化）、Assist_Agent。依赖 `agno`，本地需 Ollama（如 `qwen3-vl:4b`）。

### 8. Experiment（实验与场景）


| 子目录/文件               | 说明                                                                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **graph-rag-agent/** | GraphRAG + DeepSearch 多 Agent 问答：知识图谱增强 RAG、多级检索、Plan-Execute-Report 多智能体、Neo4j、增量更新与评估。FastAPI + Streamlit。详见 [readme.md](Experiment/graph-rag-agent/readme.md)   |
| **CRAG/**            | 纠正式 RAG：检索评估 → Correct/Incorrect/Ambiguous → 知识精炼或网络搜索。FastAPI + Streamlit，MinerU PDF。详见 [README.md](Experiment/CRAG/README.md)                                    |
| **VideoCut/**        | 智能视频合成与防重复：LangGraph 状态图、分镜脚本（YAML）、素材库、FFmpeg、成片查重与重试。详见 [README.md](Experiment/VideoCut/README.md)                                                               |
| **LongRuiGame/**     | 游戏玩家智能问答：RAG（game_faq.json）+ 工具调用（query_item、query_event_or_skill）、模糊问题反问、问答日志。详见 [README.md](Experiment/LongRuiGame/README.md)                                    |
| **Obsidian/**        | Obsidian 知识库：LlamaIndex + Ollama（qwen3-vl / qwen3-embedding），增量索引与本地问答。                                                                                            |
| **NanoBat/**         | **Qwen 驱动轻量助手**：参考 [NanoClaw](https://github.com/qwibitai/nanoclaw)，通义千问 API 驱动、国内友好、单进程 CLI、可扩展技能。详见 [Experiment/NanoBat/README.md](Experiment/NanoBat/README.md) |
| 其他                   | `weather_agent`、`stream_whales`、`quantqmt` 等示例                                                                                                                     |


---

## 技术栈


| 类别         | 技术                                                                      |
| ---------- | ----------------------------------------------------------------------- |
| **框架**     | LangChain、LangGraph、PydanticAI、Pydantic Graph、Agno、LlamaIndex（Obsidian） |
| **LLM**    | OpenAI、Ollama（qwen3、qwen3-embedding、qwen3-vl）、阿里云百炼、Google Gemini       |
| **向量/存储**  | Chroma、pgvector、InMemoryVectorStore                                     |
| **Web/服务** | Streamlit、FastAPI、Gradio                                                |
| **其他**     | MinerU（PDF）、FFmpeg（VideoCut）、Neo4j（graph-rag-agent）                     |


---

## 安装依赖与环境配置

### 安装依赖

```bash
# 核心
pip install langchain langchain-community langchain-chroma langchain-text-splitters langgraph
pip install streamlit pydantic-ai pydantic-graph

# 模型与 Ollama
pip install openai dashscope langchain-ollama

# 文档与可选
pip install pypdf python-docx
pip install agno   # 多模态 Agent
# 子项目依赖见各目录 requirements.txt（CRAG、VideoCut、graph-rag-agent 等）
```

### 环境变量


| 用途     | 变量                  | 说明                                                   |
| ------ | ------------------- | ---------------------------------------------------- |
| 阿里云百炼  | `DASHSCOPE_API_KEY` | 通义模型                                                 |
| OpenAI | `OPENAI_API_KEY`    | GPT 等                                                |
| Ollama | 无需 Key              | 本地 `http://localhost:11434`，需先 `ollama pull <model>` |
| Gemini | 在应用内或环境变量配置         | 多模态示例                                                |


### Ollama 常用模型

```bash
ollama pull qwen3:4b
ollama pull qwen3-embedding:4b    # 向量化
ollama pull qwen3-vl:4b           # 多模态（可选）
```

---

## 学习路径与快速开始

### 初学者

1. **基础**（`LangChain_Tutorial_Fast/01-10`）：LLM、Embedding、Prompt
2. **进阶**（11–23）：Prompt 模板、Chain、对话历史
3. **RAG**（24–31）：文档加载、分块、向量检索、完整 RAG
4. **实战**（`LangChain_RAG_Proj`）：企业级应用与 Web 部署

### 快速启动命令


| 目标               | 命令                                                                                                                          |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 教程示例             | `cd LangChain_Tutorial_Fast && python 01_LLM.py`                                                                            |
| RAG 问答           | `cd LangChain_RAG_Proj && streamlit run app_qa.py`                                                                          |
| PydanticAI       | `cd PydanticAI/00_Preparation && python HelloPydanticAI.py`                                                                 |
| PydanticGraph    | `cd PydanticGraph && python vending_machine.py`                                                                             |
| graph-rag-agent  | `cd Experiment/graph-rag-agent && uvicorn server.main:app --reload`，另开终端 `streamlit run frontend/app.py`                    |
| CRAG             | `cd Experiment/CRAG && uvicorn api:app --host 0.0.0.0 --port 8000` 或 `streamlit run app_streamlit.py`                       |
| VideoCut         | `cd Experiment/VideoCut && uvicorn api.main:app --reload`（需 FFmpeg）                                                         |
| LongRuiGame 玩家问答 | `cd Experiment/LongRuiGame/scene1_player_qa && python player_qa_agent.py`                                                   |
| Obsidian 知识库     | 修改 `Experiment/Obsidian/obsidian_loader.py` 中 vault 路径后运行，再运行 `obsidian_agent.py` 问答（需 Ollama + qwen3-vl + qwen3-embedding） |
| NanoBat（Qwen 助手） | `cd Experiment/NanoBat && pip install -r requirements.txt`，配置 `.env` 中的 `DASHSCOPE_API_KEY` 后 `python main.py`              |
| Agno             | `cd Agno/00_Get_Started && python 00_HelloAgno.py`                                                                          |


---

## 项目特点与文档资源

### 特点概览

- 从入门到生产的完整 RAG 与 Agent 学习路径  
- 多框架：LangChain、LangGraph、PydanticAI、Pydantic Graph、Agno、LlamaIndex  
- 多模型：OpenAI、Ollama、阿里云百炼、Gemini  
- 图式工作流、纠正式 RAG（CRAG）、GraphRAG 多 Agent、游戏问答、Obsidian 知识库、视频合成等实验与场景

### 文档与链接


| 项目                 | 文档                                                                           |
| ------------------ | ---------------------------------------------------------------------------- |
| LangChain_RAG_Proj | [README.md](LangChain_RAG_Proj/README.md)                                    |
| PydanticAI         | [README.md](PydanticAI/README.md)                                            |
| graph-rag-agent    | [readme.md](Experiment/graph-rag-agent/readme.md)                            |
| CRAG               | [README.md](Experiment/CRAG/README.md)                                       |
| VideoCut           | [README.md](Experiment/VideoCut/README.md)                                   |
| LongRuiGame        | `README.md`                                                                  |
| NanoBat            | [README.md](Experiment/NanoBat/README.md)                                    |
| LangChain          | [python.langchain.com](https://python.langchain.com)                         |
| LangGraph          | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph) |
| PydanticAI         | [ai.pydantic.dev](https://ai.pydantic.dev)                                   |


---

## 贡献与许可

欢迎提交 Issue 与 Pull Request。本项目仅用于学习与研究。

**作者**: Beamus Wayne
**最后更新**: 2026-03-05