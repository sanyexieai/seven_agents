import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models.agent_model import AgentModel, Base
from agents import (
    CoordinatorAgent, ResearchAgent, AnalysisAgent,
    ToolAgent, CommunicationAgent, ExecutionAgent, MonitorAgent
)
from config.settings import SQLALCHEMY_DATABASE_URL

# 智能体类型与类的映射
AGENT_CLASS_MAP = {
    'coordinator': CoordinatorAgent,
    'research': ResearchAgent,
    'analysis': AnalysisAgent,
    'tool': ToolAgent,
    'communication': CommunicationAgent,
    'execution': ExecutionAgent,
    'monitor': MonitorAgent,
}

# 创建数据库引擎和会话
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """创建表结构并自动同步数据库（如未存在）。"""
    # 检查key字段是否存在
    inspector = engine.dialect.inspector(engine)
    if 'agents' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('agents')]
        if 'key' not in columns:
            # 如果key字段不存在，添加它
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE agents ADD COLUMN key VARCHAR(64) UNIQUE NOT NULL DEFAULT 'default_key'"))
                conn.commit()
                print("已添加key字段到agents表")
    
    # 创建所有表（如果不存在）
    Base.metadata.create_all(engine)
    print("数据库结构已同步")

def load_agents_from_db():
    """从数据库加载所有启用的智能体实例。"""
    session = SessionLocal()
    agents = []
    try:
        for row in session.query(AgentModel).filter_by(enabled=True):
            agent_cls = AGENT_CLASS_MAP.get(row.type)
            if agent_cls:
                config = row.config or {}
                agent = agent_cls(name=row.name, **config)
                agents.append(agent)
    finally:
        session.close()
    return agents