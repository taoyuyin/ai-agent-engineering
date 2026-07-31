"""Chapter 24: render a versioned, auditable prompt."""

from prompt_runtime import PromptRegistry, PromptTemplate


def main() -> None:
    registry = PromptRegistry()
    registry.register(
        PromptTemplate(
            prompt_id="incident-summary",
            version="1.0.0",
            system="你是 SRE 助手。只根据已验证事件生成摘要。",
            template="事件：{incident}\n影响：{impact}\n输出 JSON。",
            variables=("incident", "impact"),
            output_schema={"summary": "string", "severity": "string"},
        ),
        activate=True,
    )
    rendered = registry.render(
        "incident-summary",
        {"incident": "支付 API 超时", "impact": "华东区 5% 请求失败"},
    )
    print(rendered.text)
    print(rendered.metadata)


if __name__ == "__main__":
    main()
