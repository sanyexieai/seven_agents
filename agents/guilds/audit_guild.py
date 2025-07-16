from agents.utils.register import register_agent
from agents.base_agent import BaseAgent

@register_agent
class AuditGuild(BaseAgent):
    def __init__(self, meta_agent):
        super().__init__(name="AuditGuild")
        self.meta_agent = meta_agent

    def _get_agent_description(self):
        return "负责合规性审查、风险提示、引用溯源等任务"

    def handle_task(self, params):
        tool_collective = self.meta_agent.get_tool_collective()
        return tool_collective.handle_tool_request({"目标": "合规审查", **params}) 