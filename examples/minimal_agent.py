"""最小可运行 Agent：一个 while 循环 + 工具分发。

运行：
    pip install -r requirements.txt
    export OPENAI_API_KEY=sk-xxx
    export OPENAI_BASE_URL=https://api.openai.com/v1   # 可选，OpenAI 兼容服务
    export MODEL=gpt-4o-mini                            # 可选
    python minimal_agent.py "当前目录有哪些文件？顺便算下 12*(3+4)"
"""

import json
import os
from pathlib import Path

from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)
MODEL = os.environ.get("MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = (
    "你是一个会使用工具的助手。"
    "需要外部信息或计算时必须调用工具，不要凭记忆猜测。"
    "工具返回 ERROR 时，先判断原因再换一种方式，不要重复同样的调用。"
    "信息足够时直接给出最终答案。"
)

# --- 工具定义 -------------------------------------------------------------

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "列出指定目录下的文件名和子目录名。返回名称列表，不递归。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "目录路径，默认为当前目录 .",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取文本文件内容，最多返回前 2000 个字符，超出部分会用省略号标记。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件相对或绝对路径"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算一个算术表达式，支持 + - * / ** 和括号。用于任何数值计算。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "例如 12*(3+4)"}
                },
                "required": ["expression"],
            },
        },
    },
]


def tool_list_dir(path: str = "."):
    items = sorted(p.name + ("/" if p.is_dir() else "") for p in Path(path).iterdir())
    return items[:100]


def tool_read_file(path: str):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    return text[:2000] + ("..." if len(text) > 2000 else "")


def tool_calculate(expression: str):
    # 仅允许数字和运算符，避免任意代码执行
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        raise ValueError(f"表达式含非法字符: {expression}")
    return eval(expression, {"__builtins__": {}}, {})  # noqa: S307


TOOL_IMPL = {
    "list_dir": tool_list_dir,
    "read_file": tool_read_file,
    "calculate": tool_calculate,
}

# --- 主循环 ---------------------------------------------------------------


def run(question: str, max_steps: int = 8) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    for step in range(1, max_steps + 1):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS_SCHEMA
        )
        msg = resp.choices[0].message
        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            return msg.content or ""

        for call in msg.tool_calls:
            name = call.function.name
            try:
                args = json.loads(call.function.arguments or "{}")
                result = TOOL_IMPL[name](**args)
            except Exception as exc:  # 错误也作为观察结果回喂给模型
                result = f"ERROR: {exc}"
            print(f"[step {step}] {name}({call.function.arguments}) -> {result}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return f"达到最大步数 {max_steps}，未能完成任务"


if __name__ == "__main__":
    import sys

    q = " ".join(sys.argv[1:]) or "当前目录有哪些文件？顺便算下 12*(3+4)"
    print("问题:", q)
    print("答案:", run(q))
