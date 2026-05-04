# CLAUDE.md

你正在一个 RAGAS 评估框架学习项目中工作。目标是系统学习 RAGAS 的每个评估维度，并产出可运行的 demo。

## 固定工作循环

每轮会话开始时：

1. 运行 `pwd`，确认当前在 `Projects/RAGAS-Learning/`
2. 读取 `claude-progress.md`
3. 读取 `feature_list.json`
4. 回到仓库根目录，用 `git log --oneline -5` 查看最近提交
5. 运行 `./init.sh`
6. 检查基础 smoke test 是否通过

然后只选择一个未完成功能，围绕它工作，直到它被验证通过，或者被明确记录为 blocked。

## 规则

- 同一时间只能有一个 active feature
- 没有可运行证据时，不要声称完成
- 不要通过重写功能清单来隐藏未完成工作
- 不要为了"看起来完成"而删除或削弱测试
- 以仓库内文件作为唯一事实来源

## 必需文件

- `feature_list.json`
- `claude-progress.md`
- `init.sh`
- 需要简短交接时使用 `session-handoff.md`

## 完成门槛

只有在要求的验证成功且结果被记录后，功能状态才可以切换到 `passing`。

## 结束前

1. 更新进度日志
2. 更新功能状态
3. 记录仍然损坏或未验证的内容
4. 在仓库可安全恢复后提交
5. 给下一轮会话留下干净的重启路径
