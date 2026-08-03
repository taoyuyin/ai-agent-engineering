# Prompts

`prompts/` 保存被多个 Agent 复用的 Prompt 资产。单章教学 Prompt 可以留在章节代码中；进入本目录的 Prompt 必须版本化、可评测并明确输入输出契约。

## Prompt 不是字符串常量

一个生产 Prompt 资产至少包含：

- `prompt_id`、语义版本、Owner 和用途；
- System/Developer 指令与变量 Schema；
- 结构化输出 Schema；
- 允许使用的 Tool/Capability；
- 适用模型族与已知限制；
- Eval Suite、基线分数和发布日期；
- 变更说明、灰度和回滚版本。

## 推荐结构

```text
prompts/<prompt-id>/
├── README.md
├── v1.yaml
├── v2.yaml
└── eval-cases.jsonl
```

变量必须由模板引擎显式声明，不能用字符串拼接把用户输入提升为系统指令。知识、策略和业务数据应通过独立 Context Section 注入，并保留来源与信任等级。

## 发布流程

```text
Edit → Static Variables/Schema Check → Offline Eval
     → Security Cases → Canary → Activate → Monitor/Rollback
```

Chapter 24 的 [`prompt_runtime`](../chapters/chapter24/prompt_runtime/) 已实现不可变版本、严格变量检查、Checksum 和 Active Version。共享 Prompt 在有第二个消费者之前不迁入本目录，避免没有复用价值的集中化。
