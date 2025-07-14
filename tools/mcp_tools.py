"""
MCP (Model Context Protocol) 工具模块
提供与外部模型和服务的工具调用功能
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


class WebSearchTool(MCPTool):
    """网络搜索工具"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            name="web_search",
            description="搜索网络信息",
            config={"api_key": api_key}
        )
    
    def execute(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """执行网络搜索"""
        # 这里可以集成各种搜索API，如Google、Bing等
        # 示例实现
        return {
            "query": query,
            "results": [
                {
                    "title": f"搜索结果 {i}",
                    "url": f"https://example.com/result{i}",
                    "snippet": f"这是关于 {query} 的搜索结果 {i}"
                }
                for i in range(1, max_results + 1)
            ],
            "total_results": max_results
        }
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询"
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大结果数量",
                    "default": 5
                }
            },
            "required": ["query"]
        }


class FileOperationTool(MCPTool):
    """文件操作工具"""
    
    def __init__(self):
        super().__init__(
            name="file_operation",
            description="执行文件读写操作"
        )
    
    def execute(self, operation: str, file_path: str, content: str = None) -> Dict[str, Any]:
        """执行文件操作"""
        try:
            if operation == "read":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"success": True, "content": content}
            
            elif operation == "write":
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content or "")
                return {"success": True, "message": f"文件 {file_path} 写入成功"}
            
            elif operation == "append":
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(content or "")
                return {"success": True, "message": f"文件 {file_path} 追加成功"}
            
            else:
                return {"success": False, "error": f"不支持的操作: {operation}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "append"],
                    "description": "文件操作类型"
                },
                "file_path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "content": {
                    "type": "string",
                    "description": "文件内容（写操作时使用）"
                }
            },
            "required": ["operation", "file_path"]
        }


class APICallTool(MCPTool):
    """API调用工具"""
    
    def __init__(self):
        super().__init__(
            name="api_call",
            description="调用外部API"
        )
    
    def execute(self, method: str, url: str, headers: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """执行API调用"""
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers or {},
                json=data,
                timeout=30
            )
            return {
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "description": "HTTP方法"
                },
                "url": {
                    "type": "string",
                    "description": "API URL"
                },
                "headers": {
                    "type": "object",
                    "description": "请求头"
                },
                "data": {
                    "type": "object",
                    "description": "请求数据"
                }
            },
            "required": ["method", "url"]
        }


class MCPToolManager:
    """MCP工具管理器"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.mcp_clients: Dict[str, MCPClient] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        self.register_tool(WebSearchTool())
        self.register_tool(FileOperationTool())
        self.register_tool(APICallTool())
    
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