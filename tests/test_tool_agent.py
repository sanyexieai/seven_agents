"""
工具智能体的单元测试
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tool_agent import ToolAgent


class TestToolAgent(unittest.TestCase):
    """测试工具智能体"""
    
    def setUp(self):
        self.agent = ToolAgent("测试工具智能体")
    
    def test_tool_agent_initialization(self):
        """测试工具智能体初始化"""
        self.assertEqual(self.agent.name, "测试工具智能体")
        self.assertIsNotNone(self.agent.available_tools)
        self.assertIn('mcp', self.agent.available_tools)
        self.assertIn('rag', self.agent.available_tools)
        self.assertIn('data_processor', self.agent.available_tools)
    
    def test_handle_search_task(self):
        """测试处理搜索任务"""
        with patch('agents.tool_agent.mcp_tool_manager') as mock_manager:
            mock_manager.execute_tool.return_value = {
                "query": "人工智能",
                "results": [{"title": "AI发展"}],
                "total_results": 1
            }
            
            result = self.agent._handle_search_task("搜索人工智能", query="人工智能", max_results=3)
            
            self.assertIn("搜索完成", result)
            mock_manager.execute_tool.assert_called_once_with('web_search', {
                'query': '人工智能',
                'max_results': 3
            })
    
    def test_handle_file_task(self):
        """测试处理文件任务"""
        with patch('agents.tool_agent.mcp_tool_manager') as mock_manager:
            mock_manager.execute_tool.return_value = {
                "success": True,
                "content": "文件内容"
            }
            
            result = self.agent._handle_file_task("文件读取", operation="read", file_path="test.txt")
            
            self.assertIn("文件操作完成", result)
            mock_manager.execute_tool.assert_called_once_with('file_operation', {
                'operation': 'read',
                'file_path': 'test.txt',
                'content': None
            })
    
    def test_handle_file_task_missing_path(self):
        """测试处理文件任务缺少路径"""
        result = self.agent._handle_file_task("文件读取", operation="read")
        self.assertIn("错误: 缺少文件路径", result)
    
    def test_handle_api_task(self):
        """测试处理API任务"""
        with patch('agents.tool_agent.mcp_tool_manager') as mock_manager:
            mock_manager.execute_tool.return_value = {
                "success": True,
                "status_code": 200,
                "data": {"message": "success"}
            }
            
            result = self.agent._handle_api_task("API调用", method="GET", url="https://api.example.com")
            
            self.assertIn("API调用完成", result)
            mock_manager.execute_tool.assert_called_once_with('api_call', {
                'method': 'GET',
                'url': 'https://api.example.com',
                'headers': None,
                'data': None
            })
    
    def test_handle_api_task_missing_url(self):
        """测试处理API任务缺少URL"""
        result = self.agent._handle_api_task("API调用", method="GET")
        self.assertIn("错误: 缺少API URL", result)
    
    def test_handle_rag_task_search(self):
        """测试处理RAG搜索任务"""
        with patch('agents.tool_agent.rag_tool') as mock_rag:
            mock_rag.search_knowledge.return_value = {
                "query": "人工智能",
                "results": [{"doc_id": "doc1", "content": "AI内容"}],
                "total_results": 1
            }
            
            result = self.agent._handle_rag_task("RAG搜索人工智能", query="人工智能")
            
            self.assertIn("RAG搜索完成", result)
            mock_rag.search_knowledge.assert_called_once_with("人工智能", top_k=5)
    
    def test_handle_rag_task_generate(self):
        """测试处理RAG生成任务"""
        with patch('agents.tool_agent.rag_tool') as mock_rag:
            mock_rag.generate_answer.return_value = {
                "success": True,
                "question": "什么是AI？",
                "answer": "AI是人工智能的缩写"
            }
            
            result = self.agent._handle_rag_task("RAG生成回答", question="什么是AI？")
            
            self.assertIn("RAG生成完成", result)
            mock_rag.generate_answer.assert_called_once_with("什么是AI？")
    
    def test_handle_rag_task_unknown(self):
        """测试处理未知RAG任务"""
        result = self.agent._handle_rag_task("RAG未知任务")
        self.assertIn("未知的RAG任务类型", result)
    
    def test_handle_data_task_clean(self):
        """测试处理数据清理任务"""
        with patch('agents.tool_agent.data_processor') as mock_processor:
            mock_processor.clean_text.return_value = "清理后的文本"
            
            result = self.agent._handle_data_task("数据处理清理", text="原始文本")
            
            self.assertIn("文本清理完成", result)
            mock_processor.clean_text.assert_called_once_with("原始文本")
    
    def test_handle_data_task_count(self):
        """测试处理数据统计任务"""
        with patch('agents.tool_agent.data_processor') as mock_processor:
            mock_processor.count_words.return_value = 5
            mock_processor.count_chars.return_value = 20
            
            result = self.agent._handle_data_task("数据处理统计", text="测试文本")
            
            self.assertIn("文本统计", result)
            self.assertIn("单词数=5", result)
            self.assertIn("字符数=20", result)
    
    def test_handle_data_task_summary(self):
        """测试处理数据摘要任务"""
        with patch('agents.tool_agent.data_processor') as mock_processor:
            mock_processor.generate_summary.return_value = "摘要内容"
            
            result = self.agent._handle_data_task("数据处理摘要", text="长文本", max_length=100)
            
            self.assertIn("摘要生成完成", result)
            mock_processor.generate_summary.assert_called_once_with("长文本", 100)
    
    def test_handle_data_task_unknown(self):
        """测试处理未知数据处理任务"""
        result = self.agent._handle_data_task("数据处理未知", text="文本")
        self.assertIn("未知的数据处理任务", result)
    
    def test_handle_format_task_json_to_yaml(self):
        """测试处理JSON转YAML任务"""
        with patch('agents.tool_agent.format_converter') as mock_converter:
            mock_converter.json_to_yaml.return_value = "name: 张三\nage: 25"
            
            result = self.agent._handle_format_task("格式转换JSON转YAML", content='{"name": "张三", "age": 25}')
            
            self.assertIn("JSON转YAML完成", result)
            mock_converter.json_to_yaml.assert_called_once_with('{"name": "张三", "age": 25}')
    
    def test_handle_format_task_yaml_to_json(self):
        """测试处理YAML转JSON任务"""
        with patch('agents.tool_agent.format_converter') as mock_converter:
            mock_converter.yaml_to_json.return_value = '{"name": "张三", "age": 25}'
            
            result = self.agent._handle_format_task("格式转换YAML转JSON", content="name: 张三\nage: 25")
            
            self.assertIn("YAML转JSON完成", result)
            mock_converter.yaml_to_json.assert_called_once_with("name: 张三\nage: 25")
    
    def test_handle_format_task_unknown(self):
        """测试处理未知格式转换任务"""
        result = self.agent._handle_format_task("格式转换未知", content="内容")
        self.assertIn("未知的格式转换任务", result)
    
    def test_handle_validation_task_email(self):
        """测试处理邮箱验证任务"""
        with patch('agents.tool_agent.validation_utils') as mock_validation:
            mock_validation.is_valid_email.return_value = True
            
            result = self.agent._handle_validation_task("验证邮箱", value="test@example.com")
            
            self.assertIn("邮箱验证结果: True", result)
            mock_validation.is_valid_email.assert_called_once_with("test@example.com")
    
    def test_handle_validation_task_url(self):
        """测试处理URL验证任务"""
        with patch('agents.tool_agent.validation_utils') as mock_validation:
            mock_validation.is_valid_url.return_value = False
            
            result = self.agent._handle_validation_task("验证URL", value="invalid-url")
            
            self.assertIn("URL验证结果: False", result)
            mock_validation.is_valid_url.assert_called_once_with("invalid-url")
    
    def test_handle_validation_task_json(self):
        """测试处理JSON验证任务"""
        with patch('agents.tool_agent.validation_utils') as mock_validation:
            mock_validation.is_valid_json.return_value = True
            
            result = self.agent._handle_validation_task("验证JSON", value='{"key": "value"}')
            
            self.assertIn("JSON验证结果: True", result)
            mock_validation.is_valid_json.assert_called_once_with('{"key": "value"}')
    
    def test_handle_validation_task_unknown(self):
        """测试处理未知验证任务"""
        result = self.agent._handle_validation_task("验证未知", value="值")
        self.assertIn("未知的验证任务", result)
    
    def test_handle_general_task(self):
        """测试处理通用任务"""
        result = self.agent._handle_general_task("通用任务")
        self.assertIn("处理任务: 通用任务", result)
        self.assertIn("通用的工具调用任务", result)
    
    def test_run_search_task(self):
        """测试运行搜索任务"""
        with patch.object(self.agent, '_handle_search_task') as mock_handler:
            mock_handler.return_value = "搜索结果"
            
            result = self.agent.run("搜索人工智能", query="AI", max_results=5)
            
            self.assertEqual(result, "搜索结果")
            mock_handler.assert_called_once_with("搜索人工智能", query="AI", max_results=5)
    
    def test_run_file_task(self):
        """测试运行文件任务"""
        with patch.object(self.agent, '_handle_file_task') as mock_handler:
            mock_handler.return_value = "文件操作结果"
            
            result = self.agent.run("文件读取", operation="read", file_path="test.txt")
            
            self.assertEqual(result, "文件操作结果")
            mock_handler.assert_called_once_with("文件读取", operation="read", file_path="test.txt")
    
    def test_run_api_task(self):
        """测试运行API任务"""
        with patch.object(self.agent, '_handle_api_task') as mock_handler:
            mock_handler.return_value = "API调用结果"
            
            result = self.agent.run("API调用", method="GET", url="https://api.example.com")
            
            self.assertEqual(result, "API调用结果")
            mock_handler.assert_called_once_with("API调用", method="GET", url="https://api.example.com")
    
    def test_run_rag_task(self):
        """测试运行RAG任务"""
        with patch.object(self.agent, '_handle_rag_task') as mock_handler:
            mock_handler.return_value = "RAG结果"
            
            result = self.agent.run("RAG搜索", query="人工智能")
            
            self.assertEqual(result, "RAG结果")
            mock_handler.assert_called_once_with("RAG搜索", query="人工智能")
    
    def test_run_data_task(self):
        """测试运行数据处理任务"""
        with patch.object(self.agent, '_handle_data_task') as mock_handler:
            mock_handler.return_value = "数据处理结果"
            
            result = self.agent.run("数据处理清理", text="原始文本")
            
            self.assertEqual(result, "数据处理结果")
            mock_handler.assert_called_once_with("数据处理清理", text="原始文本")
    
    def test_run_format_task(self):
        """测试运行格式转换任务"""
        with patch.object(self.agent, '_handle_format_task') as mock_handler:
            mock_handler.return_value = "格式转换结果"
            
            result = self.agent.run("格式转换JSON转YAML", content='{"key": "value"}')
            
            self.assertEqual(result, "格式转换结果")
            mock_handler.assert_called_once_with("格式转换JSON转YAML", content='{"key": "value"}')
    
    def test_run_validation_task(self):
        """测试运行验证任务"""
        with patch.object(self.agent, '_handle_validation_task') as mock_handler:
            mock_handler.return_value = "验证结果"
            
            result = self.agent.run("验证邮箱", value="test@example.com")
            
            self.assertEqual(result, "验证结果")
            mock_handler.assert_called_once_with("验证邮箱", value="test@example.com")
    
    def test_run_general_task(self):
        """测试运行通用任务"""
        with patch.object(self.agent, '_handle_general_task') as mock_handler:
            mock_handler.return_value = "通用任务结果"
            
            result = self.agent.run("通用任务", param="value")
            
            self.assertEqual(result, "通用任务结果")
            mock_handler.assert_called_once_with("通用任务", param="value")
    
    def test_run_with_exception(self):
        """测试运行任务时出现异常"""
        with patch.object(self.agent, '_handle_search_task') as mock_handler:
            mock_handler.side_effect = Exception("测试异常")
            
            result = self.agent.run("搜索任务")
            
            self.assertIn("执行任务失败", result)
            self.assertIn("测试异常", result)
    
    def test_list_available_tools(self):
        """测试列出可用工具"""
        with patch('agents.tool_agent.mcp_tool_manager') as mock_manager:
            mock_manager.list_tools.return_value = [
                {"name": "web_search", "description": "网络搜索"},
                {"name": "file_operation", "description": "文件操作"}
            ]
            
            tools = self.agent.list_available_tools()
            
            self.assertIsInstance(tools, list)
            self.assertGreater(len(tools), 0)
            
            # 检查MCP工具
            mcp_tools = [tool for tool in tools if tool["type"] == "MCP"]
            self.assertEqual(len(mcp_tools), 2)
            
            # 检查其他工具
            other_tools = [tool for tool in tools if tool["type"] != "MCP"]
            self.assertGreater(len(other_tools), 0)
            
            # 验证工具格式
            for tool in tools:
                self.assertIn("type", tool)
                self.assertIn("name", tool)
                self.assertIn("description", tool)


if __name__ == '__main__':
    unittest.main() 