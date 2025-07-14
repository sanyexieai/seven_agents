from .base_agent import BaseAgent
from tools.mcp_tools import mcp_tool_manager
from tools.rag_tools import rag_tool
from tools.utility_tools import data_processor, file_utils, format_converter, security_utils, validation_utils, time_utils
from langchain.tools import BaseTool
from typing import List

class ToolAgent(BaseAgent):
    """
    工具智能体
    职责: 工具调用、MCP集成、外部API交互
    工具: MCP客户端、API调用器、工具管理器
    特点: 工具集成专家，扩展性强
    """
    
    def __init__(self, name: str, **kwargs):
        # 配置工具智能体的特定设置
        tool_config = {
            'llm': kwargs.get('llm', {'model': 'gpt-3.5-turbo', 'temperature': 0.7}),
            'memory_type': 'buffer',
            'verbose': kwargs.get('verbose', True),
            'system_prompt': """你是一个专业的工具调用智能体。

你的职责是:
- 理解用户需求并选择合适的工具
- 执行各种工具操作（搜索、文件处理、API调用等）
- 提供准确的操作结果和解释
- 处理工具调用错误并提供解决方案

可用工具包括:
- MCP工具：网络搜索、文件操作、API调用
- RAG工具：知识库搜索和问答
- 数据处理工具：文本清理、格式转换、验证
- 安全工具：密码哈希、令牌生成
- 时间工具：时间戳转换、持续时间计算

请根据用户需求选择合适的工具并执行操作。""",
            'tools': self._get_tool_configs()
        }
        
        super().__init__(name, **tool_config)
        
        # 保持原有的工具映射
        self.available_tools = {
            'mcp': mcp_tool_manager,
            'rag': rag_tool,
            'data_processor': data_processor,
            'file_utils': file_utils,
            'format_converter': format_converter,
            'security_utils': security_utils,
            'validation_utils': validation_utils,
            'time_utils': time_utils
        }
    
    def run(self, task: str, **kwargs):
        """执行工具调用任务"""
        try:
            # 解析任务类型
            if task.startswith("搜索"):
                return self._handle_search_task(task, **kwargs)
            elif task.startswith("文件"):
                return self._handle_file_task(task, **kwargs)
            elif task.startswith("API"):
                return self._handle_api_task(task, **kwargs)
            elif task.startswith("RAG"):
                return self._handle_rag_task(task, **kwargs)
            elif task.startswith("数据处理"):
                return self._handle_data_task(task, **kwargs)
            elif task.startswith("格式转换"):
                return self._handle_format_task(task, **kwargs)
            elif task.startswith("验证"):
                return self._handle_validation_task(task, **kwargs)
            else:
                return self._handle_general_task(task, **kwargs)
                
        except Exception as e:
            return f"[工具] 执行任务失败: {str(e)}"
    
    def _handle_search_task(self, task: str, **kwargs):
        """处理搜索任务"""
        query = kwargs.get('query', task.replace("搜索", "").strip())
        max_results = kwargs.get('max_results', 5)
        
        result = mcp_tool_manager.execute_tool('web_search', {
            'query': query,
            'max_results': max_results
        })
        
        return f"[工具] 搜索完成: {result}"
    
    def _handle_file_task(self, task: str, **kwargs):
        """处理文件操作任务"""
        operation = kwargs.get('operation', 'read')
        file_path = kwargs.get('file_path', '')
        
        if not file_path:
            return "[工具] 错误: 缺少文件路径"
        
        result = mcp_tool_manager.execute_tool('file_operation', {
            'operation': operation,
            'file_path': file_path,
            'content': kwargs.get('content')
        })
        
        return f"[工具] 文件操作完成: {result}"
    
    def _handle_api_task(self, task: str, **kwargs):
        """处理API调用任务"""
        method = kwargs.get('method', 'GET')
        url = kwargs.get('url', '')
        
        if not url:
            return "[工具] 错误: 缺少API URL"
        
        result = mcp_tool_manager.execute_tool('api_call', {
            'method': method,
            'url': url,
            'headers': kwargs.get('headers'),
            'data': kwargs.get('data')
        })
        
        return f"[工具] API调用完成: {result}"
    
    def _handle_rag_task(self, task: str, **kwargs):
        """处理RAG任务"""
        if "搜索" in task:
            query = kwargs.get('query', task.replace("RAG搜索", "").strip())
            top_k = kwargs.get('top_k', 5)
            result = rag_tool.search_knowledge(query, top_k=top_k)
            return f"[工具] RAG搜索完成: {result}"
        elif "生成" in task:
            question = kwargs.get('question', task.replace("RAG生成", "").strip())
            result = rag_tool.generate_answer(question)
            return f"[工具] RAG生成完成: {result}"
        else:
            return "[工具] 未知的RAG任务类型"
    
    def _handle_data_task(self, task: str, **kwargs):
        """处理数据处理任务"""
        text = kwargs.get('text', '')
        
        if "清理" in task:
            result = data_processor.clean_text(text)
            return f"[工具] 文本清理完成: {result}"
        elif "统计" in task:
            word_count = data_processor.count_words(text)
            char_count = data_processor.count_chars(text)
            return f"[工具] 文本统计: 单词数={word_count}, 字符数={char_count}"
        elif "摘要" in task:
            max_length = kwargs.get('max_length', 200)
            result = data_processor.generate_summary(text, max_length)
            return f"[工具] 摘要生成完成: {result}"
        else:
            return "[工具] 未知的数据处理任务"
    
    def _handle_format_task(self, task: str, **kwargs):
        """处理格式转换任务"""
        content = kwargs.get('content', '')
        
        if "JSON转YAML" in task:
            result = format_converter.json_to_yaml(content)
            return f"[工具] JSON转YAML完成: {result}"
        elif "YAML转JSON" in task:
            result = format_converter.yaml_to_json(content)
            return f"[工具] YAML转JSON完成: {result}"
        else:
            return "[工具] 未知的格式转换任务"
    
    def _handle_validation_task(self, task: str, **kwargs):
        """处理验证任务"""
        value = kwargs.get('value', '')
        
        if "邮箱" in task:
            result = validation_utils.is_valid_email(value)
            return f"[工具] 邮箱验证结果: {result}"
        elif "URL" in task:
            result = validation_utils.is_valid_url(value)
            return f"[工具] URL验证结果: {result}"
        elif "JSON" in task:
            result = validation_utils.is_valid_json(value)
            return f"[工具] JSON验证结果: {result}"
        else:
            return "[工具] 未知的验证任务"
    
    def _handle_general_task(self, task: str, **kwargs):
        """处理通用任务"""
        return f"[工具] 处理任务: {task} - 这是一个通用的工具调用任务"
    
    def _get_tool_configs(self) -> List[dict]:
        """获取工具配置列表"""
        return [
            {
                "type": "function",
                "name": "web_search",
                "description": "网络搜索工具"
            },
            {
                "type": "function", 
                "name": "file_operation",
                "description": "文件操作工具"
            },
            {
                "type": "function",
                "name": "api_call", 
                "description": "API调用工具"
            },
            {
                "type": "function",
                "name": "rag_search",
                "description": "RAG知识库搜索"
            },
            {
                "type": "function",
                "name": "data_process",
                "description": "数据处理工具"
            }
        ]
    
    def _get_agent_description(self) -> str:
        """获取智能体描述"""
        return """工具调用智能体，专门负责执行各种工具操作，包括搜索、文件处理、API调用、数据处理等任务。"""
    
    def list_available_tools(self):
        """列出可用工具"""
        tools_info = []
        
        # MCP工具
        mcp_tools = mcp_tool_manager.list_tools()
        tools_info.extend([{"type": "MCP", "name": tool["name"], "description": tool["description"]} for tool in mcp_tools])
        
        # 其他工具
        other_tools = [
            {"type": "RAG", "name": "知识库搜索", "description": "搜索知识库"},
            {"type": "RAG", "name": "RAG生成", "description": "基于知识库生成回答"},
            {"type": "数据处理", "name": "文本清理", "description": "清理文本内容"},
            {"type": "数据处理", "name": "文本统计", "description": "统计文本信息"},
            {"type": "格式转换", "name": "JSON转YAML", "description": "JSON格式转YAML"},
            {"type": "验证", "name": "邮箱验证", "description": "验证邮箱格式"},
        ]
        tools_info.extend(other_tools)
        
        return tools_info 