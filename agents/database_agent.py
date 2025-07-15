from agents.base_agent import BaseAgent
from agents.utils.register import register_agent
from tools.mcp_tools import call_mcp_tool

default_prompt = 'system'

@register_agent
class DatabaseAgent(BaseAgent):
    def _get_agent_description(self) -> str:
        return "数据库操作智能体，通过MCP工具链实现结构同步、表结构查询、数据增删改查等操作。"

    def _setup_prompt(self):
        from langchain.prompts import ChatPromptTemplate
        import os
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt', 'database_agent', f'{default_prompt}.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_text = f.read()
        return ChatPromptTemplate.from_template(prompt_text)

    def run(self, task: str, **kwargs) -> str:
        """
        仅通过MCP工具链实现数据库相关操作。
        """
        method = kwargs.pop("method", None)
        params = {"task": task}
        params.update(kwargs)
        try:
            result = call_mcp_tool("database_operation", params, method=method)
            return result
        except Exception as e:
            return f"MCP数据库操作失败: {e}" 