# -*- coding: utf-8 -*-
"""
数据分析智能体使用示例
"""

import os
import sys
import pandas as pd
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_analysis_agent import DataAnalysisAgent
from config.settings import get_settings


def create_sample_data():
    """创建示例数据"""
    # 创建销售数据
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    data = {
        'date': dates,
        'product': np.random.choice(['A', 'B', 'C'], 100),
        'sales': np.random.randint(10, 1000, 100),
        'price': np.random.uniform(10, 100, 100),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 100)
    }
    
    df = pd.DataFrame(data)
    
    # 保存到文件
    output_dir = 'examples/data'
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, 'sales_data.csv')
    df.to_csv(file_path, index=False)
    
    print(f"示例数据已保存到: {file_path}")
    return file_path


def main():
    """主函数"""
    print("=== 数据分析智能体示例 ===\n")
    
    # 检查环境变量
    settings = get_settings()
    if not settings.openai_api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    # 创建示例数据
    data_file = create_sample_data()
    
    # 创建数据分析智能体
    print("🤖 初始化数据分析智能体...")
    agent = DataAnalysisAgent(
        name="数据分析助手",
        output_dir="examples/analysis_outputs"
    )
    
    # 设置数据文件
    agent.set_data_file(data_file)
    
    # 执行数据分析任务
    print("\n📊 开始数据分析...")
    
    # 任务1: 基础统计分析
    print("\n1. 基础统计分析")
    result1 = agent.analyze_data(
        "请对销售数据进行基础统计分析，包括销售总额、平均价格、各产品销量等"
    )
    
    if result1['success']:
        print("✅ 基础统计分析完成")
        print(f"📁 结果保存在: {result1['session_dir']}")
        print(f"📋 执行结果:\n{result1['formatted_result']}")
    else:
        print(f"❌ 分析失败: {result1['error']}")
    
    # 任务2: 可视化分析
    print("\n2. 可视化分析")
    result2 = agent.analyze_data(
        "请创建销售数据的可视化图表，包括销售趋势图、产品销量对比图、地区分布图等"
    )
    
    if result2['success']:
        print("✅ 可视化分析完成")
        print(f"📁 结果保存在: {result2['session_dir']}")
        print(f"📋 执行结果:\n{result2['formatted_result']}")
    else:
        print(f"❌ 分析失败: {result2['error']}")
    
    # 任务3: 高级分析
    print("\n3. 高级分析")
    result3 = agent.analyze_data(
        "请进行高级数据分析，包括相关性分析、时间序列分析、异常值检测等"
    )
    
    if result3['success']:
        print("✅ 高级分析完成")
        print(f"📁 结果保存在: {result3['session_dir']}")
        print(f"📋 执行结果:\n{result3['formatted_result']}")
    else:
        print(f"❌ 分析失败: {result3['error']}")
    
    # 获取分析历史
    print("\n📚 分析历史:")
    history = agent.get_analysis_history()
    for i, record in enumerate(history, 1):
        print(f"  {i}. {record['user_input'][:50]}...")
    
    # 获取环境信息
    print(f"\n🔧 执行环境信息:")
    print(agent.get_environment_info())
    
    print("\n✅ 数据分析示例完成!")


if __name__ == "__main__":
    main() 