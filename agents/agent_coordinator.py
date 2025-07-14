import os
import json
from agents.base_agent import BaseAgent
from agents.utils.register import AGENT_REGISTRY, register_agent, get_agent_by_name

class AgentCoordinatorAgent(BaseAgent):
    def _get_agent_description(self) -> str:
        return "智能体调度者，能够获取所有已注册智能体及其描述，并根据用户需求调度合适的智能体。"

    def _load_prompt(self, prompt_name):
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt', 'agent_coordinator', f'{prompt_name}.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_all_agents_info(self):
        # 获取所有已注册智能体的名称和描述
        agent_infos = []
        for name, cls in AGENT_REGISTRY.items():
            try:
                desc = cls._get_agent_description(cls)
            except Exception:
                desc = "无描述"
            agent_infos.append({"name": name, "description": desc})
        return agent_infos

    def select_agent(self, user_query: str) -> str:
        agent_list = self.get_all_agents_info()
        prompt_template = self._load_prompt('agent_list')
        prompt = prompt_template.format(
            agent_list=json.dumps(agent_list, ensure_ascii=False, indent=2),
            user_query=user_query
        )
        llm_response = self.llm(prompt)
        return llm_response

    def select_and_call_agent(self, user_query: str) -> str:
        agent_list = self.get_all_agents_info()
        prompt_template = self._load_prompt('agent_select')
        prompt = prompt_template.format(
            agent_list=json.dumps(agent_list, ensure_ascii=False, indent=2),
            user_query=user_query
        )
        # 1. 让LLM选择智能体并补全参数
        agent_call = self.llm_structured(prompt)
        if not agent_call or "agent_name" not in agent_call:
            return f"LLM未能正确选择智能体: {agent_call}"
        agent_name = agent_call["agent_name"]
        params = agent_call.get("params", {})
        # 2. 动态实例化并调用被选中智能体
        agent = get_agent_by_name(agent_name)
        if not agent:
            return f"未找到名为 {agent_name} 的智能体"
        try:
            result = agent.run(user_query, **params)
            return result
        except Exception as e:
            return f"被选中智能体调用失败: {e}" 