"""
MCP (Model Context Protocol) 工具模块
提供与外部模型和服务的工具调用功能

本文件只保留MCP协议推荐的远程调用方式。
"""

import asyncio
import json
import logging
import os
import shutil
from contextlib import AsyncExitStack
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

class Configuration:
    def __init__(self) -> None:
        self.load_env()
        self.api_key = os.getenv("LLM_API_KEY")

    @staticmethod
    def load_env() -> None:
        load_dotenv()

    @staticmethod
    def load_config(file_path: str) -> dict:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

class Server:
    def __init__(self, name: str, config: dict) -> None:
        self.name = name
        self.config = config
        self.session: Optional[Any] = None
        self.exit_stack: AsyncExitStack = AsyncExitStack()
        self.is_http = bool(config.get("url"))
        self.url = config.get("url")
        self.transport_type = config.get("transport_type", "streamable_http")

    async def initialize(self) -> None:
        if self.is_http:
            from mcp.client.streamable_http import streamablehttp_client
            from mcp.client.sse import sse_client
            if self.transport_type == "sse":
                client_ctx = sse_client(url=self.url)
                read_stream, write_stream = await self.exit_stack.enter_async_context(client_ctx)
            else:
                client_ctx = streamablehttp_client(url=self.url)
                read_stream, write_stream, _ = await self.exit_stack.enter_async_context(client_ctx)
            session = await self.exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
            await session.initialize()
            self.session = session
            return
        # STDIO 原有逻辑
        command = shutil.which("npx") if self.config.get("command") == "npx" else self.config.get("command")
        if not command:
            raise ValueError("The command must be a valid string and cannot be None.")
        args = self.config.get("args", [])
        env = {**os.environ, **self.config.get("env", {})} if self.config.get("env") else None
        cwd = self.config.get("cwd", None)
        encoding = self.config.get("encoding", "utf-8")
        encoding_error_handler = self.config.get("encoding_error_handler", "strict")
        from collections import namedtuple
        StdioParams = namedtuple('StdioParams', [
            'command', 'args', 'env', 'cwd', 'encoding', 'encoding_error_handler'
        ])
        server_params = StdioParams(
            command=command, args=args, env=env, cwd=cwd, encoding=encoding, encoding_error_handler=encoding_error_handler
        )
        try:
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self.session = session
        except Exception as e:
            logging.error(f"Error initializing server {self.name}: {e}")
            await self.cleanup()
            raise

    async def list_tools(self) -> List[dict]:
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")
        tools_response = await self.session.list_tools()
        # 兼容不同MCP实现，提取tools
        if isinstance(tools_response, dict) and "tools" in tools_response:
            tools = tools_response["tools"]
        elif hasattr(tools_response, "tools"):
            tools = getattr(tools_response, "tools")
        elif isinstance(tools_response, list):
            tools = tools_response
        else:
            tools = []
        # 保证所有工具都是dict
        result = []
        for tool in tools:
            if isinstance(tool, dict):
                result.append(tool)
            else:
                # Tool对象或其它，转为dict
                result.append({
                    "name": getattr(tool, "name", None),
                    "description": getattr(tool, "description", ""),
                    "inputSchema": getattr(tool, "inputSchema", {}),
                    "outputSchema": getattr(tool, "outputSchema", {}),
                    "title": getattr(tool, "title", None)
                })
        return result

    async def execute_tool(self, tool_name: str, arguments: dict, retries: int = 2, delay: float = 1.0) -> Any:
        if not self.session:
            raise RuntimeError(f"Server {self.name} not initialized")
        attempt = 0
        while attempt < retries:
            try:
                logging.info(f"Executing {tool_name}...")
                result = await self.session.call_tool(tool_name, arguments)
                return result
            except Exception as e:
                attempt += 1
                logging.warning(f"Error executing tool: {e}. Attempt {attempt} of {retries}.")
                if attempt < retries:
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logging.error("Max retries reached. Failing.")
                    raise

    async def cleanup(self) -> None:
        try:
            await self.exit_stack.aclose()
            self.session = None
        except Exception as e:
            logging.error(f"Error during cleanup of server {self.name}: {e}")

# 兼容原有接口
_config_cache = None
_server_cache = None

def load_mcp_servers_config(config_path=None) -> dict:
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    config_path = config_path or os.path.join(os.path.dirname(__file__), '..', 'mcp_servers.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        _config_cache = json.load(f)
    return _config_cache

def get_server(server_name: Optional[str] = None) -> Server:
    global _server_cache
    if _server_cache is not None and (server_name is None or _server_cache.name == server_name):
        return _server_cache
    config = load_mcp_servers_config()
    servers = config.get('mcpServers', {})
    if not servers:
        raise RuntimeError("mcpServers.json未配置任何MCP服务")
    if server_name and server_name in servers:
        srv = Server(server_name, servers[server_name])
    else:
        name, conf = next(iter(servers.items()))
        srv = Server(name, conf)
    _server_cache = srv
    return srv

async def list_mcp_tools_async(server_name=None):
    server = get_server(server_name)
    await server.initialize()
    tools = await server.list_tools()
    return [
        {
            "name": t.get("name"),
            "description": t.get("description"),
            "inputSchema": t.get("inputSchema"),
            "title": t.get("title")
        } for t in tools
    ]

def list_mcp_tools(server_name=None):
    return asyncio.run(list_mcp_tools_async(server_name))

def format_tool_schema(tool: dict) -> str:
    # 直接用dict格式化
    args_desc = []
    input_schema = tool.get("inputSchema", {})
    if "properties" in input_schema:
        for param_name, param_info in input_schema["properties"].items():
            arg_desc = f"- {param_name}: {param_info.get('description', 'No description')}"
            if param_name in input_schema.get("required", []):
                arg_desc += " (required)"
            args_desc.append(arg_desc)
    output = f"Tool: {tool.get('name')}\n"
    if tool.get('title'):
        output += f"User-readable title: {tool.get('title')}\n"
    output += f"Description: {tool.get('description')}\nArguments:\n" + "\n".join(args_desc)
    output_schema = tool.get("outputSchema", {})
    if output_schema and "properties" in output_schema:
        output += "\nOutput:\n"
        for out_name, out_info in output_schema["properties"].items():
            output += f"- {out_name}: {out_info.get('description', 'No description')}\n"
    return output

async def call_mcp_tool_async(tool_name, params, server_name=None, **kwargs):
    server = get_server(server_name)
    await server.initialize()
    return await server.execute_tool(tool_name, params, **kwargs)

def call_mcp_tool(tool_name, params, server_name=None, **kwargs):
    return asyncio.run(call_mcp_tool_async(tool_name, params, server_name, **kwargs))

__all__ = [
    "call_mcp_tool",
    "list_mcp_tools",
    "format_tool_schema"
] 