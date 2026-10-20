# 01 什么是 Agent

## 一句话定义

> Agent 是让 LLM 在**循环**中自主决定下一步动作（调用工具 / 输出结果）的系统。

普通调用：

```
用户问题 -> LLM -> 答案
```

Agent：

```
用户目标 -> LLM 决策 -> 调工具 -> 观察结果 -> LLM 再决策 -> ... -> 终止
```

区别不在模型，而在**控制流由谁掌握**。普通调用里控制流写死在代码里；Agent 里控制流是模型每轮临时决定的。

## 四个必备组件

1. **模型（Brain）**：做决策。需要具备 function calling 能力。
2. **工具（Tools）**：真正干活的手脚。搜索、读文件、跑命令、调 API。
3. **循环（Loop）**：把「决策 → 执行 → 观察」串起来，并提供终止条件。
4. **状态（State）**：消息历史、中间结果、待办事项。没有状态就没有「连贯性」。

可选但工程上迟早要加：记忆、规划、反思、人工审批。

## 最小的 Agent 长什么样

核心就是一个 `while`：

```python
while step < max_steps:
    resp = llm(messages, tools=tools)
    if not resp.tool_calls:
        return resp.content          # 模型认为可以收工了
    for call in resp.tool_calls:
        result = dispatch(call)       # 执行工具
        messages.append(tool_message(call.id, result))
```

完整可运行版本见 [examples/minimal_agent.py](../examples/minimal_agent.py)。

## 什么时候不该用 Agent

- 任务步骤固定、可以写成流程图 → 用普通函数或 workflow，便宜且可控。
- 一次调用就能答对 → 直接调模型。
- 错误代价极高且无法回滚 → 加人工确认，或改成「Agent 出建议、人执行」。

判断标准：**任务路径是否不可预知**。可预知就别上 Agent。

## 踩坑记录

- 忘记设 `max_steps`：模型可能无限重试同一个失败的工具，烧钱。
- 工具报错直接抛异常：整个循环挂掉。应该把错误当**观察结果**喂回模型，让它自己纠正。
- 把工具结果截断得太狠：模型拿不到关键信息，会反复重试。

## 动手练习

1. 跑通 `examples/minimal_agent.py`，观察每一步的 `[step N]` 日志。
2. 故意让某个工具抛异常，确认 Agent 能自己换个方式完成任务。
3. 把 `max_steps` 改成 1，看会发生什么。
