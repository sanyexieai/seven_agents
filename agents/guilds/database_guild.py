from agents.utils.register import register_agent
from agents.base_agent import BaseAgent

@register_agent
class DatabaseGuild(BaseAgent):
    def __init__(self, meta_agent):
        super().__init__(name="DatabaseGuild")
        self.meta_agent = meta_agent

    def _get_agent_description(self):
        return "负责数据库相关业务推理与工具调用。"

    def handle_task(self, task, context=None):
        tool_collective = self.meta_agent.get_tool_collective()
        return tool_collective.handle_tool_request({"目标": "数据库操作", **task}) 