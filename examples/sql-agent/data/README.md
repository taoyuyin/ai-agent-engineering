# SQL Agent Data

本目录保存 SQL Agent 的可公开、可重复 Fixture：

- `schema.sql`：SQLite 教学 Schema；
- `seed.sql`：包含多租户和区域销售数据的固定样例。

数据只用于验证 Schema Discovery、参数化查询、Tenant Filter 和 Evidence，不代表真实企业数据模型。修改 Fixture 时必须同步测试期望与 README 示例结果；跨租户样例不能删除，因为它用于验证数据隔离。

运行入口会创建本地数据库，生成文件不应提交。生产环境应使用独立只读账号、RLS、Statement Timeout 和受治理 Semantic Layer。
