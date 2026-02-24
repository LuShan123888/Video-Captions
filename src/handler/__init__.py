"""
Handler 层 - 接入层模块

处理 CLI 和 MCP 协议差异
"""

from handler.cli import main as cli_main
from handler.mcp import main as mcp_main, mcp

__all__ = [
    "cli_main",
    "mcp_main",
    "mcp",
]
