"""Chapter 28: enforce guardrails before and after model execution."""

from guardrail_runtime import GuardrailPipeline, ToolProposal


def main() -> None:
    pipeline = GuardrailPipeline(allowed_tools={"crm.read"}, sensitive_fields={"phone", "email"})
    print(pipeline.check_input("查询客户订单状态"))
    print(pipeline.check_tool(ToolProposal("crm.read", {"customer_id": "C-7"})))
    print(pipeline.check_output({"answer": "已发货", "phone": "13800000000"}))


if __name__ == "__main__":
    main()
