---
name: goal-writer
description: 把用户的任务/需求改写成一条适合 Claude Code `/goal` 命令的完成条件（做什么 + 可度量终态 + 验证方式 + 约束）。当用户提到"goal"、"/goal"、"设置一个 goal"、"帮我写 goal 条件"、"让 Claude 一直跑到完成为止"、"无人值守跑任务"、"自动循环直到通过"等，或用户描述了一个希望持续迭代直到达成的大任务（如"迁移完所有模块"、"测试全绿再停"）时，务必使用本 skill，即使用户没有明确说出 "goal" 这个词。
---

# Goal 提示词编写

帮用户把任务改写成一条 `/goal` 完成条件。产出物是一行可直接粘贴到 `/goal` 后面的文本，≤4000 字符。

## /goal 机制要点（决定条件怎么写）

- 每轮结束后，一个独立的评估模型（默认 Haiku）会拿**对话内容**去判断条件是否达成。评估模型**不执行命令、不读文件、不看终端**，它只能看到 Claude 在对话里说了什么。
- 因此条件必须能被 Claude **自己的输出证明**。例如："`npm test` 退出码为 0 且输出中有 `All tests passed`" 可行；"测试确实都通过了"（评估者无法验证）不可行。
- 判定结果是三选一：`Not yet met`（继续下一轮）/ `Met`（结束）/ `Impossible`（结束并清除）。条件写得无法判定，会导致无限循环或误判 Impossible。
- 一个会话同时只能有一个 goal；goal 不改变权限模式，无人值守跑需配合 auto mode。

## 条件四要素

改写时把用户的模糊需求补全为：

1. **要做什么**：`/goal` 的条件文本同时是工作指令——Claude 拿到它才知道该干什么。只写验收标准（"测试全绿"）Claude 不知道改什么；条件必须包含任务本身（"把 X 重构为 Y，直到…"）。
2. **可度量的终态**：什么时候算"完成"？用具体的、可观测的信号描述（命令退出码、文件存在且含某内容、数量归零、某输出出现）。
3. **验证方式**：Claude 每轮要跑什么命令、看什么输出来自证？评估模型只看对话，所以验证动作必须是 Claude 会在对话里展示的。
4. **约束**：边界条件。常用子句：
   - `or stop after N turns`（限制时长，防跑飞）
   - 范围限定（只改哪些文件/目录，不动什么）
   - 完成后要做什么（如输出总结报告）

## 常见坏模式

- **模糊终态**："代码质量更好了"、"基本完成" → 评估者无法判定。改为具体信号。
- **依赖对话外证据**："用户确认后"（无人值守时没有用户）、"所有调用点都正确"（未给出验证命令）。改为 Claude 可自证的验证步骤。
- **不可达条件**：条件依赖外部资源（付费 API、需要人工审批），会判定 Impossible 或死循环。改写为可达成的代理信号，或在条件中说明 fallback。
- **无验证动作**：只说结果不说怎么查。每条终态都应附带"用 X 命令/检查 Y 输出"的验证方式。
- **范围失控**：未限定范围时 Claude 可能顺手改无关文件。加上范围约束。
- **假设工具已存在**：终态依赖的脚本/检查器如果项目里没有，goal 会在第一轮就卡住。把它作为 goal 的第一步写进条件（"先创建 X 脚本，然后…"），确保整个闭环在 goal 生命周期内可建立。

## 编写流程

1. 从用户描述中提取：真正的目标、已有的验证手段（测试/lint/编译/脚本）、范围边界。
2. 若用户没说验证手段，先快速查看项目（package.json scripts、Makefile、pytest 配置等）找现成命令，不要凭空编造。
3. 按三要素起草条件，一条写完（`/goal` 只接受一段文本，可用分号组织多个检查点）。
4. 自检：假设你是只看对话的评估模型——Claude 达成后，对话里会出现什么文字让你敢判 Met？答不上来就补验证方式。

## 语言与呈现

- 条件正文可以用中文写（评估模型能读懂中文），但命令、退出码、预期输出等验证信号必须保持字面精确（如 `` `npm test` exits 0 ``），不要意译成"测试通过"。
- 若用户没提过 `/goal` 或明显不熟悉其机制，先一句话解释（"它会循环执行直到评估模型判定条件达成"）再给条件，不要假设用户知道怎么用。
- 大任务适合无头模式时提示：`claude -p "/goal <条件>" --output-format stream-json --verbose`（长任务必须加 stream-json，否则输出要等全部结束才打印）。

## 输出格式

给出：

1. **goal 条件**（代码块，一行，可直接粘贴）：
   ```
   <条件全文>
   ```
2. **设计说明**（简短）：终态是什么、每轮怎么自证、为什么加这些约束。
3. **使用提示**（仅在相关时）：建议配合 auto mode、预估轮数、风险点（如某验证命令较慢）。

**示例 1**
用户输入：帮我重构 utils 模块，拆成小文件，要保证不出错
输出条件：
```
Split utils.py into focused modules under utils/ with no file over 300 lines; after each move run `python -m pytest tests/ -x` and it must exit 0 with all tests passing; also run `python -m ruff check utils/` which must report no errors; when done, state the final file list and test summary; stop after 15 turns if not complete
```
说明：三个可判定信号（文件行数上限、pytest 退出码、ruff 无报错），每轮自证，带轮数上限。

**示例 2**
用户输入：让 Claude 自己把 issue 队列清空
输出条件：
```
Work through every open issue in the project issue tracker (docs/agents/issue-tracker.md): for each one, either fix it or close it with a reason; the goal is met when the tracker lists zero open issues and you have posted a per-issue summary of what was done; stop after 25 turns if not complete
```
说明：终态是"tracker 中 open 数为 0"——Claude 每轮会在对话里列出当前 open issues，评估者据此判定；带轮数上限。
