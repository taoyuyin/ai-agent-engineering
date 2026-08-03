# SQL Agent Tests

本目录验证完整业务链而不只验证 SQL 字符串。

测试应覆盖：正常指标查询、Schema Tool、Tenant 隔离、缺少 Scope、非只读 SQL、参数绑定、Trace 顺序和 Evidence。Fixture 来自 [`../data/`](../data/README.md)，不能依赖开发者本机数据库。

```bash
pytest examples/sql-agent/tests
```

本测试命令需要先按父目录 README 安装依赖。生产化后还应增加 PostgreSQL/RLS 集成测试、SQL AST、超时、扫描预算和 Text-to-SQL Eval。
