# Guardrail Runtime MVP

本模块展示 Input、Context、Tool 和 Output 四层 Guardrail，而不是用一个 System Prompt 承担全部安全责任。

## 实现内容

- Input 检测典型指令注入并 Block；
- Context 要求 Provenance，并移除不可信指令行；
- Tool 只能来自 Allowlist，Raw SQL/Shell 类参数进入 Review；
- Output 验证必需字段并脱敏敏感字段；
- 每层返回 `allow/transform/review/block` 与审计原因。

## 模型关系

模型输入输出都通过 Guardrail Pipeline；Pipeline 不依赖模型自我判断。正则仅是教学层，生产安全还需要身份、Tool Schema、DLP、Sandbox 和业务审批。

```bash
python chapters/chapter28/example.py
python -m unittest discover -s chapters/chapter28 -p "test_*.py"
```

正文见 [Chapter 28](../README.md)。
