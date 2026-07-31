# Context Runtime MVP

在总预算之外增加 section quota，并保留内容信任边界和丢弃原因。

完整示例把 Policy、Evidence 和 History 作为候选输入，先按当前任务做轻量语义排序，再执行 section/total token budget，输出可审计的 Context 和 dropped reason。

对应 Part II：Embedding 候选排序、Token Estimation、Context Window 与信任边界。

```bash
python chapters/chapter17/example.py
python -m unittest discover -s chapters/chapter17 -p "test_*.py"
```
