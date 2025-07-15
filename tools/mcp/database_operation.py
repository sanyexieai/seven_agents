from tools.mcp import mcp
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from config.settings import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

@mcp.tool(description="创建表，传入SQL建表语句")
async def database_create_table(sql: str):
    """执行CREATE TABLE语句创建新表"""
    session = Session()
    try:
        session.execute(text(sql))
        session.commit()
        return {"success": True, "message": "表创建成功"}
    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        session.close()

@mcp.tool(description="删除表，传入表名")
async def database_drop_table(table_name: str):
    """删除指定表"""
    session = Session()
    try:
        session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        session.commit()
        return {"success": True, "message": f"表 {table_name} 已删除"}
    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        session.close()

@mcp.tool(description="通用SQL查询，支持自定义SQL语句和参数")
async def database_execute_sql(sql: str, params: dict = None):
    """
    通用SQL执行工具，支持任意查询/写入/更新/删除。
    - sql: SQL语句（如SELECT * FROM tablename WHERE name=:name）
    - params: 参数字典（如{"name": "张三"}）
    """
    session = Session()
    try:
        result = session.execute(text(sql), params or {})
        if sql.strip().lower().startswith("select"):
            rows = result.fetchall()
            return [dict(row) for row in rows]
        else:
            session.commit()
            return {"success": True, "rowcount": result.rowcount}
    except Exception as e:
        session.rollback()
        return {"success": False, "error": str(e)}
    finally:
        session.close() 