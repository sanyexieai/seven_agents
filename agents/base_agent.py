"""
基于LangChain的智能体基类
提供LLM集成、记忆、工具链等核心功能
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import logging

# LangChain核心组件
from langchain.llms.base import LLM
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain, ConversationChain
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema.runnable import RunnablePassthrough

# 配置和工具
from config.settings import get_settings
from tools.mcp_tools import get_all_mcp_tools, get_all_mcp_tool_descriptions, call_mcp_tool

class BaseAgent(ABC):
    """
    基于LangChain的智能体基类
    
    特性:
    - LLM集成 (OpenAI, Anthropic等)
    - 对话记忆管理
    - 工具链集成
    - 提示词模板
    - 配置管理
    - 日志记录
    """
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.extra_config = kwargs
        
        # 初始化设置
        self.settings = get_settings()
        self.logger = self._setup_logger()
        
        # LangChain组件
        self.llm = self._setup_llm()
        self.memory = self._setup_memory()
        self.tools = self._setup_tools()
        self.prompt = self._setup_prompt()
        self.chain = self._setup_chain()
        self.agent = self._setup_agent()
        
        # 状态管理
        self.conversation_history = []
        self.task_history = []
        self.doc_meta = {
            "created_at": datetime.now().isoformat(),
            "agent_type": self.__class__.__name__,
            "version": "1.0.0"
        }
        
        self.logger.info(f"智能体 '{self.name}' 初始化完成")
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"agent.{self.name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_llm(self):
        """设置语言模型"""
        try:
            from .utils.llm_helper import LLMHelper
            from config.llm_config import LLMConfig
            
            # 检查是否手动传入了LLM配置
            if 'llm_config' in self.extra_config:
                # 使用手动传入的配置
                config = self.extra_config['llm_config']
                self.logger.info("使用手动传入的LLM配置")
            else:
                # 从配置获取LLM设置
                llm_config = self.extra_config.get('llm', {})
                
                # 创建默认LLM配置
                config = LLMConfig.from_settings()
                
                # 如果传入了自定义参数，覆盖默认值
                if llm_config:
                    if 'model' in llm_config:
                        config.model = llm_config['model']
                    if 'max_tokens' in llm_config:
                        config.max_tokens = llm_config['max_tokens']
                    if 'temperature' in llm_config:
                        config.temperature = llm_config['temperature']
                    if 'api_key' in llm_config:
                        config.api_key = llm_config['api_key']
                    if 'base_url' in llm_config:
                        config.base_url = llm_config['base_url']
                
                self.logger.info("使用默认LLM配置")
            
            # 检查API密钥
            if not config.api_key:
                self.logger.error("LLM初始化失败: 未设置API密钥")
                return self._create_fallback_llm()
            
            # 创建LLMHelper实例
            llm_helper = LLMHelper(config)
            
            self.logger.info(f"LLM初始化成功: {config.model}")
            return llm_helper
            
        except Exception as e:
            self.logger.error(f"LLM初始化失败: {e}")
            return self._create_fallback_llm()
    
    def _create_fallback_llm(self) -> LLM:
        """创建后备LLM"""
        class FallbackLLM(LLM):
            def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
                return f"回显: {prompt}"
            
            @property
            def _llm_type(self) -> str:
                return "fallback"
        
        return FallbackLLM()
    
    def _setup_memory(self) -> ConversationBufferMemory:
        """设置对话记忆"""
        memory_type = self.extra_config.get('memory_type', 'buffer')
        
        if memory_type == 'summary':
            memory = ConversationSummaryMemory(
                llm=self.llm,
                max_token_limit=1000
            )
        else:
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        
        self.logger.info(f"记忆系统初始化: {memory_type}")
        return memory
    
    def _setup_tools(self) -> List[BaseTool]:
        """设置工具列表"""
        tools = []
        function_tools = []
        # 添加默认工具
        default_tools = self.extra_config.get('tools', [])
        for tool_config in default_tools:
            try:
                tool = self._create_tool(tool_config)
                if tool:
                    tools.append(tool)
                    # 判断是否为function tool（用@tool装饰的）
                    if hasattr(tool, "args") and hasattr(tool, "__call__"):
                        function_tools.append(tool)
            except Exception as e:
                self.logger.error(f"工具创建失败 {tool_config}: {e}")
        # 自动加载 MCP 工具
        try:
            mcp_tools = get_all_mcp_tools()
            tools.extend(mcp_tools)
            self.logger.info(f"工具初始化完成: {len(tools)} 个工具（含MCP）")
        except Exception as e:
            self.logger.error(f"MCP工具加载失败: {e}")
        self._function_tools = function_tools
        return tools

    def get_all_tool_schemas(self):
        """获取所有MCP工具的schema/描述，便于LLM参数补全和工具选择"""
        return get_all_mcp_tool_descriptions()

    def call_tool_by_name(self, tool_name, params):
        """统一调用MCP工具"""
        return call_mcp_tool(tool_name, params)
    
    def _create_tool(self, tool_config: Dict[str, Any]) -> Optional[BaseTool]:
        """创建工具实例"""
        tool_type = tool_config.get('type')
        tool_name = tool_config.get('name')
        
        # 这里可以根据工具类型创建相应的LangChain工具
        # 示例实现
        if tool_type == 'function':
            return self._create_function_tool(tool_config)
        elif tool_type == 'api':
            return self._create_api_tool(tool_config)
        
        return None
    
    def _create_function_tool(self, config: Dict[str, Any]) -> BaseTool:
        """创建函数工具"""
        from langchain.tools import tool
        
        @tool
        def custom_function(**kwargs):
            """自定义函数工具"""
            return f"执行函数: {config.get('name')} 参数: {kwargs}"
        
        return custom_function
    
    def _create_api_tool(self, config: Dict[str, Any]) -> BaseTool:
        """创建API工具"""
        from langchain.tools import BaseTool
        
        class APITool(BaseTool):
            name = config.get('name', 'api_tool')
            description = config.get('description', 'API调用工具')
            
            def _run(self, query: str) -> str:
                return f"API调用: {query}"
        
        return APITool()
    
    def _load_base_prompt(self, prompt_name):
        import os
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt', 'base_agent', f'{prompt_name}.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _setup_prompt(self) -> ChatPromptTemplate:
        """设置提示词模板"""
        # 加载系统提示词模板
        system_template = self._load_base_prompt('system')
        # 格式化模板内容
        system_prompt = system_template.format(
            agent_name=self.name,
            tools="{tools}",
            chat_history="{chat_history}",
            agent_scratchpad="{agent_scratchpad}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        self.logger.info("提示词模板设置完成")
        return prompt
    
    def _setup_chain(self) -> LLMChain:
        """设置LLM链"""
        chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=self.extra_config.get('verbose', False)
        )
        
        self.logger.info("LLM链设置完成")
        return chain
    
    def _setup_agent(self) -> Optional[AgentExecutor]:
        """设置智能体执行器"""
        # 只用function tool时才用function agent，否则不用
        if hasattr(self, '_function_tools') and self._function_tools:
            try:
                agent = create_openai_functions_agent(
                    llm=self.llm,
                    tools=self._function_tools,
                    prompt=self.prompt
                )
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=self._function_tools,
                    memory=self.memory,
                    verbose=self.extra_config.get('verbose', False),
                    handle_parsing_errors=True
                )
                self.logger.info("智能体执行器设置完成 (function agent)")
                return agent_executor
            except Exception as e:
                self.logger.error(f"智能体设置失败: {e}")
                return None
        else:
            self.logger.info("没有可用function工具，跳过function agent设置，仅支持chain调用")
            return None
    
    def run(self, task: str, **kwargs) -> str:
        """
        执行任务的主要方法
        
        Args:
            task: 任务描述
            **kwargs: 额外参数
            
        Returns:
            任务执行结果
        """
        try:
            self.logger.info(f"开始执行任务: {task}")
            
            # 记录任务历史
            self.task_history.append({
                "task": task,
                "timestamp": datetime.now().isoformat(),
                "parameters": kwargs
            })
            
            # 如果有智能体执行器，使用它
            if self.agent:
                result = self.agent.invoke({
                    "input": task,
                    **kwargs
                })
                response = result.get('output', str(result))
            else:
                # 使用简单的LLM链
                response = self.chain.run(task)
            
            # 记录对话历史
            self.conversation_history.append({
                "role": "user",
                "content": task,
                "timestamp": datetime.now().isoformat()
            })
            self.conversation_history.append({
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"任务执行完成: {task}")
            return response
            
        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def chat(self, message: str) -> str:
        """进行对话"""
        return self.run(message)
    
    def get_memory_summary(self) -> str:
        """获取记忆摘要"""
        if hasattr(self.memory, 'buffer'):
            return str(self.memory.buffer)
        return "无记忆内容"
    
    def clear_memory(self):
        """清除记忆"""
        self.memory.clear()
        self.conversation_history.clear()
        self.logger.info("记忆已清除")
    
    def get_status(self) -> Dict[str, Any]:
        """获取智能体状态"""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "llm_model": getattr(self.llm, 'model_name', 'unknown'),
            "tools_count": len(self.tools),
            "memory_type": self.memory.__class__.__name__,
            "conversation_count": len(self.conversation_history),
            "task_count": len(self.task_history),
            "doc_meta": self.doc_meta
        }
    
    def save_state(self, file_path: str):
        """保存智能体状态"""
        state = {
            "conversation_history": self.conversation_history,
            "task_history": self.task_history,
            "doc_meta": self.doc_meta
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"状态已保存到: {file_path}")
    
    def load_state(self, file_path: str):
        """加载智能体状态"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.conversation_history = state.get('conversation_history', [])
            self.task_history = state.get('task_history', [])
            self.doc_meta.update(state.get('doc_meta', {}))
            
            self.logger.info(f"状态已从 {file_path} 加载")
            
        except Exception as e:
            self.logger.error(f"状态加载失败: {e}")
    
    def llm_structured(self, prompt: str) -> dict:
        """统一结构化LLM输出，自动处理代码块格式，返回dict"""
        llm_response = self.llm(prompt)
        return self.llm.parse_code_block_response(llm_response)
    
    @abstractmethod
    def _get_agent_description(self) -> str:
        """获取智能体描述，子类必须实现"""
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return self.__str__() 