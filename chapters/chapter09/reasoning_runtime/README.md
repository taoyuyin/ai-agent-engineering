# Reasoning Runtime MVP

示例把推理工程化为有边界的 `plan → action → observation → verification` 状态，而不是记录模型私有思维链。

```bash
python chapters/chapter09/example.py
python -m unittest discover -s chapters/chapter09 -p "test_*.py"
```

真实项目可把确定性计划器替换为模型适配器，但应保留步数预算、工具白名单、证据验证和结构化 trace。
