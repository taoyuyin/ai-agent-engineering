# Browser Agent

当前状态：**设计契约，尚无本目录可运行浏览器工程**。安全动作 Harness MVP 见 [Chapter 52](../../chapters/chapter52/README.md)。

## 业务目标

在没有稳定 API 的供应商门户中读取库存、填写询价草案并在提交前等待用户确认。案例用于展示 Computer Use 的完整 Observation–Action Loop，而不是通用网页爬虫。

## 端到端流程

```text
Goal + Direct User Authorization
  → Isolated Browser Session
  → Screenshot / DOM / Accessibility Observation
  → Model Action Proposal
  → Domain + Action + Data Policy
  → Execute One Action
  → Capture and Verify New State
  → Confirm High-risk Side Effect
  → Receipt Evidence / Trace / Destroy Session
```

## 模型与确定性边界

多模态模型读取 Observation 并提出 Click、Type、Scroll 等动作；Harness 决定是否执行。网页、邮件和文档内容永远不能扩大用户授权。优先 API，其次 DOM/Accessibility，视觉坐标作为恢复和 Long Tail 能力。

## 目标工程结构

```text
browser-agent/
├── README.md
├── requirements.txt
├── browser_agent/
│   ├── session.py
│   ├── observation.py
│   ├── policy.py
│   ├── executor.py
│   ├── verifier.py
│   └── application.py
├── fixtures/
├── tests/
├── evaluation/
└── Dockerfile
```

## 最小验收

- 使用隔离浏览器，不复用员工个人 Profile；
- 协议、域名、下载、上传和动作有 Allowlist；
- 敏感输入和外部副作用在执行前即时确认；
- 每一步后重新观察，不盲目执行坐标序列；
- 设置最大步骤、超时、成本、循环和人工接管；
- Receipt 由独立状态或回执验证。

## 生产升级

接入 Browser Pool、短期凭证、网络策略、视频/截图脱敏、回放和 OSWorld 类任务评测；对付款、删除、发信等动作建立更严格的业务 Policy。
