# Chapter 18 Observation：把工具返回转换成可用证据

Part III Agent Architecture —— Agent 内部如何工作

Version: 2026-07

Last Updated: 2026-07-31

## Core Question

Tool Result 为什么不能直接追加到 Prompt？Runtime 如何处理错误、超长结果、来源、敏感数据和 Prompt Injection？

## Chapter Conclusion

Observation 是 Agent 对外部执行结果的标准化认识，不等于原始返回。Observation Adapter 负责校验、分类、裁剪、脱敏、标注来源和建立信任边界。

## Learning Objectives

- 区分 Tool Result、Observation 与 Evidence
- 设计统一 Observation schema
- 分类 transient、validation、permission 和 business error
- 处理结果大小、敏感数据与不可信指令
- 运行 ToolResult → Observation MVP

## 18.1 三层对象

```text
Tool Result
  raw provider/function response
          ↓ normalize
Observation
  status + summary + provenance + trust + retryability
          ↓ verify
Evidence
  supports a Goal criterion or decision
```

工具成功返回只说明调用完成，不说明数据正确，更不说明它支持最终结论。

## 18.2 Observation Contract

建议字段：

```json
{
  "call_id": "call-17",
  "step_id": "query-revenue",
  "status": "success",
  "content": {"revenue": 218000},
  "source": "warehouse.sales_monthly",
  "observed_at": "2026-07-31T10:00:00Z",
  "schema_version": "1",
  "trusted_as_instruction": false,
  "retryable": false
}
```

`trusted_as_instruction` 对外部数据必须为 false。即使数据库返回“忽略上面的规则”，它也只是数据。

## 18.3 Error Taxonomy

| 错误 | 示例 | 默认动作 |
|---|---|---|
| Transient | timeout、rate limit、503 | 有界退避重试 |
| Validation | 参数/schema 不合法 | 修复参数 |
| Permission | scope/tenant 被拒绝 | 终止或人工授权 |
| Not Found | 资源不存在 | 澄清或换路径 |
| Business | 订单已退款 | 更新计划，不盲重试 |
| Quality | 数据过期、样本不足 | 获取新证据 |

错误 taxonomy 应来自 Runtime，不让模型通过错误文本猜测。

## 18.4 结果大小与 Context

工具可能返回百万行、二进制文件或完整日志。Adapter 应：

- 设置 byte/row/token 上限；
- 大结果落对象存储，只返回 handle 与摘要；
- 对表格保留 schema、采样与统计；
- 对日志保留关键窗口和检索接口；
- 记录 truncation，禁止静默截断；
- 将完整内容与模型 Context 解耦。

## 18.5 安全边界

Observation 处理至少包括：

- PII/secret 检测与脱敏；
- source allowlist 与 provenance；
- HTML/Markdown 中外链和脚本清理；
- Prompt Injection 标记；
- 文件 MIME/type 检查；
- 结果 schema 与业务不变量；
- 错误信息去除内部栈和凭证。

Prompt 提醒只是纵深防御，不能替代这些确定性控制。

## 18.6 工具/协议结果对比

| 来源 | 原始结果形态 | Runtime 关注点 |
|---|---|---|
| OpenAI function tool | tool output 与 call id | 关联调用、错误、敏感 trace |
| Anthropic tool use | tool_result content block | block 顺序、错误标记、大小 |
| Gemini function calling | function response | 调用关联与 SDK 自动循环 |
| MCP | content array / structured content | content type、server trust、schema |
| LangGraph ToolNode | ToolMessage / state update | error handling、state merge |
| REST/gRPC | status/body/metadata | HTTP/RPC 错误与重试语义 |

统一 Observation 可以把供应商细节隔离在 Adapter 层。

## 18.7 业务案例：SQL Agent

SQL 执行结果不能直接送给模型。Adapter 应附加：

- 实际执行的 query hash；
- 数据源与 snapshot 时间；
- row count 和 truncation；
- 列类型与敏感等级；
- 查询耗时和扫描量；
- 只读策略验证结果；
- 结果样本或存储 handle。

最终报告引用 Observation ID，而不是复制无法追溯的数字。

## 18.8 Python MVP

```bash
python chapters/chapter18/example.py
python -m unittest discover -s chapters/chapter18 -p "test_*.py"
```

MVP 实现统一状态、来源、长度限制、外部数据非指令标记和 retryable error 分类。

## Production Checklist

- [ ] 原始结果与 Observation 分层保存
- [ ] Observation 关联 run/step/call ID
- [ ] 结果有 schema、source、time 和 version
- [ ] 大结果落存储，不直接进 Context
- [ ] 外部内容永远不提升为 instruction
- [ ] 错误使用稳定 reason code
- [ ] 脱敏后才进入模型和 trace
- [ ] Evidence 必须通过独立验证

## Summary

Observation Adapter 是外部世界进入 Agent 的数据防火墙。它决定模型看到的是可控证据，还是未经处理的噪声和攻击载荷。

## Notes

不同供应商对 Tool Result 的消息结构不同，本章的 Observation 是应用内部统一契约，不是外部协议标准。

## References

[1] MCP, Tools.
https://modelcontextprotocol.io/specification/2026-07-28/server/tools

[2] LangChain, Tools.
https://docs.langchain.com/oss/python/langchain/tools

[3] OpenAI Agents SDK, Tracing.
https://openai.github.io/openai-agents-python/tracing/

以上 URL 已在 2026-07-31 核对。
