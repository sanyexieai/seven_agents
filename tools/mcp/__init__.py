# -*- coding: utf-8 -*-
"""
MCP (Model Context Protocol) 工具包
提供与外部模型和服务的工具调用功能
"""

from mcp.server.fastmcp import FastMCP
mcp = FastMCP("AllToolsDemo")

__all__ = ["mcp"] 