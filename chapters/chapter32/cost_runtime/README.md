# Cost Runtime MVP

本模块实现 Capability-aware Model Routing 与请求级预算账本。

## 实现内容

- `ModelProfile` 声明 Capability、Quality Tier 和 Token 单价；
- 分开估算 Uncached Input、Cached Input 和 Output；
- `RouteRequest` 声明任务能力、质量和 Token 预测；
- Router 选择预算内最便宜的合格模型；
- `BudgetLedger` 拒绝超出剩余预算的记录。

## 模型关系

Model Profile 是配置和评测结果，不由模型自报。示例价格为教学输入，不代表实时厂商价格；生产系统应版本化价格、实际 Usage 和汇率。

```bash
python chapters/chapter32/example.py
python -m unittest discover -s chapters/chapter32 -p "test_*.py"
```

生产升级加入质量预测、Fallback、Tenant Quota、月度预算和成本归因。正文见 [Chapter 32](../README.md)。
