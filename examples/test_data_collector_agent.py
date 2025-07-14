import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_collector_agent import DataCollectorAgent

if __name__ == "__main__":
    agent = DataCollectorAgent(name="数据搜集Agent")
    keyword = "朗视仪器"
    result = agent.collect_data(keyword)
    print(f"【朗视仪器】相关数据搜集结果：\n{result}") 