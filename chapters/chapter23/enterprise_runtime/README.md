# Enterprise Agent Runtime MVP

用 composition root 串起请求身份、Embedding Gateway、租户隔离检索、Context Compiler、Tool Gateway、证据和审计边界。

完整示例输入一个租户销售目标，依次执行 scope authorization、语义检索、Context Budget、受控工具查询、证据组装和审计。输出带 embedding model、context、业务 evidence 与完整事件。

对应 Part II：Token、Embedding、Context、Reasoning/Structured Goal、Function Calling 和 MCP Gateway 的完整架构投影。

```bash
python chapters/chapter23/example.py
python -m unittest discover -s chapters/chapter23 -p "test_*.py"
```
