import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import subprocess
from agents.orchestrator import AgentOrchestrator
from database.db_sync import db_sync
from config.settings import ENVIRONMENT, DATABASE_SYNC_MODE
from agents.meta_agent import MetaAgent
from agents.task_incubator import TaskIncubator
from agents.orchestrator import Orchestrator
from agents.guilds.database_guild import DatabaseGuild
from agents.tool_agent import ToolCollective

def run_alembic_upgrade():
    """自动执行 Alembic 数据库迁移到最新版本。"""
    subprocess.run(['alembic', 'upgrade', 'head'], cwd=os.path.dirname(__file__))

def sync_database_structure():
    """根据环境变量选择数据库同步方式"""
    print(f"当前环境: {ENVIRONMENT}")
    print(f"数据库同步模式: {DATABASE_SYNC_MODE}")
    
    if DATABASE_SYNC_MODE == 'none':
        print("跳过数据库同步")
        return
    
    elif DATABASE_SYNC_MODE == 'alembic' or ENVIRONMENT == 'production':
        print("使用Alembic进行数据库迁移...")
        run_alembic_upgrade()
    
    elif DATABASE_SYNC_MODE == 'auto' or ENVIRONMENT == 'development':
        print("使用SQLAlchemy自动同步数据库结构...")
        db_sync.sync_database()
        
        # 开发环境也可以同时运行Alembic作为备份
        if ENVIRONMENT == 'development':
            print("开发环境：同时执行Alembic迁移作为备份...")
            run_alembic_upgrade()
    
    else:
        print(f"未知的同步模式: {DATABASE_SYNC_MODE}，使用默认的SQLAlchemy自动同步")
        db_sync.sync_database()

# 1. 初始化各智能体
meta = MetaAgent()
tool_collective = ToolCollective()
db_guild = DatabaseGuild(tool_collective)
incubator = TaskIncubator()
orchestrator = Orchestrator(meta)

# 2. 注册到元治理
meta.register("ToolCollective", tool_collective)
meta.register("DatabaseGuild", db_guild)
meta.register("TaskIncubator", incubator)
meta.register("Orchestrator", orchestrator)

# 3. 用户输入
user_input = "查询 test_table 所有数据"

# 4. 任务孵化
task_blueprint = incubator.incubate(user_input)

# 5. 调度分发
result = orchestrator.dispatch(task_blueprint)

print("最终结果：", result)

if __name__ == '__main__':
    # 根据环境变量同步数据库结构
    sync_database_structure()
    
    # 测试：加载所有智能体并执行一次任务
    orchestrator = AgentOrchestrator()
    print("已加载智能体:", orchestrator.list_agents())
    for agent_type in orchestrator.list_agents():
        result = orchestrator.execute_task("测试任务", agent_type=agent_type)
        print(f"[{agent_type}] 结果: {result}") 