class BaseAgent:
    """所有智能体的基类，定义通用接口和属性。"""
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.extra_config = kwargs

    def run(self, task: str, **kwargs):
        """执行任务的通用方法，需在子类中实现。"""
        raise NotImplementedError("子类需实现 run 方法") 