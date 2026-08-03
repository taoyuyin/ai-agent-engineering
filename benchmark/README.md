# Benchmark

`benchmark/` 保存可复现的对比实验，用来回答“在同一任务、数据和预算下，不同模型、Runtime 或策略有什么差异”。它不保存缺少配置和原始结果的排行榜截图。

## Benchmark 与 Evaluation 的区别

- `evaluation/` 定义正确性和门禁，可用于单个系统持续回归；
- `benchmark/` 固定实验协议，对多个候选进行公平比较；
- `datasets/` 提供输入、Ground Truth 和数据版本。

## 实验必须固定

- Dataset 与 split checksum；
- Agent、Prompt、Tool、Policy 和模型版本；
- 温度、最大 Token、超时、重试和并发；
- 硬件、地域、服务版本和缓存状态；
- 每个 Case 的原始 Trace、成本和错误；
- 重复次数、随机种子和统计方法。

## 推荐结构

```text
benchmark/<name>/
├── README.md          # 假设、范围和复现命令
├── config.yaml        # 被测矩阵与预算
├── run.py             # 统一执行入口
├── cases/             # 固定输入或数据引用
└── results/           # 带时间和 commit 的机器可读结果
```

## 对比原则

同一实验应使用相同 Tool、Context 和权限；如果厂商能力不同，必须明确哪些差异来自模型、哪些来自平台内置 Tool。除 Task Success 外，同时报告 P50/P95 延迟、Token、成本、失败类型和安全拒绝。

当前仓库尚未发布正式 Benchmark Runner。Chapter 29 的离线 Evaluation MVP 是未来基准执行器的评分基础；在加入首个 Benchmark 时，应同时提交配置、样例结果和复现说明。
