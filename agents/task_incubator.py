from agents.utils.register import register_agent
from agents.base_agent import BaseAgent
import os

@register_agent
class TaskIncubator(BaseAgent):
    def __init__(self, name="TaskIncubator"):
        super().__init__(name=name)

    def _get_agent_description(self) -> str:
        return "任务孵化智能体，负责将用户输入转化为结构化任务蓝图。"

    def _load_prompt(self, prompt_name):
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt', 'task_incubator', f'{prompt_name}.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def incubate(self, user_input, meta_agent=None):
        # 获取所有能力描述
        abilities = meta_agent.discover_capabilities() if meta_agent else {}
        prompt_template = self._load_prompt('task_incubate')
        prompt = prompt_template.format(user_input=user_input, abilities=abilities)
        result = self.llm_structured(prompt)
        if not result or 'tasks' not in result:
            # 回退到简单模式
            return {"tasks": [user_input]}
        return result 