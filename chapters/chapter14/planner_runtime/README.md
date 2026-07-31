# Planner Runtime MVP

实现依赖图、ready queue、完成状态、失败修复与循环依赖检查。

完整示例创建 load → analyze → report 三步 DAG，逐步取得 ready task、写回结果并完成计划。相同 Plan IR 可以接收 Reasoning Model 的结构化提案，但循环依赖和执行顺序由 Runtime 检查。

对应 Part II：Reasoning、Structured Output、Context 中的当前 Observation。

```bash
python chapters/chapter14/example.py
python -m unittest discover -s chapters/chapter14 -p "test_*.py"
```
