import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tool_agent import ToolAgent

if __name__ == "__main__":
    agent = ToolAgent(name="工具智能体")
    user_query = "以商汤科技为关键词，搜索相关新闻"
    # 明确指定method参数
    result = agent.call_tool_by_name("search_news", {"query": "商汤科技"})
    print(f"【工具智能体】任务结果：\n{result}") 