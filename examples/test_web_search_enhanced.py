# -*- coding: utf-8 -*-
"""
增强网络搜索功能测试
"""

import os
import random
import sys
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.mcp.web_search import WebSearchTool


def test_web_search():
    """测试普通网页搜索"""
    print("=== 测试普通网页搜索 ===")
    tool = WebSearchTool()
    
    result = tool.execute(query="Python编程", max_results=3)
    print(f"查询: {result['query']}")
    print(f"搜索引擎: {result['search_engine']}")
    print(f"结果数量: {result['total_results']}")
    #等待2秒
    time.sleep(random.uniform(2, 6))
    for i, item in enumerate(result['results'], 1):
        print(f"  {i}. {item['title']}")
        print(f"     URL: {item['url']}")
        print(f"     摘要: {item['snippet'][:100]}...")
        print()


def test_news_search():
    """测试新闻搜索"""
    print("=== 测试新闻搜索 ===")
    tool = WebSearchTool()
    
    result = tool.execute(
        query="人工智能", 
        max_results=3, 
        search_type="news",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    #等待2秒
    # time.sleep(random.uniform(2, 6))
    
    print(f"查询: {result['query']}")
    print(f"搜索引擎: {result['search_engine']}")
    print(f"搜索类型: {result['search_type']}")
    print(f"结果数量: {result['total_results']}")
    
    for i, item in enumerate(result['results'], 1):
        print(f"  {i}. {item['title']}")
        print(f"     URL: {item['url']}")
        print(f"     来源: {item.get('source', 'N/A')}")
        print(f"     日期: {item.get('date', 'N/A')}")
        print(f"     摘要: {item['snippet'][:100]}...")
        print()


def test_different_engines():
    """测试不同搜索引擎"""
    print("=== 测试不同搜索引擎 ===")
    tool = WebSearchTool()
    
    engines = ["google", "bing", "duckduckgo"]
    for engine in engines:
        print(f"\n--- {engine.upper()} 搜索 ---")
        try:
            result = tool.execute(query="机器学习", max_results=2, search_engine=engine)
            print(f"结果数量: {result['total_results']}")
            #等待2秒
            # time.sleep(random.uniform(2, 6))
            if result['results']:
                print(f"第一个结果: {result['results'][0]['title']}")
        except NotImplementedError as e:
            print(f"❌ {engine} 搜索功能尚未实现: {e}")
        except Exception as e:
            print(f"❌ {engine} 搜索失败: {e}")


def main():
    """主函数"""
    print("🔍 增强网络搜索功能测试\n")
    
    try:
        test_web_search()
        test_news_search()
        test_different_engines()
        print("✅ 所有测试完成!")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    main() 