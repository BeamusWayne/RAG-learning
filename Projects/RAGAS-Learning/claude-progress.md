# 进度日志

## 当前已验证状态

- 仓库根目录：`/Users/katya/Files/RAG-learning`
- 子项目目录：`Projects/RAGAS-Learning/`
- 标准启动路径：`cd Projects/RAGAS-Learning && ./init.sh`
- 标准验证路径：`cd Projects/RAGAS-Learning && python -c "import ragas; print(ragas.__version__)"`
- 当前最高优先级未完成功能：ragas-008 — 对比评估 Naive RAG vs Reranked RAG
- 当前 blocker：无

## 会话记录

### Session 005 — 2026-05-04

- 日期：2026-05-04
- 本轮目标：完成 ragas-006 evaluate() 综合评估 demo
- 已完成：ragas-006 验证通过（3 样本 × 4 指标 = 12 个评估任务）
- 运行过的验证：`uv run python demos/demo_evaluate.py`
- 已记录证据：feature_list.json ragas-006 evidence 已填充
- 关键发现：
  1. `evaluate()` 是同步函数，不需要 `await`（前面各指标用 `single_turn_ascore` 是异步的）
  2. `LangchainEmbeddingsWrapper` 从 `ragas.embeddings` 导入，不是 `ragas.utils`
  3. `EvaluationDataset(samples=[...])` 包裹多个 `SingleTurnSample`
  4. `result.to_pandas()` 返回 DataFrame，包含所有指标列
  5. 运行时间约 50 秒（3 样本 × 4 指标），有 tqdm 进度条
- 更新过的文件：demo_evaluate.py, feature_list.json, tutorial.html, claude-progress.md
- 下一步最佳动作：ragas-007 合成测试数据集生成 demo

### Session 006 — 2026-05-04

- 日期：2026-05-04
- 本轮目标：完成 ragas-006 和 ragas-007
- 已完成：
  - ragas-006 evaluate() 综合评估 demo 验证通过
  - ragas-007 合成测试数据集生成 demo 验证通过
- 运行过的验证：
  - `uv run python demos/demo_evaluate.py` — 3 样本 × 4 指标 OK
  - `uv run python demos/demo_testset_generator.py` — 生成 6 条测试样本
- 已记录证据：feature_list.json ragas-006/007 evidence 已填充
- 关键发现：
  1. evaluate() 是同步函数，不需要 await
  2. LangchainEmbeddingsWrapper 从 ragas.embeddings 导入
  3. TestsetGenerator 内部执行 7 步 transform 管线
  4. 需要 rapidfuzz 依赖（NER 重叠度计算）
  5. 直接用 /opt/homebrew/bin/python3 会缺少 dotenv（需用 uv run 或激活 venv）
- 修复：延伸阅读改为纯文本标签（原来看起来像链接但不可点击）
- 更新过的文件：demo_evaluate.py, demo_testset_generator.py, feature_list.json, tutorial.html, claude-progress.md
- 下一步最佳动作：ragas-008 对比评估 Naive RAG vs Reranked RAG

- 日期：2026-05-04
- 本轮目标：完成 ragas-003 Answer Relevancy demo
- 已完成：ragas-003 验证通过（相关答案 0.8739，不相关答案 0.4567）
- 关键发现：
  1. ResponseRelevancy 需要 LLM + Embeddings 两部分
  2. glm-4-flash 的反向问题生成质量不足，需用 glm-4-plus
  3. Embeddings 使用智谱 embedding-3（OpenAI 兼容接口）
  4. LangchainEmbeddingsWrapper 包装 langchain embedding 供 RAGAS 使用
- 更新过的文件：demo_answer_relevancy.py, feature_list.json, tutorial.html, claude-progress.md
- 下一步最佳动作：ragas-004 Context Precision demo

### Session 003 — 2026-05-04

- 日期：2026-05-04
- 本轮目标：完成 ragas-002 Faithfulness demo
- 已完成：ragas-002 验证通过（高忠实度 1.0000，低忠实度 0.0000）
- 运行过的验证：`python demos/demo_faithfulness.py` 使用智谱 GLM-4-flash
- 已记录证据：feature_list.json ragas-002 evidence 已填充
- 关键发现：
  1. RAGAS 0.4.3 使用 `SingleTurnSample` + `Faithfulness(llm=llm)` + `scorer.single_turn_ascore(sample)` API
  2. 必须显式传入 `llm_factory(model, client=OpenAI(...))` ，不会自动从环境变量创建 LLM
  3. 推理模型（MiniMax-M2/M2.7、GLM-5.1）的思考输出破坏 instructor 的 JSON 解析，必须用非推理模型
  4. 智谱 glm-4-flash 兼容 OpenAI 协议，可用于 RAGAS 评估
- 目录整理：demo 移入 demos/，文档移入 docs/
- .env 更新：添加智谱 AI 配置（ZHIPU_API_KEY/BASE_URL/CHAT_MODEL）
- 更新过的文件：demo_faithfulness.py, .env, feature_list.json, claude-progress.md
- 下一步最佳动作：ragas-003 Answer Relevancy demo

### Session 002 — 2026-05-04

- 日期：2026-05-04
- 本轮目标：完成 ragas-001 环境搭建验证
- 已完成：ragas-001 通过验证，修复 init.sh 语法错误，解决 mistralai 兼容性问题
- 运行过的验证：`./init.sh` 全部 3 个依赖就绪（RAGAS 0.4.3, Datasets 4.8.5, LangChain 1.2.10）
- 已记录证据：feature_list.json ragas-001 evidence 已填充
- 关键修复：
  1. init.sh Python heredoc 从双引号改为 `<< 'PYEOF'`，避免 bash 展开 f-string 中的 `${}`
  2. pyproject.toml 添加 `mistralai<2` 约束，因 instructor 1.15.1 调用 `mistralai.Mistral` 在 2.x 已移除
- 更新过的文件：init.sh, pyproject.toml, feature_list.json, claude-progress.md
- 下一步最佳动作：从 ragas-002 开始，创建 Faithfulness demo

### Session 001 — 2026-05-04

- 日期：2026-05-04
- 本轮目标：创建 RAGAS-Learning 子项目，搭建 Harness Engineering 文件骨架
- 已完成：CLAUDE.md, AGENTS.md, feature_list.json, claude-progress.md, init.sh, session-handoff.md, clean-state-checklist.md, evaluator-rubric.md, quality-document.md 全部就位
- 运行过的验证：确认目录结构正确
- 已记录证据：无（harness 文件就位，尚未开始实际功能开发）
- 提交记录：待提交
- 更新过的文件或工件：Projects/RAGAS-Learning/ 下全部 harness 文件
- 已知风险或未解决问题：ragas 与仓库现有依赖的兼容性未验证
- 下一步最佳动作：从 ragas-001 开始，安装 ragas 并验证 import
