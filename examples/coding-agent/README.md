# Coding Agent

当前状态：**设计契约，尚无本目录可运行工程**。受控 Patch、Test、Rollback MVP 见 [Chapter 45](../../chapters/chapter45/README.md)。

## 业务目标

Agent 在明确仓库、任务和权限范围内读取代码、提出计划、生成 Patch、运行验证并提交供人审查的 Change Proposal。默认不直接合并或部署。

## 端到端流程

```text
Issue / Executable Spec
  → Repository Map + Instructions
  → Plan + Risk Classification
  → Isolated Worktree / Sandbox
  → Search / Edit / Test Loop
  → Diff + Static/Security Checks
  → Evidence Bundle
  → Human Review
  → Commit / PR (explicit authorization)
```

## 模型与确定性边界

模型负责代码理解、计划和 Patch 候选；Harness 控制文件范围、命令 Allowlist、网络、Secret、时间和资源。测试通过只是证据之一，合并权限、发布门禁和高风险目录审批由确定性系统执行。

## 目标工程结构

```text
coding-agent/
├── README.md
├── requirements.txt
├── coding_agent/
│   ├── repository.py
│   ├── planner.py
│   ├── sandbox.py
│   ├── patcher.py
│   ├── verifier.py
│   └── application.py
├── fixtures/
├── tests/
├── evaluation/
└── Dockerfile
```

## 最小验收

- Agent 只能修改 Task Scope 内文件；
- Shell、网络、Secret 和依赖安装受策略限制；
- Patch 可回滚并保留 Agent/Model/Prompt/Tool Provenance；
- 测试、类型、安全和需求覆盖形成 Evidence Gate；
- 高风险变更必须人工批准；
- 失败循环受 Step、Token、时间和成本预算限制。

## 生产升级

接入 Git Provider、CI、Code Search、构建缓存、漏洞扫描和 PR Review；按仓库敏感等级配置不同 Sandbox，并持续测量 Lead Time、缺陷、返工和审查负担。
