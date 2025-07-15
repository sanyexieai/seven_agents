from tools.mcp import mcp
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models.agent_model import AgentModel
from config.settings import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

@mcp.tool()
async def sync_schema():
    from models.agent_model import Base
    Base.metadata.create_all(engine)
    return '数据库结构同步完成。'

@mcp.tool()
async def get_table_info():
    inspector = inspect(engine)
    if 'agents' in inspector.get_table_names():
        columns = inspector.get_columns('agents')
        info = '\n'.join([f"{col['name']}: {col['type']}" for col in columns])
        return f"agents表结构:\n{info}"
    return '未找到agents表。'

@mcp.tool()
async def query_agents():
    session = Session()
    try:
        agents = session.query(AgentModel).all()
        result = [f"id={a.id}, key={a.key}, name={a.name}, type={a.type}, enabled={a.enabled}" for a in agents]
        return '\n'.join(result) if result else '无数据。'
    finally:
        session.close()

@mcp.tool()
async def insert_agent(key: str, name: str, type: str):
    session = Session()
    try:
        agent = AgentModel(key=key, name=name, type=type)
        session.add(agent)
        session.commit()
        return f'已插入agent: key={key}, name={name}, type={type}'
    except Exception as e:
        session.rollback()
        return f'插入失败: {e}'
    finally:
        session.close()

@mcp.tool()
async def delete_agent(key: str):
    session = Session()
    try:
        count = session.query(AgentModel).filter_by(key=key).delete()
        session.commit()
        return f'已删除{count}条记录。'
    except Exception as e:
        session.rollback()
        return f'删除失败: {e}'
    finally:
        session.close()

@mcp.tool()
async def update_agent(key: str, name: str = None, type: str = None):
    session = Session()
    try:
        agent = session.query(AgentModel).filter_by(key=key).first()
        if not agent:
            return '未找到指定key的记录。'
        if name is not None:
            agent.name = name
        if type is not None:
            agent.type = type
        session.commit()
        return f'已更新agent: key={key}, name={agent.name}, type={agent.type}'
    except Exception as e:
        session.rollback()
        return f'更新失败: {e}'
    finally:
        session.close() 