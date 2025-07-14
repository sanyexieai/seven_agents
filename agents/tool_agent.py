from agents.base_agent import BaseAgent
from tools.mcp_tools import get_all_mcp_tool_descriptions, call_mcp_tool
import json
import os
from agents.utils.register import register_agent

@register_agent
class ToolAgent(BaseAgent):
    def _get_agent_description(self) -> str:
        return "工具智能体，能够根据用户需求自动选择最合适的MCP工具，补全参数并完成任务。"

    def _load_prompt(self, prompt_name):
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt', 'tool_agent', f'{prompt_name}.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def select_and_call_tool(self, user_query: str) -> str:
        # 1. 获取所有MCP工具schema
        tool_schemas = self.get_all_tool_schemas()
        # 2. 加载并格式化tool_select提示词模板
        prompt_template = self._load_prompt('tool_select')
        prompt = prompt_template.format(
            tool_schemas=json.dumps(tool_schemas, ensure_ascii=False, indent=2),
            user_query=user_query
        )
        # 3. 用llm_structured统一结构化解析LLM输出
        tool_call = self.llm_structured(prompt)
        if not tool_call or "tool_name" not in tool_call or "params" not in tool_call:
            return f"LLM参数解析失败: {tool_call}\n原始LLM输出: {tool_call}"
        tool_name = tool_call["tool_name"]
        params = tool_call["params"]
        # 4. 调用MCP工具
        try:
            result = call_mcp_tool(tool_name, params)
            return result
        except Exception as e:
            return f"MCP工具调用失败: {e}"

    def run(self, task: str, **kwargs) -> str:
        # 兼容BaseAgent的run接口
        return self.select_and_call_tool(task) 