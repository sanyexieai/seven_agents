"""
MCP (Model Context Protocol) 工具模块
提供与外部模型和服务的工具调用功能

此文件所有MCP工具（本地和远程）均通过json配置动态加载和注册，无任何硬编码import。
"""

import os
import json
import subprocess
import importlib
from .mcp import (
    MCPTool,
    MCPClient,
    MCPToolManager,
    FileOperationTool,
    APICallTool,
)

# 创建默认的MCP工具管理器实例
mcp_tool_manager = MCPToolManager()

# 动态加载MCP服务器配置并注册MCPClient和本地工具
MCP_SERVERS_CONFIG = os.environ.get("MCP_SERVERS_CONFIG", "mcp_servers.json")
if os.path.exists(MCP_SERVERS_CONFIG):
    with open(MCP_SERVERS_CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    # 注册远程MCP服务
    for name, server in config.get("mcpServers", {}).items():
        if server.get("command"):
            subprocess.Popen(
                [server["command"]] + server.get("args", []),
                env={**server.get("env", {}), **os.environ}
            )
        port = server.get("env", {}).get("PORT", "8080")
        client = MCPClient(server_url=f"http://localhost:{port}")
        mcp_tool_manager.register_mcp_client(name, client)
    # 注册本地Python工具
    for tool_name, tool_info in config.get("localTools", {}).items():
        module = importlib.import_module(tool_info["module"])
        tool_cls = getattr(module, tool_info["class"])
        tool_instance = tool_cls()
        mcp_tool_manager.register_tool(tool_instance)


def get_all_mcp_tool_descriptions():
    """
    获取所有已注册MCP工具的描述信息（含name、description、parameters），便于传递给LLM。
    :return: List[Dict]
    """
    return [
        {
            "name": tool.name,
            "description": getattr(tool, "description", ""),
            "parameters": tool.get_parameters() if hasattr(tool, "get_parameters") else {}
        }
        for tool in mcp_tool_manager.tools.values()
    ]

def get_all_mcp_tools():
    """
    获取所有已注册的MCP工具对象（便于agent自动集成）
    :return: List[MCPTool]
    """
    return list(mcp_tool_manager.tools.values())

def call_mcp_tool(tool_name, params):
    """
    统一调用MCP工具
    :param tool_name: 工具名称
    :param params: 参数dict
    :return: 工具执行结果
    """
    tool = mcp_tool_manager.tools.get(tool_name)
    if not tool:
        raise ValueError(f"MCP工具未注册: {tool_name}")
    # 调试输出工具类型和属性
    print(f"[MCP调试] 工具名: {tool_name}, 类型: {type(tool)}, 属性: {dir(tool)}")
    # 兼容本地和远程MCP工具
    if hasattr(tool, "run") and callable(tool.run):
        return tool.run(**params)
    elif callable(tool):
        return tool(**params)
    else:
        raise TypeError(f"工具 {tool_name} 不可调用，实际类型: {type(tool)}，属性: {dir(tool)}")

__all__ = [
    "MCPTool",
    "MCPClient",
    "MCPToolManager", 
    "FileOperationTool",
    "APICallTool",
    "mcp_tool_manager",
    "get_all_mcp_tool_descriptions",
    "get_all_mcp_tools",
    "call_mcp_tool"
] 