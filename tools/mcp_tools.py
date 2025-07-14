"""
MCP (Model Context Protocol) 工具模块
提供与外部模型和服务的工具调用功能

此文件现在从 tools.mcp 包导入所有MCP工具
"""

# 从新的mcp包导入所有工具
from .mcp import (
    MCPTool,
    MCPClient,
    MCPToolManager,
    FileOperationTool,
    APICallTool,
)
from .mcp.google_news_search import GoogleNewsSearchTool

# 创建默认的MCP工具管理器实例
mcp_tool_manager = MCPToolManager()
mcp_tool_manager.register_tool(GoogleNewsSearchTool())

__all__ = [
    "MCPTool",
    "MCPClient",
    "MCPToolManager", 
    "FileOperationTool",
    "APICallTool",
    "GoogleNewsSearchTool",
    "mcp_tool_manager"
] 