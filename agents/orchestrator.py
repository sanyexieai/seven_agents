from agents.agent_loader import load_agents_from_db

class AgentOrchestrator:
    """
    智能体编排器：负责统一调度和任务分发。
    """
    def __init__(self):
        # 动态加载所有启用的智能体
        self.agents = {agent.__class__.__name__: agent for agent in load_agents_from_db()}

    def list_agents(self):
        """列出所有已加载的智能体。"""
        return list(self.agents.keys())

    def execute_task(self, task: str, agent_type: str = None, **kwargs):
        """
        执行任务。
        - agent_type: 指定智能体类型（如 'CoordinatorAgent'），不指定则由协调者分配。
        """
        if agent_type:
            agent = self.agents.get(agent_type)
            if agent:
                return agent.run(task, **kwargs)
            else:
                raise ValueError(f"未找到指定类型的智能体: {agent_type}")
        # 默认由协调者分配
        coordinator = self.agents.get('CoordinatorAgent')
        if coordinator:
            return coordinator.run(task, **kwargs)
        else:
            raise ValueError("未找到协调者智能体") 