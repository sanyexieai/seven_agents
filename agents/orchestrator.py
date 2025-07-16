from agents.utils.register import register_agent
from agents.base_agent import BaseAgent
import importlib
import re
import sys
import os
import json

# 彩色日志打印函数
def print_color(msg, color):
    colors = {
        'green': '\033[92m',
        'blue': '\033[94m',
        'reset': '\033[0m',
        'red': '\033[91m',
        'yellow': '\033[93m',
    }
    sys.stdout.write(colors.get(color, '') + msg + colors['reset'] + '\n')
    sys.stdout.flush()

def safe_to_dict(obj):
    if isinstance(obj, list):
        return [safe_to_dict(i) for i in obj]
    if isinstance(obj, dict):
        return {k: safe_to_dict(v) for k, v in obj.items()}
    if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
        return safe_to_dict(obj.to_dict())
    if hasattr(obj, '__dict__'):
        return {k: safe_to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    return obj

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
        self.meta_agent.context.clear()
        for idx, task in enumerate(task_blueprint["tasks"]):
            print_color(f"[Orchestrator] 开始执行任务 {idx+1}/{len(task_blueprint['tasks'])}: {task.get('intent', str(task))}", 'green')
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
                    print_color(f"[Orchestrator] 任务 {idx+1} 工会创建失败: {e}", 'red')
                    results.append({"task": task, "error": f"无法自动创建工会 {guild_name}: {e}"})
                    continue
            try:
                # 传递 context 给 handle_task
                result = guild.handle_task(task)
                self.meta_agent.context[f"task_{idx}_result"] = result
                results.append({"task": task, "result": result})
                print_color(f"[Orchestrator] 结束任务 {idx+1}: {task.get('intent', str(task))}", 'blue')
            except Exception as e:
                print_color(f"[Orchestrator] 任务 {idx+1} 执行异常: {e}", 'red')
                results.append({"task": task, "error": str(e)})
        return results

    def _load_prompt(self, prompt_name):
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt', 'orchestrator', prompt_name)
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()

    def handle_task(self, params):
        """
        支持 Orchestrator 作为任务节点参与多轮调度。
        params: 可以是新的用户输入、任务蓝图、或 context 信息
        """
        incubator = self.meta_agent.registry.get("TaskIncubator")
        if not incubator:
            return "未找到 TaskIncubator，无法重新孵化任务"

        context = self.meta_agent.context
        # 优先用 LLM 直接生成任务链
        prompt_template = self._load_prompt('orchestrator.txt')
        abilities = self.meta_agent.discover_capabilities()
        # 1. 收集所有上游结果
        upstream_results = []
        for k, v in self.meta_agent.context.items():
            if k.startswith("task_") and k.endswith("_result"):
                upstream_results.append(safe_to_dict(v))

        # 2. 构造结构化 user_input
        user_input = {
            "user_params": safe_to_dict(params.get("params")),
            "upstream_results": upstream_results
        }

        # 3. 生成 prompt
        prompt = prompt_template.format(
            user_input=json.dumps(user_input, ensure_ascii=False, indent=2),
            abilities=json.dumps(abilities, ensure_ascii=False, indent=2)
        )
        result = self.llm_structured(prompt)

        # 4. 处理 LLM 结果
        if result and 'tasks' in result:
            params["tasks"] = result["tasks"]
            return self.dispatch(params)
        else:
            new_blueprint = incubator.incubate(user_input, self.meta_agent)
            return self.dispatch(new_blueprint) 