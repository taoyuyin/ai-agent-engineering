# Framework Development

## 环境初始化

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

Windows PowerShell 激活命令：

```powershell
.venv\Scripts\Activate.ps1
```

## 建议的质量检查

```bash
pytest
ruff check framework examples/sql-agent
mypy framework
```

这些命令应进入 CI。新增组件至少覆盖：

- 正常执行；
- Schema 拒绝；
- Scope 拒绝；
- Tool 失败和重试上限；
- Tenant 隔离；
- Evidence 与 Trace 完整性。

## 新增 Tool

1. 用 Pydantic 定义输入契约。
2. 实现只接收已校验对象的 Handler。
3. 声明 `required_scopes` 和 `risk`。
4. 注册到业务 Agent 的 `ToolRegistry`。
5. 测试正常、越权和异常路径。

Tool Handler 不应读取 Prompt 来决定权限，也不应接受模型直接传入的 `tenant_id` 覆盖调用上下文。

## 新增业务 Agent

每个业务 Agent 建议保持下面的结构：

```text
examples/<agent>/
├── README.md
├── requirements.txt
├── <agent_package>/
│   ├── application.py
│   ├── planner.py
│   ├── tools.py
│   ├── answer.py
│   └── api.py
├── data/
├── tests/
└── Dockerfile
```

业务包依赖 `framework`，`framework` 不反向依赖业务包。

## 依赖策略

- Runtime 核心保持最少依赖。
- 厂商 SDK 放到 `integrations/` 或业务案例 requirements 中。
- 依赖使用兼容版本区间，不在教材中绑定瞬时 patch 版本。
- 新依赖必须说明用途、数据边界、License 和可替代方案。
