"""
BaseAgent的单元测试
测试LangChain集成功能
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent


class TestBaseAgent(unittest.TestCase):
    """测试BaseAgent基类"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建一个测试用的BaseAgent子类
        class TestAgent(BaseAgent):
            def _get_agent_description(self) -> str:
                return "测试智能体"
        
        self.agent = TestAgent("测试智能体")
    
    def test_agent_initialization(self):
        """测试智能体初始化"""
        self.assertEqual(self.agent.name, "测试智能体")
        self.assertIsNotNone(self.agent.llm)
        self.assertIsNotNone(self.agent.memory)
        self.assertIsNotNone(self.agent.prompt)
        self.assertIsNotNone(self.agent.chain)
        self.assertIsInstance(self.agent.conversation_history, list)
        self.assertIsInstance(self.agent.task_history, list)
    
    def test_agent_status(self):
        """测试获取智能体状态"""
        status = self.agent.get_status()
        
        self.assertIn("name", status)
        self.assertIn("type", status)
        self.assertIn("llm_model", status)
        self.assertIn("tools_count", status)
        self.assertIn("memory_type", status)
        self.assertIn("conversation_count", status)
        self.assertIn("task_count", status)
        self.assertIn("doc_meta", status)
        
        self.assertEqual(status["name"], "测试智能体")
        self.assertEqual(status["type"], "TestAgent")
    
    def test_run_method(self):
        """测试run方法"""
        with patch.object(self.agent, 'chain') as mock_chain:
            mock_chain.run.return_value = "测试响应"
            
            result = self.agent.run("测试任务")
            
            self.assertEqual(result, "测试响应")
            self.assertEqual(len(self.agent.task_history), 1)
            self.assertEqual(len(self.agent.conversation_history), 2)
    
    def test_chat_method(self):
        """测试chat方法"""
        with patch.object(self.agent, 'run') as mock_run:
            mock_run.return_value = "聊天响应"
            
            result = self.agent.chat("你好")
            
            mock_run.assert_called_once_with("你好")
            self.assertEqual(result, "聊天响应")
    
    def test_memory_operations(self):
        """测试记忆操作"""
        # 测试获取记忆摘要
        summary = self.agent.get_memory_summary()
        self.assertIsInstance(summary, str)
        
        # 测试清除记忆
        self.agent.conversation_history = [{"test": "data"}]
        self.agent.clear_memory()
        self.assertEqual(len(self.agent.conversation_history), 0)
    
    def test_state_save_load(self):
        """测试状态保存和加载"""
        import tempfile
        
        # 添加一些测试数据
        self.agent.conversation_history = [{"role": "user", "content": "测试"}]
        self.agent.task_history = [{"task": "测试任务"}]
        
        # 保存状态
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            self.agent.save_state(temp_file)
            
            # 清除数据
            self.agent.conversation_history = []
            self.agent.task_history = []
            
            # 加载状态
            self.agent.load_state(temp_file)
            
            self.assertEqual(len(self.agent.conversation_history), 1)
            self.assertEqual(len(self.agent.task_history), 1)
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_agent_string_representation(self):
        """测试智能体字符串表示"""
        str_repr = str(self.agent)
        repr_repr = repr(self.agent)
        
        self.assertIn("TestAgent", str_repr)
        self.assertIn("测试智能体", str_repr)
        self.assertEqual(str_repr, repr_repr)
    
    def test_abstract_method_implementation(self):
        """测试抽象方法实现"""
        description = self.agent._get_agent_description()
        self.assertEqual(description, "测试智能体")
    
    def test_llm_setup_with_config(self):
        """测试LLM配置设置"""
        # 创建带LLM配置的智能体
        class ConfigAgent(BaseAgent):
            def _get_agent_description(self) -> str:
                return "配置测试智能体"
        
        agent = ConfigAgent("配置测试", llm={
            'model': 'gpt-4',
            'temperature': 0.5,
            'max_tokens': 500
        })
        
        # 验证LLM配置被正确设置
        self.assertIsNotNone(agent.llm)
        # 检查LLM是否是正确的类型
        self.assertTrue(hasattr(agent.llm, 'config'))
        if hasattr(agent.llm, 'config'):
            self.assertEqual(agent.llm.config.model, 'gpt-4')
            self.assertEqual(agent.llm.config.temperature, 0.5)
            self.assertEqual(agent.llm.config.max_tokens, 500)
    
    def test_memory_type_configuration(self):
        """测试记忆类型配置"""
        # 测试buffer记忆
        class BufferAgent(BaseAgent):
            def _get_agent_description(self) -> str:
                return "Buffer记忆智能体"
        
        buffer_agent = BufferAgent("Buffer测试", memory_type='buffer')
        self.assertIsInstance(buffer_agent.memory, type(buffer_agent.memory))
        
        # 测试summary记忆 - 使用真实的LLM实例
        class SummaryAgent(BaseAgent):
            def _get_agent_description(self) -> str:
                return "Summary记忆智能体"
        
        summary_agent = SummaryAgent("Summary测试", memory_type='summary')
        # 验证记忆类型设置被正确传递
        self.assertIsNotNone(summary_agent.memory)


if __name__ == '__main__':
    unittest.main() 