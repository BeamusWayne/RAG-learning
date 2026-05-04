# 进度日志

## 当前已验证状态

- 仓库根目录：`/Users/katya/Files/RAG-learning`
- 标准启动路径：`source .venv/bin/activate && uv sync`
- 标准验证路径：`python <module>/demo.py` 或 Streamlit `streamlit run app.py`
- 当前最高优先级未完成功能：无（所有现有模块已就位）
- 当前 blocker：无

## 仓库总览

### Foundations（基础）
| 模块 | 状态 | 说明 |
|------|------|------|
| RAG-Primer（9 子模块） | passing | 01-Loading 到 09-Pitfalls，骨架 demo 就位 |
| LangChain_Tutorial_Fast | passing | 33 个 LangChain 循序渐进示例 |

### RAG-Techniques（RAG 改进技术）
| 模块 | 状态 | 说明 |
|------|------|------|
| Basic/HyDE | passing | demo.py 可运行 |
| Basic/RAGFusion | passing | 4 个渐进式脚本 |
| Advanced/CRAG | passing | 完整 Streamlit 项目 |
| Advanced/Self-RAG | passing | demo.py 可运行 |
| Advanced/AgenticRAG | passing | demo.py + 论文汇总 |

### Projects（完整项目）
| 模块 | 状态 | 说明 |
|------|------|------|
| LangChain_RAG_Proj | passing | 知识库 QA + 文件上传 |
| MultiLevelRAG | passing | 意图路由 x 5 策略对比平台 |

### Frameworks（框架学习）
| 模块 | 状态 | 说明 |
|------|------|------|
| LangGraph | passing | 基础图 + 官方教程 |
| PydanticAI | passing | 7 个子目录 |
| PydanticGraph | passing | 6 个示例 |
| Agno | passing | 入门 + Assist Agent |
| Agents | passing | 多模态 Agent |

### Experiment（实验项目）
| 模块 | 状态 | 说明 |
|------|------|------|
| graph-rag-agent | passing | 生产级 GraphRAG（Neo4j） |
| NanoBat | passing | 轻量 Agent |
| VideoCut | passing | 视频剪辑 Agent |
| Obsidian | passing | 笔记 Agent |
| LongRuiGame | passing | 游戏场景 Agent |

## 会话记录

### Session 001 — 2026-04-25 ~ 2026-04-30
- 本轮目标：仓库重组、多模块新增
- 已完成：目录重组、HyDE/RAGFusion/CRAG/Self-RAG/AgenticRAG/MultiLevelRAG/RAG-Primer 新增、LangChain/PydanticAI/LangGraph 等框架学习目录就位
- 提交记录：e2a8a66, 7620df8, 096fe97, e307099, 77627fc, 762cd2f
- 下一步最佳动作：为各 demo.py 补充更丰富的示例内容，或新增 RAG 范式（如 RAPTOR、GraphRAG 进阶）

### Session 002 — 2026-05-02
- 本轮目标：抽取 RAG-Primer _common.py + 新增 AGENTS.md + 清理 graph-rag-agent
- 已完成：RAG-Primer 9 模块抽取公共 _common.py、根目录 AGENTS.md、清理 .env 与 .DS_Store
- 提交记录：b1afbeb, ea29b80
- 下一步最佳动作：继续补齐各 demo.py 的实际内容

### Session 003 — 2026-05-04
- 本轮目标：根据仓库现状更新 feature_list.json、claude-progress.md、init.sh
- 已完成：feature_list.json 映射全部 27 个功能模块、claude-progress.md 重写、init.sh 适配 Python 项目
- 更新过的文件：feature_list.json, claude-progress.md, init.sh
- 下一步最佳动作：为具体 demo.py 补充实质性代码内容，或开始新的 RAG 范式实验
