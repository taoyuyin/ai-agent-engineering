# Goal Runtime MVP

把自然语言目标收敛为 objective、constraints、success criteria、allowed tools 与 risk level。

完整示例把结构化模型提案编译为 `GoalSpec`，再使用独立 evidence map 验收成功标准。缺少 objective、可测试标准或合法风险等级时 fail closed。

对应 Part II：Reasoning 用于理解，Structured Output 用于提案，Runtime schema 用于确定性验证。

```bash
python chapters/chapter13/example.py
python -m unittest discover -s chapters/chapter13 -p "test_*.py"
```
