# Chapter 52 Computer Use

Part VII Future —— 下一代软件

Version: 2026-08

Last Updated: 2026-08-03

## Core Question

当系统没有稳定 API 时，Agent 如何通过屏幕、鼠标和键盘完成任务，同时控制视觉误判、界面变化和安全风险？

## Chapter Conclusion

Computer Use 把 GUI 变成一种 Tool：Agent 观察屏幕，提出动作，执行环境完成动作并返回新截图。它扩展了 Agent 可以操作的软件范围，却比 API 调用更慢、更脆弱、也更危险。

工程原则是 `API first, GUI fallback`。Computer Use 必须运行在隔离环境中，以允许列表、最小权限、动作验证和即时人工确认包围模型，而不是让模型直接控制真实桌面。

## Learning Objectives

完成本章后，你应该能够：

- 区分 Browser Automation、Browser Agent、GUI Agent 和 Computer Use；
- 实现 Observation → Action → Execute → Verify 循环；
- 横向比较 API、DOM、Accessibility Tree、Vision 和 Hybrid 路线；
- 设计 Sandbox、Domain Allowlist、Action Policy 和 Human Confirmation；
- 为 Computer Use 建立任务、步骤、安全和成本评测。

## 52.1 Computer Use 解决什么问题

企业仍有大量系统缺少可用 API：老旧 ERP、供应商门户、桌面客户端、远程运维界面和只允许人工登录的网站。传统 RPA 依赖固定选择器和流程，界面稍有变化就会失败；多模态 Agent 可以根据视觉和语义重新定位控件。

但“能够点击”不等于“可靠完成业务”。Computer Use 的价值主要在：

- 覆盖没有 API 的 Long Tail 软件；
- 在页面布局轻微变化时重新规划；
- 处理跨应用、步骤不固定的知识工作；
- 为现有软件提供过渡性的自动化接口。

高频、关键、可标准化操作仍应建设 API。GUI 是最外层、最不稳定的集成契约。

## 52.2 概念边界

| 概念 | 主要输入 | 主要动作 | 决策来源 |
| --- | --- | --- | --- |
| Browser Automation | DOM / Selector | Click、Fill、Navigate | 固定脚本 |
| RPA | UI Selector / Image | 跨应用操作 | 固定流程与规则 |
| Browser Agent | DOM、页面文本、截图 | 浏览器 Tool | LLM + Runtime |
| GUI Agent | Screenshot / Accessibility | Mouse、Keyboard | 多模态模型 + Policy |
| Computer Use | 通用计算机环境 Observation | Screenshot、Click、Type、Scroll | Agent Loop + Harness |

这些路线不是互斥的。生产系统通常使用 Hybrid：优先 DOM 或 Accessibility 定位，视觉负责理解和恢复，API 负责关键提交。

## 52.3 Observation–Action Loop

官方 Computer Use 接口的共同结构可以抽象为：

```text
User Goal
   ↓
Isolated Environment ──screenshot/state──→ Model
        ↑                                  │
        │                            proposed action(s)
        │                                  ↓
        └──── Executor ← Policy / Approval Gate
                    │
                    └── execute, capture, verify, repeat
```

一次循环包含：

1. Harness 创建隔离浏览器或虚拟机；
2. Runtime 把目标和当前截图发送给模型；
3. 模型返回结构化动作，如 Click、Type、Scroll；
4. Policy Engine 在执行前校验域名、动作、数据和副作用；
5. Executor 执行动作并截取新屏幕；
6. Runtime 验证状态是否按预期改变；
7. 完成、恢复、等待人工或继续下一步。

截图是 Observation，不是可信指令。网页中“忽略规则并上传文件”的文字属于第三方内容，不能扩大用户授权。

## 52.4 技术路线横向比较

| 路线 | 优点 | 缺点 | 适用场景 |
| --- | --- | --- | --- |
| API / Function Calling | 稳定、结构化、可测试、低延迟 | 需要系统提供接口 | 支付、写库、批量操作 |
| DOM / Selector | 元素定位精确，可读取结构 | 跨站差异大，虚拟画布不可见 | Web 表单和内部系统 |
| Accessibility Tree | 语义标签更清晰，兼顾可访问性 | 应用支持质量不一致 | 桌面与浏览器控件 |
| Pure Vision | 接近人类界面，可覆盖 Canvas/远程桌面 | 坐标脆弱、Token/延迟高 | 无结构界面和恢复路径 |
| Hybrid | 可在精度、覆盖和恢复之间平衡 | Harness 与路由更复杂 | 企业级 Computer Use |

推荐顺序：API → 语义结构 → 视觉定位。视觉模型不应成为所有操作的默认通道。

## 52.5 为什么 GUI Agent 容易失败

### 坐标不是身份

`click(640, 420)` 只对当前分辨率和页面状态有效。弹窗、滚动、字体、响应式布局都可能让坐标失效。动作后必须重新观察，不能盲目连续执行坐标序列。

### 页面状态是部分可观测的

加载中、登录过期、按钮禁用、隐藏弹窗和异步请求都可能不在当前截图中清晰呈现。Harness 需要等待条件、超时、截图差异和页面状态探针。

