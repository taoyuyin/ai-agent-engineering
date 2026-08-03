# Chapter 48 Manufacturing Agent

Part VI Enterprise Practice —— 企业实践

Version: 2026-08

Last Updated: 2026-08-03

## 本章结论

Manufacturing Agent 应优先作为 OT 系统之上的诊断和决策支持层，而不是直接闭环控制 PLC。生产安全、实时控制、联锁和停机逻辑仍属于确定性 OT 系统；Agent 负责跨数据源收集证据、解释异常、提出工单并等待授权。

## 学习目标

- 理解 ISA-95 式企业层、MES/SCADA/PLC 边界；
- 组合时序数据、设备主数据、维修知识和工单；
- 设计诊断、风险分级与人工审批状态机；
- 处理 IT/OT 网络隔离、可用性和安全要求；
- 评估误报、漏报、提前量和维护业务价值。

## 48.1 业务背景

电机轴承温度和振动持续升高。Agent 需要读取授权工厂的遥测、校验传感器质量、比较设备型号阈值、查找维修手册并提出维护建议。

错误停机可能造成产能损失，漏报可能造成设备和人员风险。制造场景的风险边界明显高于普通知识问答。

## 48.2 分层架构

```text
ERP / EAM / Data Platform
          |
Manufacturing Agent Service
  -> Asset Registry / Historian Read API
  -> Knowledge / Maintenance History
  -> Diagnostic & Risk Engine
  -> Work-order Proposal
  -> Human Approval
          |
MES / SCADA Gateway
          |
PLC / Safety Instrumented System
```

Agent 默认通过只读 Historian/Data API 获取遥测，不从云端直接访问 PLC。安全联锁不依赖 LLM 或外部网络。

## 48.3 数据 Contract

设备数据需要：Asset ID、Plant、Model、测点、单位、采样时间、质量码、校准信息和数据来源。没有单位或质量码的传感器数值不应进入诊断。

知识数据需要匹配设备型号、手册版本和工厂差异。维修工单提供历史故障模式，但不能自动证明当前根因。

## 48.4 最小可运行 MVP

`example.py` 实现：

- 工厂和 `telemetry:read` 权限；
- 温度、振动与 RPM 时间序列；
- 版本化安全阈值；
- 最新值、近期均值和趋势检查；
- 严重度分级；
- 维护工单 Proposal；
- Lockout/Tagout 标记和主管审批；
- 明确 `automatic_control_command_sent=false`。

```bash
cd chapters/chapter48
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python example.py motor-7
```

示例同时触发温度与振动阈值，因此状态是 `awaiting_human_approval`，不会自动停机或重启设备。

## 48.5 规则、ML 与 LLM 的分工

| 能力 | 推荐技术 |
| --- | --- |
| 实时联锁/停机 | PLC/SIS 确定性逻辑 |
| 阈值与组合规则 | Rule Engine |
| 异常检测/剩余寿命 | 经验证的时序 ML |
| 手册检索与解释 | RAG/LLM |
| 跨系统任务协调 | Agent/Workflow |
| 最终高风险决定 | 授权工程师 |

LLM 不应把自然语言建议直接翻译为控制指令。

## 48.6 IT/OT 安全

NIST SP 800-82 强调 OT 的性能、可靠性和安全要求。Agent 部署要遵循分区分域、最小通信、跳板/API Gateway、只读数据复制、资产清单和变更管理。

模型服务不可用时，设备安全逻辑仍要独立运行。Agent 是增强层，不是安全关键依赖。

## 48.7 Human-in-the-loop

审批包包含：设备、测点趋势、阈值版本、相似历史、建议动作、风险和 Trace。审批人可以批准、拒绝或要求更多证据。

执行维修后，将实际根因、处理动作和结果写回 EAM，经审核后用于评测和知识更新，不能让 Agent 自动把自己的推测写成事实。

## 48.8 评测与上线

指标包括：Precision/Recall、平均提前量、误停机建议率、漏报率、MTTR、非计划停机时间、工单接受率和安全事件。

上线顺序：历史回放 → Shadow Mode → 只生成诊断 → 创建工单草稿 → 受审批执行。跨季节、负载、设备型号和传感器故障做分层评测。

## 48.9 常见踩坑

- 忽略单位、时区和传感器质量码；
- 用统一阈值覆盖所有型号；
- 让 Agent 直接连接 PLC；
- 把相关异常当作故障根因；
- 云服务失败影响现场安全逻辑；
- 维修结果未经审核就写入长期知识；
- 只优化模型准确率，不衡量停机业务影响。

## 48.10 生产化清单

- Asset/Signal/Unit Contract；
- OT 网络分区与只读 Gateway；
- 规则、ML、LLM 职责分离；
- 安全关键动作人工审批；
- 阈值、模型和手册版本化；
- Historian、EAM、MES Evidence 可关联；
- 离线回放和 Shadow Mode；
- 断网、降级、回滚与应急演练。

## Summary

制造业 Agent 的价值是缩短异常到维护决策的链路，同时尊重 OT 的安全和实时边界。MVP 只生成可审计工单提案，清晰展示了“Agent 建议、确定性系统保护、人负责批准”。

## References

[1] NIST. SP 800-82 Rev. 3, Guide to Operational Technology Security.
https://csrc.nist.gov/pubs/sp/800/82/r3/final

[2] NIST. AI Risk Management Framework.
https://airc.nist.gov/airmf-resources/airmf/
