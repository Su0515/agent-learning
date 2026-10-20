# Agent 开发学习笔记

个人学习 Agent（智能体）开发的笔记与可运行示例。目标是把「调用一次 LLM」逐步变成「能自主完成任务的系统」。

## 学习路线

| # | 主题 | 文档 | 一句话 |
|---|------|------|--------|
| 1 | 什么是 Agent | [docs/01-what-is-an-agent.md](docs/01-what-is-an-agent.md) | Agent = LLM + 工具 + 循环 + 记忆 |
| 2 | 工具调用 | [docs/02-tool-calling.md](docs/02-tool-calling.md) | function calling 是 Agent 的「手」 |
| 3 | 记忆与上下文 | [docs/03-memory-and-context.md](docs/03-memory-and-context.md) | 上下文窗口是稀缺资源 |
| 4 | 编排模式 | [docs/04-orchestration.md](docs/04-orchestration.md) | ReAct / Plan-and-Execute / 多 Agent |
| 5 | 评测与调试 | [docs/05-evaluation.md](docs/05-evaluation.md) | 没有评测就没有迭代 |

## 目录结构

```
agent-learning/
├── README.md
├── docs/                 # 学习笔记
├── examples/             # 可运行代码
│   ├── minimal_agent.py  # 最小 Agent 循环（工具调用）
│   └── requirements.txt
└── .gitignore
```

## 快速开始

```bash
cd examples
pip install -r requirements.txt

# 任选一个 OpenAI 兼容服务
export OPENAI_API_KEY=sk-xxx
export OPENAI_BASE_URL=https://api.openai.com/v1   # 可选
export MODEL=gpt-4o-mini                            # 可选

python minimal_agent.py "帮我看下当前目录有哪些文件，再算一下 12*(3+4)"
```

## 学习原则

1. **先手写循环，再用框架**。LangChain / LangGraph / OpenAI Agents SDK 都是在循环上包了一层，不理解循环就会被框架卡住。
2. **每次只改一个变量**。改提示词、换模型、加工具分开做，否则不知道是哪一步起的作用。
3. **把 Agent 的运行过程当分布式系统看**：可观测性（日志/轨迹）、超时、重试、幂等、成本上限，一个都不能少。
4. **工具描述就是 API 文档**。模型选错工具，九成是描述写得含糊。
