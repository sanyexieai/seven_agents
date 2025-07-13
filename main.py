import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import subprocess
from agents.orchestrator import AgentOrchestrator

def run_alembic_upgrade():
    """自动执行 Alembic 数据库迁移到最新版本。"""
    subprocess.run(['alembic', 'upgrade', 'head'], cwd=os.path.dirname(__file__))

if __name__ == '__main__':
    run_alembic_upgrade()
    # 测试：加载所有智能体并执行一次任务
    orchestrator = AgentOrchestrator()
    print("已加载智能体:", orchestrator.list_agents())
    for agent_type in orchestrator.list_agents():
        result = orchestrator.execute_task("测试任务", agent_type=agent_type)
        print(f"[{agent_type}] 结果: {result}") 