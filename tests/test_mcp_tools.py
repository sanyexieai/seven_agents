"""
MCP工具模块的单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.mcp_tools import (
    MCPTool, WebSearchTool, FileOperationTool, APICallTool,
    MCPClient, MCPToolManager
)


class TestMCPTool(unittest.TestCase):
    """测试MCP工具基类"""
    
    def test_mcp_tool_initialization(self):
        """测试MCP工具初始化"""
        class TestTool(MCPTool):
            def execute(self, **kwargs):
                return "test result"
            
            def get_parameters(self):
                return {"type": "object", "properties": {}}
        
        tool = TestTool("test_tool", "测试工具")
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(tool.description, "测试工具")
        self.assertEqual(tool.config, {})
    
    def test_get_schema(self):
        """测试获取工具模式"""
        class TestTool(MCPTool):
            def execute(self, **kwargs):
                return "test result"
            
            def get_parameters(self):
                return {"type": "object", "properties": {}}
        
        tool = TestTool("test_tool", "测试工具")
        schema = tool.get_schema()
        
        self.assertEqual(schema["name"], "test_tool")
        self.assertEqual(schema["description"], "测试工具")
        self.assertEqual(schema["parameters"], {"type": "object", "properties": {}})


class TestWebSearchTool(unittest.TestCase):
    """测试网络搜索工具"""
    
    def setUp(self):
        self.tool = WebSearchTool()
    
    def test_web_search_tool_initialization(self):
        """测试网络搜索工具初始化"""
        self.assertEqual(self.tool.name, "web_search")
        self.assertEqual(self.tool.description, "搜索网络信息")
    
    def test_execute_web_search(self):
        """测试执行网络搜索"""
        result = self.tool.execute(query="人工智能", max_results=3)
        
        self.assertIn("query", result)
        self.assertIn("results", result)
        self.assertIn("total_results", result)
        self.assertEqual(result["query"], "人工智能")
        self.assertEqual(result["total_results"], 3)
        self.assertEqual(len(result["results"]), 3)
    
    def test_get_parameters(self):
        """测试获取参数定义"""
        params = self.tool.get_parameters()
        
        self.assertEqual(params["type"], "object")
        self.assertIn("properties", params)
        self.assertIn("required", params)
        self.assertIn("query", params["properties"])
        self.assertIn("max_results", params["properties"])


class TestFileOperationTool(unittest.TestCase):
    """测试文件操作工具"""
    
    def setUp(self):
        self.tool = FileOperationTool()
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write("测试内容")
        self.temp_file.close()
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_file_operation_tool_initialization(self):
        """测试文件操作工具初始化"""
        self.assertEqual(self.tool.name, "file_operation")
        self.assertEqual(self.tool.description, "执行文件读写操作")
    
    def test_read_file(self):
        """测试读取文件"""
        # 确保文件存在且有内容
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            f.write("测试内容")
        
        result = self.tool.execute(
            operation="read",
            file_path=self.temp_file.name
        )
        
        self.assertTrue(result["success"])
        self.assertIn("content", result)
        self.assertEqual(result["content"], "测试内容")
    
    def test_write_file(self):
        """测试写入文件"""
        test_content = "新的测试内容"
        result = self.tool.execute(
            operation="write",
            file_path=self.temp_file.name,
            content=test_content
        )
        
        self.assertTrue(result["success"])
        
        # 验证文件内容
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, test_content)
    
    def test_append_file(self):
        """测试追加文件"""
        original_content = "原始内容"
        append_content = "追加内容"
        
        # 先写入原始内容
        self.tool.execute(
            operation="write",
            file_path=self.temp_file.name,
            content=original_content
        )
        
        # 追加内容
        result = self.tool.execute(
            operation="append",
            file_path=self.temp_file.name,
            content=append_content
        )
        
        self.assertTrue(result["success"])
        
        # 验证文件内容
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, original_content + append_content)
    
    def test_invalid_operation(self):
        """测试无效操作"""
        result = self.tool.execute(
            operation="invalid",
            file_path=self.temp_file.name
        )
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_nonexistent_file_read(self):
        """测试读取不存在的文件"""
        result = self.tool.execute(
            operation="read",
            file_path="nonexistent_file.txt"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)


class TestAPICallTool(unittest.TestCase):
    """测试API调用工具"""
    
    def setUp(self):
        self.tool = APICallTool()
    
    @patch('tools.mcp.api_call.requests.request')
    def test_api_call_success(self, mock_request):
        """测试成功的API调用"""
        # 模拟成功的响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {"message": "success"}
        mock_request.return_value = mock_response
        
        result = self.tool.execute(
            method="GET",
            url="https://api.example.com/test"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["data"], {"message": "success"})
    
    @patch('tools.mcp.api_call.requests.request')
    def test_api_call_failure(self, mock_request):
        """测试失败的API调用"""
        # 模拟请求异常
        mock_request.side_effect = Exception("Connection error")
        
        result = self.tool.execute(
            method="GET",
            url="https://api.example.com/test"
        )
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)


class TestMCPClient(unittest.TestCase):
    """测试MCP客户端"""
    
    def setUp(self):
        self.client = MCPClient("https://api.example.com")
    
    @patch('tools.mcp.base.requests.Session.post')
    def test_call_tool_success(self, mock_post):
        """测试成功的工具调用"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response
        
        result = self.client.call_tool("test_tool", {"param": "value"})
        
        self.assertEqual(result, {"result": "success"})
    
    @patch('tools.mcp.base.requests.Session.post')
    def test_call_tool_failure(self, mock_post):
        """测试失败的工具调用"""
        mock_post.side_effect = Exception("Network error")
        
        result = self.client.call_tool("test_tool", {"param": "value"})
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    @patch('tools.mcp.base.requests.Session.get')
    def test_list_tools_success(self, mock_get):
        """测试成功获取工具列表"""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"name": "tool1"}, {"name": "tool2"}]
        mock_get.return_value = mock_response
        
        result = self.client.list_tools()
        
        self.assertEqual(result, [{"name": "tool1"}, {"name": "tool2"}])
    
    @patch('tools.mcp.base.requests.Session.get')
    def test_list_tools_failure(self, mock_get):
        """测试失败获取工具列表"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.client.list_tools()
        
        self.assertEqual(result, [])


class TestMCPToolManager(unittest.TestCase):
    """测试MCP工具管理器"""
    
    def setUp(self):
        self.manager = MCPToolManager()
    
    def test_register_tool(self):
        """测试注册工具"""
        class TestTool(MCPTool):
            def execute(self, **kwargs):
                return "test result"
            
            def get_parameters(self):
                return {"type": "object", "properties": {}}
        
        tool = TestTool("test_tool", "测试工具")
        self.manager.register_tool(tool)
        
        self.assertIn("test_tool", self.manager.tools)
        self.assertEqual(self.manager.tools["test_tool"], tool)
    
    def test_get_tool(self):
        """测试获取工具"""
        tool = self.manager.get_tool("web_search")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.name, "web_search")
        
        # 测试获取不存在的工具
        tool = self.manager.get_tool("nonexistent_tool")
        self.assertIsNone(tool)
    
    def test_list_tools(self):
        """测试列出工具"""
        tools = self.manager.list_tools()
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # 检查工具模式格式
        for tool in tools:
            self.assertIn("name", tool)
            self.assertIn("description", tool)
            self.assertIn("parameters", tool)
    
    def test_execute_tool(self):
        """测试执行工具"""
        result = self.manager.execute_tool("web_search", {
            "query": "测试查询",
            "max_results": 2
        })
        
        self.assertIn("query", result)
        self.assertEqual(result["query"], "测试查询")
        self.assertEqual(result["total_results"], 2)
    
    def test_execute_nonexistent_tool(self):
        """测试执行不存在的工具"""
        result = self.manager.execute_tool("nonexistent_tool", {})
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_register_mcp_client(self):
        """测试注册MCP客户端"""
        client = MCPClient("https://api.example.com")
        self.manager.register_mcp_client("test_client", client)
        
        self.assertIn("test_client", self.manager.mcp_clients)
        self.assertEqual(self.manager.mcp_clients["test_client"], client)
    
    @patch('tools.mcp.base.MCPClient.call_tool')
    def test_call_remote_tool(self, mock_call_tool):
        """测试调用远程工具"""
        mock_call_tool.return_value = {"result": "remote success"}
        
        client = MCPClient("https://api.example.com")
        self.manager.register_mcp_client("test_client", client)
        
        result = self.manager.call_remote_tool("test_client", "remote_tool", {})
        
        self.assertEqual(result, {"result": "remote success"})
    
    def test_call_nonexistent_remote_tool(self):
        """测试调用不存在的远程工具"""
        result = self.manager.call_remote_tool("nonexistent_client", "tool", {})
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)


if __name__ == '__main__':
    unittest.main() 