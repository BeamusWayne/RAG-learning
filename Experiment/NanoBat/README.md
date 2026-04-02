# NanoBat

基于 **Qwen（通义）** 驱动的轻量级个人 AI 助手，参考 [NanoClaw](https://github.com/qwibitai/nanoclaw) 设计，面向**中国大陆**使用场景：无 Claude 依赖，使用阿里云通义千问 API（及可选本地 Ollama 通义模型），单进程、易读易改、可扩展技能。

## 与 NanoClaw 的对比

| 维度 | NanoClaw | NanoBat |
|------|----------|---------|
| 驱动 | Claude Code / Anthropic Agents SDK | **通义千问 API**（DashScope / OpenAI 兼容） |
| 地域 | 依赖 Claude 服务 | **国内友好**：阿里云通义、亦可 Ollama 本地 |
| 语言 | TypeScript / Node.js | Python |
| 架构 | 单进程 + 容器内跑 Agent | 单进程 + 进程内 Agent（可选后续加容器） |
| 技能 | Claude Code Skills（/setup, /add-telegram） | **技能模块**（Python，可插拔） |
| 通道 | WhatsApp / Telegram / Discord 等 | 先 CLI，通道可扩展 |

## 设计原则

- **小到能读懂**：单进程、少量文件，方便阅读与二次开发。
- **国内可用**：默认通义 API，可选 Ollama 本地 qwen，不依赖境外服务。
- **技能即扩展**：新能力通过「技能」挂载，而非往核心堆配置。
- **对话即入口**：以多轮对话为主，可接 CLI / 未来接 IM、Web 等。

## 项目结构

```
NanoBat/
├── README.md           # 本说明
├── requirements.txt    # 依赖
├── .env.example        # 环境变量示例
├── main.py             # 入口（CLI 对话）
├── src/
│   ├── agent.py        # 通义驱动的 Agent（多轮对话）
│   ├── db.py           # 会话/历史（SQLite，可选）
│   └── channels/
│       └── cli.py      # 命令行通道
└── skills/             # 技能目录（可扩展）
    └── README.md       # 技能开发说明
```

## 快速开始

### 1. 安装依赖

```bash
cd Experiment/NanoBat
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写：

```bash
# 通义千问（推荐，国内直连）
DASHSCOPE_API_KEY=sk-xxx

# 可选：使用 OpenAI 兼容端点（如 Ollama 代理、其他国内兼容服务）
# OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
# OPENAI_API_KEY=sk-xxx
```

### 3. 运行

```bash
python main.py
```

进入 CLI 后，输入内容与 Qwen 对话；输入 `exit` 或 `quit` 退出。

## 配置说明

- **通义 API**：在 [阿里云百炼](https://bailian.console.aliyun.com/) 或 DashScope 开通并获取 `DASHSCOPE_API_KEY`，即可在国内直接使用。
- **本地 Ollama**：若使用 Ollama 跑 qwen，需本地起服务并配置为 OpenAI 兼容端点，在 `.env` 中设置 `OPENAI_API_BASE` 与 `OPENAI_API_KEY`（或对应环境变量）。

## 技能扩展

在 `skills/` 下可添加自定义技能模块，由 Agent 在对话中按需调用（如查天气、记待办、读本地文件等）。参见 `skills/README.md`。

## 依赖

- Python 3.10+
- `openai`（通义使用 OpenAI 兼容接口）或 `dashscope`
- `python-dotenv`

详见 `requirements.txt`。

## 许可证

MIT。本项目仅供学习与参考；NanoClaw 为原设计灵感来源。
