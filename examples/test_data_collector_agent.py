import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tool_agent import ToolAgent

if __name__ == "__main__":
    agent = ToolAgent(name="工具智能体")
    user_query = "以朗视仪器为关键词，搜索相关新闻"
    result = agent.select_and_call_tool(user_query)
    print(f"【工具智能体】任务结果：\n{result}") 