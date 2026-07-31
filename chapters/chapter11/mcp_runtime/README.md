# MCP Server / Client MVP

`protocol.py` 是零依赖的数据层教学实现；`server.py` 与 `client.py` 使用官方 MCP Python SDK 2.x，暴露 Tool、Resource 和 Prompt。

```bash
python chapters/chapter11/example.py
python -m unittest discover -s chapters/chapter11 -p "test_*.py"

cd chapters/chapter11/mcp_runtime
python -m pip install -r requirements.txt
python client.py
uv run mcp dev server.py
```

`client.py` 使用 SDK 的进程内 transport，便于测试；把 `Client(mcp)` 替换成 `Client("https://host/mcp")` 即可连接 Streamable HTTP 服务。
