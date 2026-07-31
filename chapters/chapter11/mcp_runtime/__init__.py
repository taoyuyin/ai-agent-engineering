"""Dependency-free MCP protocol teaching implementation."""

from .protocol import InProcessMCPClient, MetricsMCPServer, ProtocolError

__all__ = ["InProcessMCPClient", "MetricsMCPServer", "ProtocolError"]
