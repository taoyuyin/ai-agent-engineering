"""Minimal context assembler MVP.

Run:
    python chapters/chapter08/example.py
"""

from dataclasses import dataclass


@dataclass
class ContextItem:
    name: str
    content: str
    priority: int

    @property
    def token_estimate(self):
        # Teaching approximation: one Chinese char / word-like segment ~= one token.
        return max(1, len(self.content) // 2)


def assemble_context(items, max_tokens):
    selected = []
    used = 0
    for item in sorted(items, key=lambda x: x.priority, reverse=True):
        if used + item.token_estimate <= max_tokens:
            selected.append(item)
            used += item.token_estimate
    prompt = "\n\n".join(f"[{item.name}]\n{item.content}" for item in selected)
    return prompt, used, [item.name for item in selected]


if __name__ == "__main__":
    items = [
        ContextItem("goal", "审查合同中的付款和违约风险", 100),
        ContextItem("policy", "公司要求超过 30 天账期必须法务审批", 90),
        ContextItem("contract", "本合同约定甲方在验收后 90 天内付款", 80),
        ContextItem("irrelevant", "供应商历史介绍和市场宣传材料" * 10, 10),
    ]
    prompt, used, names = assemble_context(items, max_tokens=80)
    print("Selected:", names)
    print("Estimated tokens:", used)
    print("\nFinal context:\n")
    print(prompt)
