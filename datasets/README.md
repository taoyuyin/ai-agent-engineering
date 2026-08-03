# Datasets

`datasets/` 保存教程示例和评测使用的可公开、可版本化数据。业务案例自己的小型 Fixture 可以留在 `examples/<agent>/data/`；被多个章节复用的数据才进入本目录。

## 数据集契约

每个数据集应使用独立子目录并包含：

```text
datasets/<dataset-name>/
├── README.md          # 来源、License、字段和使用限制
├── manifest.json      # 版本、校验和、行数和拆分
├── raw/               # 允许提交时保存不可变原始数据
├── processed/         # 可复现转换结果
└── scripts/           # 下载、清洗和校验脚本
```

Manifest 至少记录：`name`、`version`、`source`、`license`、`checksum`、`created_at`、`schema_version` 和 `splits`。训练、开发和测试集必须按稳定 ID 切分，避免同一文档或同一用户泄漏到多个集合。

## 数据治理

- 不提交私有数据、密钥、个人隐私、客户内容或受合同限制的数据；
- 未知 License 的数据不能默认作为公开数据发布；
- 合成数据必须标注生成方法和与真实分布的差异；
- 任何清洗、脱敏和切分都要有可复现脚本；
- 原始数据不可静默覆盖，使用新版本发布；
- 删除请求和保留期限要进入数据生命周期设计。

## 与评测的关系

`datasets/` 保存输入与 Ground Truth，`evaluation/` 定义评分方法，`benchmark/` 固定被测系统和运行配置。三者共同构成可复现实验，不能只保存最终分数。

当前仓库的可运行 SQL Fixture 位于 [`examples/sql-agent/data/`](../examples/sql-agent/data/)。本目录暂不复制该数据，避免出现两个不一致版本。
