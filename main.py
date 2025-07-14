import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import subprocess
from agents.orchestrator import AgentOrchestrator
from database.db_sync import db_sync
from config.settings import ENVIRONMENT, DATABASE_SYNC_MODE

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

if __name__ == '__main__':
    # 根据环境变量同步数据库结构
    sync_database_structure()
    
    # 测试：加载所有智能体并执行一次任务
    orchestrator = AgentOrchestrator()
    print("已加载智能体:", orchestrator.list_agents())
    for agent_type in orchestrator.list_agents():
        result = orchestrator.execute_task("测试任务", agent_type=agent_type)
        print(f"[{agent_type}] 结果: {result}") 