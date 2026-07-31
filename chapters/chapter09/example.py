"""Minimal ReAct loop MVP.

Run:
    python chapters/chapter09/example.py
"""

DATA = {
    "churn_rate": "客户流失率从 5% 上升到 9%",
    "support_tickets": "退款相关工单增加 40%",
    "usage": "核心功能使用频次下降 25%",
}


def tool(name):
    return DATA[name]


def decide_next(observations):
    if "churn_rate" not in observations:
        return "churn_rate", "先确认流失是否真的上升"
    if "support_tickets" not in observations:
        return "support_tickets", "流失上升后，检查客服工单是否有异常"
    if "usage" not in observations:
        return "usage", "继续检查产品使用是否下降"
    return None, "已有足够证据，可以总结"


def react(goal, max_steps=5):
    observations = {}
    trace = []
    for _ in range(max_steps):
        action, thought = decide_next(observations)
        trace.append(("thought", thought))
        if action is None:
            break
        result = tool(action)
        observations[action] = result
        trace.append(("action", action))
        trace.append(("observation", result))
    return trace, observations


if __name__ == "__main__":
    trace, observations = react("分析客户流失原因")
    for kind, value in trace:
        print(f"{kind.upper()}: {value}")
    print("\nConclusion: 流失可能与退款工单增加和核心功能使用下降有关。")
