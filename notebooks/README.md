# Notebooks

`notebooks/` 用于探索性实验、数据分析和教学可视化，不作为生产 Runtime 的唯一实现位置。

## 适用内容

- Token、Embedding、Retrieval 和 Evaluation 的可视化实验；
- Benchmark 结果分析和误差切片；
- 数据质量检查与合成数据验证；
- 需要逐步展示中间结果的教学实验。

## Notebook 规范

1. 文件名使用 `NN-topic.ipynb`，开头写目标、输入数据和环境；
2. 固定随机种子并记录数据、模型和 Prompt 版本；
3. 从仓库模块导入实现，不在单元格复制另一套 Runtime；
4. 不写入密钥、个人路径和不可公开输出；
5. “Run All” 应能从干净 Kernel 完成；
6. 大型结果写入可忽略目录，不提交二进制缓存；
7. 结论同时记录失败案例和适用边界。

## 从实验到工程

Notebook 中验证有效的算法应迁移到 `framework/`、`evaluation/` 或对应 Chapter，并补充测试、类型、CLI 和 README。Notebook 保留研究过程，工程目录保留稳定 Contract。

当前目录还没有正式 Notebook；首次加入时应同时提供独立依赖或在文件头声明使用根目录开发环境。
