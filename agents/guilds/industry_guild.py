from agents.utils.register import register_agent
from agents.base_agent import BaseAgent

@register_agent
class IndustryGuild(BaseAgent):
    def __init__(self, meta_agent):
        super().__init__(name="IndustryGuild")
        self.meta_agent = meta_agent

    def _get_agent_description(self):
        return "负责行业结构分析、趋势预测、横向对比等任务"

    def handle_task(self, params):
        tool_collective = self.meta_agent.get_tool_collective()
        return tool_collective.handle_tool_request({"目标": "行业分析", **params}) 