# NanoBat 技能扩展

技能用于扩展 NanoBat 的能力（如查天气、读文件、执行命令等），而不改动核心 Agent 代码。

## 约定

- 每个技能可对应一个 Python 模块或一个可调用对象。
- 在 `src/agent.py` 中可注册「工具」描述，由 Qwen 在回复中声明需要调用某技能时，由主流程解析并执行（后续版本可接入 function calling）。
- 当前为占位：可在此目录下新增 `skill_xxx.py`，在 Agent 的 system prompt 中说明可用技能，由用户或后续路由逻辑触发。

## 示例（占位）

将来可在此添加：

- `skill_weather.py`：查询天气（调用外部 API 或本地工具）。
- `skill_todo.py`：简单待办记录与提醒。
- `skill_file.py`：安全范围内读/写本地文件。

扩展时请保持单一职责，并在本 README 中简要说明新技能的用途与用法。
