from agents.utils.register import register_agent
from agents.base_agent import BaseAgent
import importlib
import re

@register_agent
class Orchestrator(BaseAgent):
    def __init__(self, meta_agent):
        super().__init__(name="Orchestrator")
        self.meta_agent = meta_agent

    def _get_agent_description(self):
        return "自治调度智能体，负责任务分发、工会调度、结果聚合等。"

    def _snake_to_camel(self, s):
        return ''.join([w.capitalize() for w in s.split('_')])

    def _camel_to_snake(self, name):
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    def dispatch(self, task_blueprint):
        results = []
        context = {}
        for idx, task in enumerate(task_blueprint["tasks"]):
            intent = task["intent"] if isinstance(task, dict) and "intent" in task else None
            if intent:
                if '_' in intent:
                    class_name = self._snake_to_camel(intent)
                    file_name = intent.lower()
                else:
                    class_name = intent
                    file_name = self._camel_to_snake(intent)
                guild_name = class_name
            else:
                guild_name = class_name = "DatabaseGuild"
                file_name = "database_guild"
            guild = self.meta_agent.registry.get(guild_name)
            if not guild:
                try:
                    module = importlib.import_module(f"agents.guilds.{file_name}")
                    guild_class = getattr(module, class_name)
                    guild = guild_class(self.meta_agent)
                    self.meta_agent.register(guild_name, guild)
                except Exception as e:
                    results.append({"task": task, "error": f"无法自动创建工会 {guild_name}: {e}"})
                    continue
            try:
                # 传递 context 给 handle_task
                result = guild.handle_task(task, context=context)
                # 记录本步结果到 context
                context[f"task_{idx}_result"] = result
                results.append({"task": task, "result": result})
            except Exception as e:
                results.append({"task": task, "error": str(e)})
        return results 