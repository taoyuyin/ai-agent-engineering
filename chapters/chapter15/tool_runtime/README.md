# Tool Runtime MVP

先用确定性 Embedding 从工具描述中召回语义候选，再按 capability、scope、read-only 和 cost 路由，并在执行边界再次授权。

完整示例注册销售摘要和管理员 SQL 两个工具。“分析华东收入趋势”只能发现当前身份有权看到的候选，模型得到 schema 后可提出 Function Call，Runtime 在真正执行时再次检查 scope。

对应 Part II：Embedding Tool Discovery、Function Calling、MCP/Tool Gateway、Context Schema Budget。

```bash
python chapters/chapter15/example.py
python -m unittest discover -s chapters/chapter15 -p "test_*.py"
```
