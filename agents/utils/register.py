AGENT_REGISTRY = {}

def register_agent(agent_cls):
    AGENT_REGISTRY[agent_cls.__name__] = agent_cls
    return agent_cls

def get_agent_by_name(agent_name):
    cls = AGENT_REGISTRY.get(agent_name)
    if cls:
        return cls(name=agent_name)
    return None 