# -*- coding: utf-8 -*-
"""
MCP基础类和工具管理器
"""

import json
import requests
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class MCPTool(ABC):
    """MCP工具基类"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.config = config or {}
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """执行工具调用"""
        pass
    
    def run(self, **params):
        """统一run接口，默认调用execute"""
        return self.execute(**params)

    def get_schema(self) -> Dict[str, Any]:
        """获取工具调用模式"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters()
        }
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """获取参数定义"""
        pass


class MCPClient:
    """MCP客户端，用于与外部MCP服务器通信"""
    
    def __init__(self, server_url: str, api_key: str = None):
        self.server_url = server_url
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用远程MCP工具"""
        try:
            response = self.session.post(
                f"{self.server_url}/tools/{tool_name}",
                json=parameters,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """获取可用的工具列表"""
        try:
            response = self.session.get(f"{self.server_url}/tools")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return []


class MCPToolManager:
    """MCP工具管理器"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.mcp_clients: Dict[str, MCPClient] = {}
        # 移除自动注册默认工具，所有工具通过json配置注册
    
    def register_tool(self, tool: MCPTool):
        """注册工具"""
        self.tools[tool.name] = tool
    
    def register_mcp_client(self, name: str, client: MCPClient):
        """注册MCP客户端"""
        self.mcp_clients[name] = client
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """获取工具"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        return [tool.get_schema() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用"""
        tool = self.get_tool(tool_name)
        if tool:
            return tool.execute(**parameters)
        else:
            return {"error": f"工具 {tool_name} 不存在", "success": False}
    
    def call_remote_tool(self, client_name: str, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """调用远程工具"""
        client = self.mcp_clients.get(client_name)
        if client:
            return client.call_tool(tool_name, parameters)
        else:
            return {"error": f"MCP客户端 {client_name} 不存在", "success": False}


# 全局工具管理器实例
mcp_tool_manager = MCPToolManager() 