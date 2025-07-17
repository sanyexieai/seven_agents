from agents.utils.register import register_agent
import logging
import importlib
import json
import os
import pkgutil
from agents.tool_agent import ToolCollective

@register_agent
class MetaAgent:
    REGISTRY_FILE = "meta_registry.json"

    def __init__(self, auto_register_all=False):
        self.registry = {}  # 所有智能体/工会/工具的注册表
        self.tool_collective = ToolCollective()  # 全局唯一工具智能体
        self.context = {}   # 全局上下文
        if auto_register_all:
            self.auto_register_all()

    def get_tool_collective(self):
        return self.tool_collective

    def get_all_tools(self):
        return self.tool_collective.get_all_tool_schemas()

    def get_tool_prompt(self, tool_name):
        return self.tool_collective.get_tool_prompt(tool_name)

    def _get_agent_description(self):
        return "元治理智能体，负责注册、健康巡检、能力发现、自治进化等。"

    def auto_register_all(self):
        """
        递归扫描 agents.guilds 及其所有子目录，自动注册所有 Guild。
        """
        #1.注册工具智能体
        self.register("ToolCollective", ToolCollective())
        #2.注册所有工会
        guilds_root = os.path.join(os.path.dirname(__file__), "guilds")
        for root, dirs, files in os.walk(guilds_root):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    rel_path = os.path.relpath(os.path.join(root, file), guilds_root)
                    module_path = rel_path.replace(os.sep, ".")[:-3]  # 去掉 .py
                    full_module = f"agents.guilds.{module_path}"
                    try:
                        module = importlib.import_module(full_module)
                        for attr in dir(module):
                            if attr.endswith("Guild"):
                                guild_class = getattr(module, attr)
                                if callable(guild_class):
                                    guild = guild_class(self)  # 传入 meta_agent 实例
                                    self.register(attr, guild)
                    except Exception as e:
                        logging.error(f"自动注册工会 {full_module} 失败: {e}")

    def save_registry(self):
        # 只保存智能体名和类名
        data = {name: agent.__class__.__name__ for name, agent in self.registry.items()}
        with open(self.REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logging.info(f"MetaAgent 注册表已持久化到 {self.REGISTRY_FILE}")

    def load_registry(self):
        if not os.path.exists(self.REGISTRY_FILE):
            return
        with open(self.REGISTRY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        from agents.tool_agent import ToolCollective
        for name, class_name in data.items():
            try:
                module = importlib.import_module(f"agents.guilds.{class_name.lower()}")
                agent_class = getattr(module, class_name)
                agent = agent_class(ToolCollective())
                self.registry[name] = agent
                logging.info(f"已恢复智能体: {name}")
            except Exception as e:
                logging.error(f"恢复智能体 {name} 失败: {e}")

    def register(self, agent_name, agent_obj):
        self.registry[agent_name] = agent_obj
        logging.info(f"注册智能体: {agent_name}")
        self.save_registry()

    def unregister(self, agent_name):
        if agent_name in self.registry:
            del self.registry[agent_name]
            logging.info(f"注销智能体: {agent_name}")
            self.save_registry()

    def discover_capabilities(self):
        # 动态发现所有能力
        return {name: getattr(agent, "get_capabilities", lambda: None)() for name, agent in self.registry.items()}

    def evolve(self):
        # 健康巡检、异常修复
        for name, agent in self.registry.items():
            status = None
            if hasattr(agent, "get_status"):
                try:
                    status = agent.get_status()
                except Exception as e:
                    logging.warning(f"Guild {name} get_status 异常: {e}")
            if status and status.get("health") == "unhealthy":
                logging.warning(f"Guild {name} 状态异常，尝试自动修复...")
                self.restart_agent(name)
            else:
                logging.info(f"Guild {name} 状态正常。")
        logging.info("MetaAgent evolve 完成。")
        self.save_registry()

    def restart_agent(self, agent_name):
        # 简单重启逻辑（可扩展为更智能的修复/替换）
        agent = self.registry.get(agent_name)
        if agent:
            agent_class = agent.__class__
            try:
                from agents.tool_agent import ToolCollective
                new_agent = agent_class(ToolCollective())
                self.registry[agent_name] = new_agent
                logging.info(f"已重启智能体: {agent_name}")
                self.save_registry()
            except Exception as e:
                logging.error(f"重启智能体 {agent_name} 失败: {e}")

    def auto_register_guild(self, guild_name):
        # 动态导入并注册 Guild
        try:
            module = importlib.import_module(f"agents.guilds.{guild_name.lower()}")
            guild_class = getattr(module, guild_name)
            from agents.tool_agent import ToolCollective
            guild = guild_class(ToolCollective())
            self.register(guild_name, guild)
            logging.info(f"自动注册工会: {guild_name}")
            self.save_registry()
            return guild
        except Exception as e:
            logging.error(f"自动注册工会 {guild_name} 失败: {e}")
            return None

    def list_agents(self):
        return list(self.registry.keys())

    def upgrade_agent(self, agent_name, new_agent_obj):
        self.registry[agent_name] = new_agent_obj
        logging.info(f"升级/替换智能体: {agent_name}")
        self.save_registry() 