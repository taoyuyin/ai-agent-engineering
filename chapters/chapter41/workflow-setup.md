# Dify Workflow Setup

本文件描述 Chapter 41 Python Client 所依赖的 Dify Workflow。界面名称可能随 Dify 版本调整，但输入输出 Contract 必须与 `workflow-contract.json` 保持一致。

## 1. 创建应用

1. 在 Dify Studio 创建一个空白 **Workflow** 应用。
2. 在 Start Node 创建三个输入变量：
   - `question`：String，Required；
   - `tenant_id`：String，Required；
   - `scopes`：String，Required。
3. 不要在 Workflow 中保存真实用户 Token；调用方只使用服务端 API Key。

## 2. 添加授权分支

增加 If/Else Node：

```text
scopes contains "sales:read"
```

未授权分支直接连接 End Node：

```text
answer = "permission denied"
evidence_source = ""
```

这个节点用于演示 Workflow 控制流。生产环境的最终授权必须由受治理数据 API 根据服务身份、用户身份和 `tenant_id` 再次执行。

## 3. 配置数据 Tool

在授权分支调用企业数据 API。推荐使用 Tool 或 HTTP Request Node，输入：

```json
{
  "question": "{{question}}",
  "tenant_id": "{{tenant_id}}"
}
```

数据 API 返回：

```json
{
  "year": 2025,
  "metric": "net_revenue",
  "rows": [
    {"region": "east", "net_revenue": 338000.0, "order_count": 2},
    {"region": "north", "net_revenue": 149000.0, "order_count": 2},
    {"region": "south", "net_revenue": 148000.0, "order_count": 2}
  ],
  "source": "demo.sales_orders"
}
```

数据 API 应负责：

- 校验服务凭证和最终用户身份；
- 强制 `tenant_id` 数据隔离；
- 限制可访问指标；
- 返回稳定 Schema 和证据源；
- 记录审计日志。

## 4. 配置 LLM Node

System Prompt：

```text
你是企业销售分析 Agent。
只能使用输入中的 tool_result 回答，禁止补充或猜测任何数值。
回答必须说明年份、指标、区域结果和证据源。
```

User Prompt：

```text
用户问题：
{{question}}

受治理工具结果：
{{tool_result}}
```

模型配置、Prompt 和 Tool Schema 都应在发布记录中版本化。

## 5. 配置输出

授权分支的 End Node 输出：

```text
answer = LLM Node text
evidence_source = Tool result source
```

最终两个分支都必须满足：

- `answer`：String；
- `evidence_source`：String。

## 6. 发布与验证

1. 使用 Preview 分别验证授权和拒绝分支。
2. 发布 Workflow。
3. 在 API Access 页面创建应用 API Key。
4. 将 API Key 放入后端 Secret Manager。
5. 配置环境变量后运行：

```bash
export DIFY_BASE_URL="https://api.dify.ai"
export DIFY_API_KEY="<your-workflow-api-key>"
python example.py "查询 2025 年各区域净销售额"
```

## 7. 纳入 Git

在目标 Dify 版本中完成配置后，导出真实应用 DSL 并提交到本目录，例如 `dify-workflow.yml`。不要手工维护与实例版本不匹配的 DSL。

每次变更至少审查：

- 输入输出 Contract 是否兼容；
- 模型、Prompt 和参数是否变化；
- Tool URL、凭证作用域和超时；
- 新节点是否能访问敏感数据；
- 授权、失败与空结果分支是否仍通过。
