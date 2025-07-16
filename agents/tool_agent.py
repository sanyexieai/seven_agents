from agents.base_agent import BaseAgent
from tools.mcp_tools import call_mcp_tool, list_mcp_tools
import json
import os
from agents.utils.register import register_agent

@register_agent
class ToolCollective(BaseAgent):
    def __init__(self, name="ToolCollective"):
        super().__init__(name=name)
        self._tool_schemas_cache = None

    def _get_agent_description(self):
        return "工具自治体，负责所有外部工具的注册、参数补全、调用和结果校验。"

    def get_all_tool_schemas(self, force_reload=False):
        if self._tool_schemas_cache is not None and not force_reload:
            return self._tool_schemas_cache
        try:
            schemas = list_mcp_tools()
            self.logger.info(f"远程MCP服务加载到 {len(schemas)} 个工具")
            self._tool_schemas_cache = schemas
            return schemas
        except Exception as e:
            self.logger.error(f"远程MCP工具加载失败: {e}")
            return []

    def handle_tool_request(self, task):
        """
        task: 结构化业务描述（如 {'目标': '...', '要求': '...'} 或自然语言）
        """
        # 1. 判断是否需要工具
        if self._need_tool(task):
            # 2. 获取所有MCP工具schema
            tool_schemas = self.get_all_tool_schemas()
            # 3. 加载并格式化tool_select提示词模板
            prompt_template = self._load_prompt('tool_select')
            prompt = prompt_template.format(
                tool_schemas=json.dumps(tool_schemas, ensure_ascii=False, indent=2),
                user_query=json.dumps(task, ensure_ascii=False, indent=2) if isinstance(task, dict) else str(task)
            )
            # 4. 用llm_structured统一结构化解析LLM输出
            tool_call = self.llm_structured(prompt)
            if not tool_call or "tool_name" not in tool_call or "params" not in tool_call:
                return f"LLM参数解析失败: {tool_call}\n原始LLM输出: {tool_call}"
            tool_name = tool_call["tool_name"]
            params = tool_call.get("params", {})
            print(f"tool_name: {tool_name}, params: {params}")
            # 5. 调用MCP工具
            try:
                result = call_mcp_tool(tool_name, params)
                return result
            except Exception as e:
                return f"MCP工具调用失败: {e}"
        else:
            # 6. 不需要工具，直接用 LLM 回复
            return self._llm_reply(task)

    def _need_tool(self, task):
        """
        判断任务是否需要调用工具。
        可用 LLM、规则、关键词等方式实现。
        """
        keywords = ["查询", "抓取", "分析", "生成", "搜索", "下载", "比对", "可视化", "图表", "API", "外部数据"]
        text = json.dumps(task, ensure_ascii=False) if isinstance(task, dict) else str(task)
        return any(kw in text for kw in keywords)

    def _llm_reply(self, task):
        """
        直接用 LLM 生成回复（如无需工具）。
        """
        prompt = f"请根据以下任务需求，直接用专业、简明的语言回复用户：\n{task}"
        return self.llm_structured(prompt)

    def _load_prompt(self, prompt_name):
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt', 'tool_agent', f'{prompt_name}.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()