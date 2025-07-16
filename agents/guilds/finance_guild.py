from agents.utils.register import register_agent
from agents.base_agent import BaseAgent

@register_agent
class FinanceGuild(BaseAgent):
    def __init__(self, meta_agent):
        super().__init__(name="FinanceGuild")
        self.meta_agent = meta_agent

    def _get_agent_description(self):
        return "负责财务报表分析、比率分析、估值建模等任务"

    def handle_task(self, params):
        tool_collective = self.meta_agent.get_tool_collective()
        return tool_collective.handle_tool_request({"目标": "财务分析", **params}) 