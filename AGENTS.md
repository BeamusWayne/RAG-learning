# AGENTS.md

> 本文件供 Claude Code、Codex、Cursor 等 AI 编码助手阅读，用于快速理解仓库形态、约定与协作规范。
> 人类读者请优先阅读 [README.md](./README.md)。

---

## 1. 项目定位

`RAG-learning` 是一个 **RAG 学习与实践仓库**，不是单一可部署的产品，而是 **多个独立子项目**（教程 / 技术演示 / 实验）的合集。

- 主语言：Python ≥ 3.12
- 包管理：`uv`（首选） / `pip`（回退）
- 主要场景：检索增强生成（RAG）、Agent 框架对比、图式工作流、知识图谱、多模态实验
- 重要：**每个子目录可以独立运行**，不要假设跨子项目的导入或共享状态

---

## 2. 仓库地图（必读）

```
RAG-learning/
├── Foundations/         # 阶段一：入门
│   ├── RAG-Primer/          # 9 模块工程前置课（Loading→Chunking→...→Pitfalls）
│   └── LangChain_Tutorial_Fast/   # 31 个 LangChain 循序示例
├── Frameworks/          # 阶段二：框架（平行学习）
│   ├── LangGraph/  PydanticAI/  PydanticGraph/  Agno/  Agents/
├── RAG-Techniques/      # 阶段三：RAG 改进技术
│   ├── RAG范式总览.md
│   ├── Basic/{HyDE, RAGFusion}
│   └── Advanced/{AgenticRAG, CRAG, Self-RAG}
├── Projects/            # 阶段四：生产级项目
│   ├── LangChain_RAG_Proj/      # Streamlit 知识库 + 问答
│   └── MultiLevelRAG/           # 意图路由 × 5 策略对比平台
├── Experiment/          # 实验项目（graph-rag-agent / VideoCut / LongRuiGame / Obsidian / NanoBat）
├── Archive/             # 历史归档，不要修改
├── Data/                # 测试数据
├── pyproject.toml       # 仓库根 uv 依赖
└── requirements.txt
```

子项目可能有自己的 `requirements.txt` / `.env.example` / `README.md`，**优先尊重子项目内的约定**。

---

## 3. 运行环境与命令

### 依赖安装
```bash
uv sync                            # 首选
pip install -r requirements.txt    # 回退
```

### 运行单个脚本
```bash
uv run python <path/to/script.py>     # 推荐
python <path/to/script.py>            # 也可
```

### Streamlit 应用
```bash
cd Projects/MultiLevelRAG && streamlit run app.py
cd Projects/LangChain_RAG_Proj && streamlit run app_qa.py
```

### 子项目 FastAPI（仅参考）
```bash
cd Experiment/graph-rag-agent && uvicorn server.main:app --reload
cd Experiment/VideoCut && uvicorn api.main:app --reload
```

---

## 4. 环境变量

**永远不要把密钥写进代码或提交到 git**。本仓库使用 `.env`（已在 `.gitignore` 中）。

| 变量 | 用途 |
|---|---|
| `DASHSCOPE_API_KEY` | 阿里云百炼（通义千问、`text-embedding-v1`） |
| `OPENAI_API_KEY` | OpenAI / 兼容网关 |
| `OPENAI_BASE_URL` | 第三方网关地址（可选） |

Ollama 本地模型无需 Key，需先 `ollama pull qwen3:4b` / `qwen3-embedding:4b` 等。

---

## 5. AI Agent 工作约定

### 写代码时
- **教学优先**：本仓库以学习为目的，代码倾向 **可读 > 极致工程化**。不要把示例脚本"重构"成抽象框架。
- **不跨子项目重构**：修改 `Foundations/RAG-Primer/02-Chunking/demo.py` 不要顺手改 `RAG-Techniques/Basic/HyDE/demo.py`。
- **保留教学注释**：示例文件里中文注释通常承载教学意图，不要以"代码自解释"为由删掉。
- **新示例放正确目录**：
  - 入门示例 → `Foundations/`
  - RAG 改进算法 → `RAG-Techniques/Basic/` 或 `Advanced/`
  - 生产级完整应用 → `Projects/`
  - 一次性实验 / 玩具 → `Experiment/`
- **`Archive/` 只读**，除非用户明确要求。

### 改文件时
- 新增 RAG 技术目录时，**同步更新** [README.md](./README.md) 的目录、核心项目、快速启动命令、文档资源四个区块，以及 [RAG-Techniques/RAG范式总览.md](./RAG-Techniques/RAG范式总览.md)。
- 子项目 `README.md` 的更新与根 `README.md` 是 **两件事**，需要分别处理。
- 中文文档为主，新增文档遵循已有的中文风格与节制使用 emoji 的习惯。

### 跑命令时
- 不要在仓库根目录运行任何子项目内部脚本，**先 `cd` 到对应子目录**。
- 不要随意 `uv add` / `pip install` 全局依赖；多数场景应该在子项目的 `requirements.txt` 或 `pyproject.toml` 中维护。

---

## 6. 常见任务与入口

| 任务 | 入口 |
|---|---|
| 新加 RAG 技术演示 | `RAG-Techniques/{Basic,Advanced}/<NewTech>/{demo.py, README.md}` |
| 想测试某个 LLM/Embedding 是否可用 | `Foundations/LangChain_Tutorial_Fast/01_LLM.py` 或 `04_Embedding/` |
| 看 RAG 全景图 | [RAG-Techniques/RAG范式总览.md](./RAG-Techniques/RAG范式总览.md) |
| 入门 9 步法 | [Foundations/RAG-Primer/TUTORIAL.md](./Foundations/RAG-Primer/TUTORIAL.md) |
| 多策略对比平台 | `Projects/MultiLevelRAG/app.py` |

---

## 7. 提交规范

提交信息使用 **中文 + Conventional Commits**：

```
feat: 新增 Self-RAG 反思式 RAG 模块
docs: 同步 MultiLevelRAG 至 README 主目录与学习路径
fix: 修正 RAGFusion RRF 分母计算
```

类型：`feat` / `fix` / `docs` / `refactor` / `test` / `chore` / `perf`。

PR 前自检：
- [ ] 没有把 `.env` / 密钥 / 本地数据库文件加进 git
- [ ] 子项目 README 与根 README 同步
- [ ] `uv run python <新脚本>` 至少在本地跑通过
- [ ] 中文文档没有半角 / 全角混乱、链接没有死链

---

## 8. 不要做的事

- 修改 `Archive/` 下的内容
- 在示例脚本里硬编码 API Key
- 把 `Experiment/` 下的玩具实验当作生产代码去抽象
- 跨子项目引入循环依赖或共享 `__init__.py`
- 用全局 `pip install -U` 覆盖 `pyproject.toml` 锁定的版本

---

## 9. 参考

- 顶层说明：[README.md](./README.md)
- RAG 范式速查：[RAG-Techniques/RAG范式总览.md](./RAG-Techniques/RAG范式总览.md)
- 入门教程：[Foundations/RAG-Primer/TUTORIAL.md](./Foundations/RAG-Primer/TUTORIAL.md)
