# Function Calling Runtime MVP

该项目用统一工具定义生成不同供应商的 schema，并在真正执行前完成参数校验、权限检查、副作用审批和调用幂等。

```bash
python chapters/chapter10/example.py
python -m unittest discover -s chapters/chapter10 -p "test_*.py"
```

本实现只覆盖教学所需的 JSON Schema 子集；生产环境应使用成熟验证器并加入超时、速率限制、审计落库和密钥隔离。
