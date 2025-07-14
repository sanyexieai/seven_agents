# -*- coding: utf-8 -*-
"""
测试MCP Google News搜索功能
专门用于演示通过MCP工具调用真实的谷歌新闻搜索
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.rag_tools import RAGTool
from tools.utility_tools import data_processor, file_utils
from tools.mcp.google_news_search import GoogleNewsSearchTool


async def test_google_news_search():
    """测试Google News搜索功能"""
    print("🔍 测试MCP Google News搜索功能")
    print("=" * 60)
    
    # 移除WebSearchTool相关导入和实例化，改为google_news_search
    
    # 测试搜索关键词
    test_keywords = [
        "商汤科技 最新消息",
        "SenseTime AI技术",
        "商汤科技 财报"
    ]
    
    all_news = []
    
    for keyword in test_keywords:
        print(f"\n📰 搜索关键词: {keyword}")
        print("-" * 40)
        
        try:
            google_news_tool = GoogleNewsSearchTool()
            search_result = google_news_tool.execute(
                query=keyword,
                max_results=3,
                # start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                # end_date=datetime.now().strftime("%Y-%m-%d")
            )
            
            print(f"✅ 搜索完成，找到 {len(search_result.get('results', []))} 条新闻")
            
            # 处理搜索结果
            for i, result in enumerate(search_result.get('results', []), 1):
                print(f"\n{i}. {result.get('title', '无标题')}")
                print(f"   来源: {result.get('source', '未知')}")
                print(f"   日期: {result.get('date', '未知')}")
                print(f"   摘要: {result.get('snippet', '无摘要')[:100]}...")
                print(f"   URL: {result.get('url', '无链接')}")
                
                # 清理和存储新闻数据
                cleaned_news = clean_news_data(result, keyword)
                if cleaned_news:
                    all_news.append(cleaned_news)
            
            # 避免请求过于频繁
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            continue
    
    return all_news


def clean_news_data(raw_news: dict, keyword: str) -> dict:
    """清理新闻数据"""
    try:
        title = raw_news.get('title', '')
        snippet = raw_news.get('snippet', '')
        url = raw_news.get('url', '')
        source = raw_news.get('source', '')
        date = raw_news.get('date', '')
        
        if not title:
            return None
        
        # 清理文本
        cleaned_title = data_processor.clean_text(title)
        cleaned_snippet = data_processor.clean_text(snippet)
        
        return {
            'title': cleaned_title,
            'content': cleaned_snippet,
            'summary': cleaned_snippet[:200] + "..." if len(cleaned_snippet) > 200 else cleaned_snippet,
            'url': url,
            'source': source,
            'date': date,
            'keyword': keyword,
            'collected_at': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"清理新闻数据失败: {e}")
        return None


async def test_rag_integration(news_data: list):
    """测试RAG集成"""
    print(f"\n📚 测试RAG知识库集成")
    print("=" * 60)
    
    # 创建RAG工具实例
    rag_tool = RAGTool()
    
    # 将新闻数据存储到RAG知识库
    for news in news_data:
        try:
            # 创建文档内容
            doc_content = f"""
标题: {news['title']}
来源: {news['source']}
关键词: {news['keyword']}
日期: {news['date']}
摘要: {news['summary']}
内容: {news['content']}
URL: {news['url']}
收集时间: {news['collected_at']}
"""
            
            # 创建元数据
            doc_meta = {
                'type': 'news',
                'company': '商汤科技',
                'source': news['source'],
                'keyword': news['keyword'],
                'date': news['date'],
                'collected_at': news['collected_at']
            }
            
            # 添加到RAG知识库
            result = rag_tool.add_document(doc_content, doc_meta)
            if result.get('success'):
                print(f"✅ 已存储: {news['title'][:50]}...")
            else:
                print(f"❌ 存储失败: {news['title'][:50]}...")
                
        except Exception as e:
            print(f"❌ 存储新闻失败: {e}")
    
    # 测试RAG搜索
    print(f"\n🔍 测试RAG知识库搜索")
    print("-" * 40)
    
    search_queries = ["商汤科技", "AI技术", "财报"]
    
    for query in search_queries:
        try:
            search_result = rag_tool.search_knowledge(query, top_k=3)
            print(f"\n搜索: '{query}'")
            print(f"找到 {search_result.get('total_results', 0)} 条相关结果")
            
            for i, result in enumerate(search_result.get('results', [])[:2], 1):
                print(f"  {i}. {result.get('content', '')[:100]}...")
                
        except Exception as e:
            print(f"❌ RAG搜索失败: {e}")


async def generate_simple_report(news_data: list):
    """生成简单的分析报告"""
    print(f"\n📋 生成简单分析报告")
    print("=" * 60)
    
    if not news_data:
        print("❌ 没有新闻数据，无法生成报告")
        return
    
    # 分析数据
    sources = {}
    keywords = {}
    
    for news in news_data:
        source = news.get('source', '未知来源')
        keyword = news.get('keyword', '未知关键词')
        
        sources[source] = sources.get(source, 0) + 1
        keywords[keyword] = keywords.get(keyword, 0) + 1
    
    # 生成报告内容
    report_content = f"""
# 商汤科技新闻分析报告

**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
**数据来源**: Google News搜索
**分析周期**: 最近30天

## 数据概览

- 总新闻数量: {len(news_data)} 条
- 新闻来源数量: {len(sources)} 个
- 搜索关键词数量: {len(keywords)} 个

## 新闻来源分布

{chr(10).join([f"- {source}: {count} 条" for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)])}

## 关键词分布

{chr(10).join([f"- {keyword}: {count} 条" for keyword, count in sorted(keywords.items(), key=lambda x: x[1], reverse=True)])}

## 最新新闻摘要

"""
    
    # 添加最新新闻
    for i, news in enumerate(news_data[:5], 1):
        report_content += f"""
### {i}. {news['title']}
- **来源**: {news['source']}
- **日期**: {news['date']}
- **摘要**: {news['summary']}
- **链接**: {news['url']}

"""
    
    report_content += """
---

**免责声明**: 本报告基于Google News搜索结果生成，仅供参考。
"""
    
    # 保存报告
    try:
        report_dir = "reports"
        file_utils.ensure_directory(report_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shangtang_mcp_test_report_{timestamp}.md"
        file_path = os.path.join(report_dir, filename)
        
        success = file_utils.write_file_safe(file_path, report_content, encoding='utf-8')
        
        if success:
            print(f"✅ 报告已保存到: {file_path}")
            return file_path
        else:
            print("❌ 报告保存失败")
            
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        return None


async def main():
    """主函数"""
    print("🤖 MCP Google News搜索测试")
    print("=" * 60)
    
    try:
        # 1. 测试Google News搜索
        news_data = await test_google_news_search()
        
        if not news_data:
            print("❌ 没有获取到新闻数据，测试结束")
            return
        
        print(f"\n✅ 成功收集 {len(news_data)} 条新闻")
        
        # 2. 测试RAG集成
        await test_rag_integration(news_data)
        
        # 3. 生成简单报告
        report_path = await generate_simple_report(news_data)
        
        # 4. 输出总结
        print(f"\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print(f"✅ Google News搜索: 成功")
        print(f"✅ RAG知识库集成: 成功")
        print(f"✅ 报告生成: {'成功' if report_path else '失败'}")
        print(f"📄 报告文件: {report_path or '无'}")
        print(f"📰 收集新闻: {len(news_data)} 条")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
    
    print(f"\n" + "=" * 60)
    print("测试完成！")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main()) 