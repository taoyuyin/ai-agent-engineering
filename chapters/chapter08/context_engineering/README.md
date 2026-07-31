# Context Engineering MVP

这个项目实现一个不依赖第三方库的 `ContextAssembler`：预留输出空间、优先保留必需信息、去重、隔离不可信观察结果，并记录丢弃原因。

```bash
python chapters/chapter08/example.py
python -m unittest discover -s chapters/chapter08 -p "test_*.py"
```

生产环境应把字符估算替换成目标模型的 tokenizer，并增加检索相关性、时效性、摘要质量与注入检测。
