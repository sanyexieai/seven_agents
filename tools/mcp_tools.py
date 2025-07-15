"""
MCP (Model Context Protocol) 工具模块
提供与外部模型和服务的工具调用功能

本文件只保留MCP协议推荐的远程调用方式。
"""

import os
import json
import asyncio
import logging
from typing import Any, Dict, Optional, List

logger = logging.getLogger("mcp_tools")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

def load_mcp_servers_config(config_path=None) -> dict:
    config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'mcp_servers.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"无法读取mcp_servers.json: {e}")
        return {}

def get_server_url(server_name: Optional[str] = None) -> str:
    config = load_mcp_servers_config()
    servers = config.get('mcpServers', {})
    if not servers:
        raise RuntimeError("mcpServers.json未配置任何MCP服务")
    if server_name and server_name in servers:
        return servers[server_name]['url']
    # 默认取第一个
    return next(iter(servers.values()))['url']

def get_transport_type(url: str) -> str:
    if url.endswith('/sse'):
        return 'sse'
    elif url.endswith('/stdio'):
        return 'stdio'
    else:
        return 'streamable_http'

async def _call_tool_async(tool_name, params, method=None, server_name=None, retries=2, delay=1.0):
    url = get_server_url(server_name)
    transport = get_transport_type(url)
    remote_params = dict(params)
    if method is not None:
        remote_params["method"] = method

    from mcp.client.session import ClientSession
    if transport == 'sse':
        from mcp.client.sse import sse_client
        async with sse_client(url, timeout=60) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                for attempt in range(retries):
                    try:
                        return await session.call_tool(tool_name, arguments=remote_params)
                    except Exception as e:
                        logger.warning(f"调用失败: {e}，重试{attempt+1}/{retries}")
                        if attempt < retries - 1:
                            await asyncio.sleep(delay)
                        else:
                            raise
    else:
        from mcp.client.streamable_http import streamablehttp_client
        async with streamablehttp_client(url, timeout=60) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                for attempt in range(retries):
                    try:
                        return await session.call_tool(tool_name, arguments=remote_params)
                    except Exception as e:
                        logger.warning(f"调用失败: {e}，重试{attempt+1}/{retries}")
                        if attempt < retries - 1:
                            await asyncio.sleep(delay)
                        else:
                            raise

def call_mcp_tool(tool_name, params, method=None, server_name=None, **kwargs):
    """同步调用MCP工具，自动选服务和协议"""
    return asyncio.run(_call_tool_async(tool_name, params, method, server_name, **kwargs))

async def list_mcp_tools_async(server_name=None):
    url = get_server_url(server_name)
    transport = get_transport_type(url)
    from mcp.client.session import ClientSession
    if transport == 'sse':
        from mcp.client.sse import sse_client
        async with sse_client(url, timeout=60) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.list_tools()
                return [tool.model_dump() for tool in getattr(result, "tools", [])]
    else:
        from mcp.client.streamable_http import streamablehttp_client
        async with streamablehttp_client(url, timeout=60) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.list_tools()
                return [tool.model_dump() for tool in getattr(result, "tools", [])]

def list_mcp_tools(server_name=None):
    return asyncio.run(list_mcp_tools_async(server_name))

def format_tool_schema(tool: dict) -> str:
    """格式化工具schema，便于LLM提示词"""
    args_desc = []
    props = tool.get("inputSchema", {}).get("properties", {})
    required = tool.get("inputSchema", {}).get("required", [])
    for param, info in props.items():
        desc = f"- {param}: {info.get('description', 'No description')}"
        if param in required:
            desc += " (required)"
        args_desc.append(desc)
    output = f"Tool: {tool.get('name')}\n"
    if tool.get('title'):
        output += f"User-readable title: {tool['title']}\n"
    output += f"Description: {tool.get('description')}\nArguments:\n" + "\n".join(args_desc)
    return output

__all__ = [
    "call_mcp_tool",
    "list_mcp_tools",
    "format_tool_schema"
] 