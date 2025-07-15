from tools.mcp.base import MCPTool
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models.agent_model import AgentModel
from config.settings import SQLALCHEMY_DATABASE_URL
from typing import Dict, Any

class DatabaseOperationTool(MCPTool):
    def __init__(self):
        super().__init__(
            name="database_operation",
            description="数据库操作工具，支持结构同步、表结构查询、数据增删改查等多方法。"
        )
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self._methods = {
            "sync_schema": {
                "description": "同步数据库结构（建表/升级）",
                "parameters": {}
            },
            "get_table_info": {
                "description": "获取agents表结构信息",
                "parameters": {}
            },
            "query_agents": {
                "description": "查询所有agent记录",
                "parameters": {}
            },
            "insert_agent": {
                "description": "插入一条agent记录",
                "parameters": {
                    "key": {"type": "string", "description": "agent唯一key"},
                    "name": {"type": "string", "description": "agent名称"},
                    "type": {"type": "string", "description": "agent类型"}
                }
            },
            "delete_agent": {
                "description": "根据key删除agent记录",
                "parameters": {
                    "key": {"type": "string", "description": "agent唯一key"}
                }
            },
            "update_agent": {
                "description": "根据key更新agent名称/类型",
                "parameters": {
                    "key": {"type": "string", "description": "agent唯一key"},
                    "name": {"type": "string", "description": "新名称", "required": False},
                    "type": {"type": "string", "description": "新类型", "required": False}
                }
            }
        }

    def get_methods(self) -> Dict[str, Any]:
        """返回所有方法名、描述、参数schema"""
        return self._methods

    def get_schema(self) -> Dict[str, Any]:
        """返回工具整体schema，含所有方法"""
        return {
            "name": self.name,
            "description": self.description,
            "methods": self.get_methods()
        }

    def get_parameters(self) -> Dict[str, Any]:
        """兼容旧接口，返回所有方法参数schema"""
        return self.get_methods()

    def execute(self, method: str, **kwargs):
        if not method or method not in self._methods:
            return f"不支持的方法: {method}"
        try:
            if method == "sync_schema":
                return self.sync_schema()
            elif method == "get_table_info":
                return self.get_table_info()
            elif method == "query_agents":
                return self.query_agents()
            elif method == "insert_agent":
                return self.insert_agent(kwargs)
            elif method == "delete_agent":
                return self.delete_agent(kwargs)
            elif method == "update_agent":
                return self.update_agent(kwargs)
            else:
                return f"未知方法: {method}"
        except Exception as e:
            return f"数据库操作失败: {e}"

    def sync_schema(self):
        from models.agent_model import Base
        Base.metadata.create_all(self.engine)
        return '数据库结构同步完成。'

    def get_table_info(self):
        inspector = inspect(self.engine)
        if 'agents' in inspector.get_table_names():
            columns = inspector.get_columns('agents')
            info = '\n'.join([f"{col['name']}: {col['type']}" for col in columns])
            return f"agents表结构:\n{info}"
        return '未找到agents表。'

    def query_agents(self):
        session = self.Session()
        try:
            agents = session.query(AgentModel).all()
            result = [f"id={a.id}, key={a.key}, name={a.name}, type={a.type}, enabled={a.enabled}" for a in agents]
            return '\n'.join(result) if result else '无数据。'
        finally:
            session.close()

    def insert_agent(self, kwargs):
        session = self.Session()
        try:
            key = kwargs.get('key', 'default_key')
            name = kwargs.get('name', '新智能体')
            type_ = kwargs.get('type', 'custom')
            agent = AgentModel(key=key, name=name, type=type_)
            session.add(agent)
            session.commit()
            return f'已插入agent: key={key}, name={name}, type={type_}'
        except Exception as e:
            session.rollback()
            return f'插入失败: {e}'
        finally:
            session.close()

    def delete_agent(self, kwargs):
        session = self.Session()
        try:
            key = kwargs.get('key')
            if not key:
                return '请提供要删除的key参数。'
            count = session.query(AgentModel).filter_by(key=key).delete()
            session.commit()
            return f'已删除{count}条记录。'
        except Exception as e:
            session.rollback()
            return f'删除失败: {e}'
        finally:
            session.close()

    def update_agent(self, kwargs):
        session = self.Session()
        try:
            key = kwargs.get('key')
            if not key:
                return '请提供要更新的key参数。'
            agent = session.query(AgentModel).filter_by(key=key).first()
            if not agent:
                return '未找到指定key的记录。'
            if 'name' in kwargs:
                agent.name = kwargs['name']
            if 'type' in kwargs:
                agent.type = kwargs['type']
            session.commit()
            return f'已更新agent: key={key}, name={agent.name}, type={agent.type}'
        except Exception as e:
            session.rollback()
            return f'更新失败: {e}'
        finally:
            session.close() 