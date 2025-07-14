from agents.base_agent import BaseAgent
from tools.mcp_tools import get_all_mcp_tool_descriptions, call_mcp_tool
import json

class DataCollectorAgent(BaseAgent):
    def _get_agent_description(self) -> str:
        return "数据搜集智能体，能够根据关键词自动选择合适的MCP工具并收集相关数据。"

    def collect_data(self, keyword: str) -> str:
        # 1. 获取所有MCP工具schema
        tool_schemas = self.get_all_tool_schemas()
        # 2. 构造prompt，让LLM帮我们选工具并补全参数
        prompt = (
            f"你是一个数据搜集智能体。\n"
            f"当前可用工具如下：\n"
            f"{json.dumps(tool_schemas, ensure_ascii=False, indent=2)}\n"
            f"请根据用户输入的关键词“{keyword}”，选择最合适的工具，并补全参数（以JSON格式输出，包含'tool_name'和'params'字段）。"
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
        return self.collect_data(task)
