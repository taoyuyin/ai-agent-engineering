# SQL Agent Package

该包是仓库当前唯一完整企业案例，复用根目录 `framework` Runtime。

## 模块职责

| 模块 | 职责 |
| --- | --- |
| `application.py` | 组合 Runtime、Planner、Tool 和 Answer |
| `planner.py` | 将业务目标转换为受限查询 Plan |
| `tools.py` | Schema 和只读 SQL Tool |
| `guardrails.py` | SQL 与权限控制 |
| `database.py` | SQLite Fixture 与连接边界 |
| `answer.py` | 基于 Observation 生成答案和 Evidence |
| `api.py` | FastAPI 服务入口 |

模型或规则 Planner 只能生成候选查询；Tool Registry、Policy、参数化 SQL 和数据库权限决定是否执行。包内模块不应从 Prompt 读取 Tenant 或真实 Scope。

安装、CLI、API、Docker 和生产升级见父目录 [README](../README.md)。
