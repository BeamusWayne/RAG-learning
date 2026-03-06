# 机试准备资料总览

本目录为「游戏行业 AI Agent 开发工程师」五场景机试提供现成语料、数据集与工具函数模板，候选人无需自行爬取或从零构建基础素材。请先阅读本页与 [环境与依赖说明](docs/env_and_deps.md)。

## 使用方式

- 5 个场景任选 1 个完成，限时 30 分钟。
- 进入对应场景目录后：语料/数据在 `corpus/`、`data/`、`assets/`，工具在 `tools/`。可直接复制或引用到你的 Agent 代码中。
- 交付物：Agent 核心代码（.py）+ 测试结果日志 + 50 字内设计思路说明。

## 目录与文件清单

| 场景 | 目录 | 语料/数据 | 工具 |
|------|------|-----------|------|
| 场景一：玩家智能问答助手 | `scene1_player_qa/` | `corpus/game_faq.json` | `tools/tool_templates.py`（2 个工具） |
| 场景二：运营任务自动化 | `scene2_ops_automation/` | 无 | `tools/ops_tools.py`（3 个工具） |
| 场景三：运营数据分析 | `scene3_ops_analytics/` | `data/daily_ops_sample.csv` | `tools/analysis_tools.py`（3 个工具） |
| 场景四：素材库智能管理 | `scene4_asset_mgmt/` | `assets/materials.json` | `tools/asset_tools.py`（3 个工具） |
| 场景五：RPA+Agent 融合 | `scene5_rpa_agent/` | `README.md`（参数约定与示例） | `tools/rpa_tools.py`（3 个工具） |

## 环境要求

- Python 3.x
- LangChain / LangGraph、Pandas、OpenAI/Qwen 等（与机试说明页「通用前置条件」一致；机试环境无 Redis，场景二记忆请用内存或本地存储实现）
- 详细依赖与版本见 [docs/env_and_deps.md](docs/env_and_deps.md)

## 各场景资料说明

- **场景一**：`game_faq.json` 为游戏 FAQ 语料（玩法/道具/技能/活动）；`tool_templates.py` 提供 `query_item`、`query_event_or_skill`，供 RAG 无匹配时调用。
- **场景二**：`ops_tools.py` 提供 `check_servers`、`get_complaint_stats`、`sync_to_sheet`，用于 ReAct 编排与异常处理（如服务器异常时跳过后续）。
- **场景三**：`daily_ops_sample.csv` 为日运营样例（dau、留存、充值、关卡通过率等）；`analysis_tools.py` 提供加载清洗、分析统计、格式化总结。
- **场景四**：`materials.json` 为剧情/道具/活动轻量素材；`asset_tools.py` 提供分类清洗、标引、检索（含 mock 检索接口，可做 RAG 轻量优化）。
- **场景五**：`README.md` 提供工具参数约定与自然语言→参数示例；`rpa_tools.py` 提供 `sync_data`、`export_report`、`mark_issues`，用于 RPA+Agent 融合与异常处理考察。

以上资料均为模拟/样例，不依赖真实游戏后台或外部 API。
