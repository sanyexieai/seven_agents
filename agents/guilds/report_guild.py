from agents.utils.register import register_agent
from agents.base_agent import BaseAgent

@register_agent
class ReportGuild(BaseAgent):
    def __init__(self, meta_agent):
        super().__init__(name="ReportGuild")
        self.meta_agent = meta_agent

    def _get_agent_description(self):
        return "负责多模态研报整合、章节生成、格式化输出等任务"

    def handle_task(self, params):
        tool_collective = self.meta_agent.get_tool_collective()
        return tool_collective.handle_tool_request({"目标": "生成研报", **params}) 