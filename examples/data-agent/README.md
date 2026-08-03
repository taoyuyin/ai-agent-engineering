# Data Agent

当前状态：**设计契约，尚无本目录可运行工程**。可运行的单章控制面见 [Chapter 43](../../chapters/chapter43/README.md)。

## 业务目标

用户提交一个数据集和分析目标，Agent 完成数据剖析、质量门禁、统计分析、异常解释和报告草案；证据不足时明确停止或请求补充，而不是生成看似合理的结论。

## 端到端流程

```text
Upload / Data Reference
  → Identity + Data Classification
  → Profile / Schema / Quality Gate
  → Analysis Plan
  → Sandboxed Python / SQL Tools
  → Statistical Validation
  → Evidence Table / Chart Spec
  → Analyst Review
  → Report Artifact + Trace
```

## 模型与确定性边界

模型负责目标理解、分析计划候选和解释草案；确定性服务负责文件解析、类型推断、统计计算、代码沙箱、数据权限和结果校验。所有数值必须来自 Tool Observation，不能由模型自行计算后当作证据。

## 目标工程结构

```text
data-agent/
├── README.md
├── requirements.txt
├── data_agent/
│   ├── application.py
│   ├── profiler.py
│   ├── planner.py
│   ├── analysis_tools.py
│   ├── validator.py
│   ├── report.py
│   └── api.py
├── tests/
├── evaluation/
└── Dockerfile
```

## 最小验收

- 能识别缺失、重复、类型和范围异常；
- 质量门禁失败时不会继续生成业务结论；
- 分析代码只能访问任务目录并受时间/内存限制；
- 报告中的数字、图和结论可追溯到数据快照与执行结果；
- 不同租户的数据和 Artifact 完全隔离；
- 固定 Fixture 上结果可复现。

## 生产升级

接入对象存储、查询引擎、分布式任务、Notebook Artifact、数据目录和审批系统；增加数据漂移、统计显著性、PII、成本与在线反馈评测。