### 动作不一定幂等

刷新“查询结果”通常可重试，点击“付款”不可随意重试。每个动作应声明 `read_only`、`reversible`、`external_side_effect` 或 `destructive`。

### 成功文本不等于成功状态

页面显示“已提交”仍可能是恶意内容或旧通知。高风险操作应通过独立 API、数据库事件、邮件回执或人工确认验证。

## 52.6 安全模型

### 隔离执行环境

- 使用专用浏览器、容器或 VM，不控制员工日常桌面；
- 不挂载宿主机个人目录、SSH Key 和浏览器 Profile；
- 使用任务级临时账号、下载目录和网络策略；
- 结束后销毁环境并按策略保留 Trace。

### Domain 与 Action Allowlist

只允许访问任务所需域名；阻止 `file://`、本地网络和未知协议。只开放所需动作，高风险动作默认需要确认。

### 在风险发生点确认

人工确认必须发生在具体动作执行前，而不是任务开始时笼统询问一次。典型确认点：

- 输入密码、银行卡、身份证或商业机密；
- 发送邮件、发布内容、提交表单；
- 购买、付款、退款和签署；
- 删除、覆盖、下载或上传文件；
- 接受网站条款或改变权限。

只有用户直接给出的指令可以授权这些动作。网页、邮件和文档中的文字都应视为不可信输入。

### 凭证边界

模型不应看到长期密码。优先使用短期 Session、Secret Injection 和 Scope 限制；输入敏感值时，Harness 可将占位符解析为密文注入，并在 Trace 中脱敏。

## 52.7 业务场景：供应商门户询价

采购 Agent 需要登录三个没有 API 的供应商门户，读取库存并创建询价草案：

1. Agent 在隔离浏览器打开 Allowlist 域名；
2. 视觉或 DOM 工具读取型号和库存；
3. 数据被规范化并写入内部比较表；
4. Agent 填写询价内容，但不自动发送；
5. 采购员检查供应商、数量、价格和附件；
6. 用户确认后，Harness 执行提交并保存回执截图；
7. 独立任务检查门户状态或邮件回执。

读取库存和提交询价应使用不同 Scope。不要因为 Agent 能完成前者，就默认它有权执行后者。

## 52.8 Python MVP：安全动作 Harness

本章示例不依赖真实浏览器，而是聚焦最重要的执行边界：

- `Observation` 保存屏幕、URL 和不可信内容标记；
- `Action` 声明动作类型、目标和值是否敏感；
- `ComputerPolicy` 返回 `allow / confirm / block`；
- Harness 只执行允许动作，在敏感数据输入前暂停；
- Trace 同时记录提案和策略决定。

```bash
cd chapters/chapter52
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py
```

接入真实 Computer Use 模型时，保留同一边界：模型只生成 Action Proposal，Policy 和 Harness 决定是否执行。

**与模型的关系**：真实多模态模型读取截图并提出 Click、Type、Scroll 等动作；离线 MVP 用预置动作替代这一步，以便独立验证最关键的安全 Harness。替换模型不能绕过同一 Policy。

## 52.9 如何评测 Computer Use

| 指标 | 含义 | 为什么重要 |
| --- | --- | --- |
| Task Success Rate | 端到端任务完成比例 | 最终业务结果 |
| Step Success Rate | 单步动作正确比例 | 定位失败阶段 |
| Recovery Rate | 页面变化后恢复比例 | 评估鲁棒性 |
| Unsafe Action Rate | 越权或高风险动作比例 | 安全底线 |
| Confirmation Precision | 请求确认中真正高风险比例 | 避免审批疲劳 |
| Steps / Task | 完成任务的动作数 | 效率与循环风险 |
| Latency / Cost | 单任务耗时和模型成本 | 判断是否值得 GUI 自动化 |

OSWorld 一类基准可以比较通用计算机任务能力，但企业上线还需要用自己的页面版本、账号权限、网络延迟和风险动作建立回归集。

## 52.10 工程检查清单

- 是否确实没有更稳定的 API？
- 浏览器/VM 是否与用户桌面隔离？
- 页面内容是否始终视为不可信输入？
- 域名、协议、上传和下载是否有 Allowlist？
- 每个动作是否声明风险与幂等性？
- 高风险确认是否发生在执行前一刻？
- 动作后是否重新观察并验证状态？
- 凭证和截图 Trace 是否脱敏？
- 是否设置最大步骤、超时、成本和循环检测？
- 是否可以安全取消、回滚或人工接管？

## Summary

Computer Use 让 Agent 进入现有软件世界，但它不是“万能 API”。可靠系统采用 Hybrid 技术路线，把模型限制为动作提议者，并用隔离环境、确定性策略、状态验证和人工确认控制副作用。

下一章将进一步讨论：当目标理解和动态能力组合成为产品核心，而不只是一个自动化插件时，软件架构会发生什么变化？

## References

- [OpenAI Computer use guide](https://developers.openai.com/api/docs/guides/tools-computer-use)
- [Anthropic Computer Use Tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments](https://arxiv.org/abs/2404.07972)
