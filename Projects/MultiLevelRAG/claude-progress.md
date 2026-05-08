# MultiLevelRAG — 进度日志

## 2026-05-08 会话初始化

### 项目状态
- 已有完整代码：5 种 RAG 策略 + 意图路由 + Streamlit UI + 知识图谱
- 所有核心功能（F01-F10）状态：**passing**（代码已存在，待验证）
- 待开发功能（F11-F14）：BM25 混合检索 / Cross-encoder 重排序 / RAGAS 评估 / 流式输出

### 本次会话任务
- 创建项目管理文件（feature_list.json / claude-progress.md / init.sh）
- 运行 smoke test 验证核心功能可用性

### 验证结果
- [x] config + .env 加载 — PASS
- [x] 模块导入（5 策略 + 路由 + comparator）— PASS
- [x] 路由器逻辑（策略指定模式）— PASS
- [x] LLM 工厂（ChatOpenAI 实例）— PASS
- [x] 向量库元数据（3 个文档）— PASS
- [ ] Embedding API — **BLOCKED**：DashScope API Key 无效/缺失
- [ ] 各策略 E2E 运行 — BLOCKED（依赖 Embedding）
- [ ] Streamlit 启动 — 未测试

### Blocked
- **DashScope Embedding API Key**：`.env` 中缺少 `DASHSCOPE_API_KEY`，导致所有依赖向量检索的功能无法端到端测试
- 解决方案：添加有效 DashScope Key / 切换 embedding provider
