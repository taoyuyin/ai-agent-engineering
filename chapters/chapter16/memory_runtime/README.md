# Memory Runtime MVP

实现 memory type、版本更新、租户/主体命名空间、确定性 Embedding 检索与遗忘。

完整示例写入用户偏好和历史事件，先按 tenant/subject 隔离，再组合词项、向量相似度和 confidence 排序。更新会提升版本，forget 同时移除记录和向量。

对应 Part II：Embedding、Vector Retrieval、Token/Context Budget。

```bash
python chapters/chapter16/example.py
python -m unittest discover -s chapters/chapter16 -p "test_*.py"
```
