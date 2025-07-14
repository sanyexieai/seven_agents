# -*- coding: utf-8 -*-
"""
智能体调度者使用示例：自动分配并调用子智能体完成任务
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_coordinator import AgentCoordinatorAgent
from config.settings import get_settings


def main():
    print("=== 智能体调度者示例 ===\n")
    
    # 检查环境变量
    settings = get_settings()
    if not settings.openai_api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 初始化调度智能体
    print("🤖 初始化智能体调度者...")
    coordinator = AgentCoordinatorAgent(name="调度智能体")
    
    # 用户任务
    user_query = "以朗视仪器为关键词，搜索相关新闻"
    print(f"\n📋 用户任务: {user_query}")
    
    # 调用调度智能体自动分配并执行任务
    print("\n🚦 调度并执行...")
    result = coordinator.select_and_call_agent(user_query)
    print(f"\n【调度结果】\n{result}")

if __name__ == "__main__":
    main() 