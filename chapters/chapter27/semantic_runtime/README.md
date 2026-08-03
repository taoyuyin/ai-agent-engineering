# Semantic Runtime MVP

本模块用受治理的 Metric Catalog 把自然语言数据意图与底层 SQL 解耦。

## 实现内容

- `MetricDefinition` 声明 Expression、Source、Dimension、Owner、Unit 和 Version；
- Identifier 白名单防止 Catalog 注入；
- `MetricRequest` 只引用注册 Metric、Dimension 和 Filter；
- `compile()` 生成参数化 Query Plan；
- 未知指标、维度和筛选条件 Fail Closed。

## 模型关系

模型可以把问题转换为 `MetricRequest` 候选；Semantic Layer 校验并编译 SQL。模型不能直接定义生产指标或绕过 Catalog 查询敏感列。

```bash
python chapters/chapter27/example.py
python -m unittest discover -s chapters/chapter27 -p "test_*.py"
```

教学 SQL Builder 不是完整 Parser；生产环境还需 AST、RLS、Join Graph 和 Warehouse Quota。正文见 [Chapter 27](../README.md)。
