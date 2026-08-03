# Prompt Runtime MVP

本模块把 Prompt 建模为不可变、可版本化的工程资产，而不是散落在代码中的字符串。

## 实现内容

- `PromptTemplate`：ID、Version、System、Template、Variables 和 Output Schema；
- `validate()`：模板变量与声明必须完全一致；
- `checksum`：为 Prompt 内容生成稳定短 Hash；
- `PromptRegistry`：注册不可变版本、切换 Active Version；
- `render()`：拒绝缺失或额外变量，并返回版本元数据。

## 模型关系

Rendered Prompt 是模型请求的输入；Registry 不调用模型。这样可以在不消耗 Token 的情况下验证版本、变量和回滚契约，再由 Provider Adapter 发送。

```bash
python chapters/chapter24/example.py
python -m unittest discover -s chapters/chapter24 -p "test_*.py"
```

生产系统应增加持久 Registry、Owner、审批、Eval、Canary 和访问控制。正文见 [Chapter 24](../README.md)。
