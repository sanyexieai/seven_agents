"""
工具调用示例
展示如何使用各种工具模块
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.mcp_tools import mcp_tool_manager
from tools.rag_tools import rag_tool
from tools.utility_tools import data_processor, file_utils, format_converter, validation_utils
from agents.tool_agent import ToolAgent


def demo_mcp_tools():
    """演示MCP工具"""
    print("=== MCP工具演示 ===")
    
    # 1. 网络搜索
    print("\n1. 网络搜索:")
    search_result = mcp_tool_manager.execute_tool('web_search', {
        'query': '人工智能发展趋势',
        'max_results': 3
    })
    print(f"搜索结果: {search_result}")
    
    # 2. 文件操作
    print("\n2. 文件操作:")
    # 写入测试文件
    write_result = mcp_tool_manager.execute_tool('file_operation', {
        'operation': 'write',
        'file_path': 'test_file.txt',
        'content': '这是一个测试文件的内容。\n包含多行文本。'
    })
    print(f"写入结果: {write_result}")
    
    # 读取文件
    read_result = mcp_tool_manager.execute_tool('file_operation', {
        'operation': 'read',
        'file_path': 'test_file.txt'
    })
    print(f"读取结果: {read_result}")
    
    # 3. API调用
    print("\n3. API调用:")
    api_result = mcp_tool_manager.execute_tool('api_call', {
        'method': 'GET',
        'url': 'https://httpbin.org/json'
    })
    print(f"API调用结果: {api_result}")


def demo_rag_tools():
    """演示RAG工具"""
    print("\n=== RAG工具演示 ===")
    
    # 1. 添加文档到知识库
    print("\n1. 添加文档到知识库:")
    add_result = rag_tool.add_document(
        content="人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
        metadata={"source": "demo", "topic": "AI"}
    )
    print(f"添加文档结果: {add_result}")
    
    # 2. 搜索知识库
    print("\n2. 搜索知识库:")
    search_result = rag_tool.search_knowledge("人工智能", top_k=3)
    print(f"搜索结果: {search_result}")
    
    # 3. 生成回答
    print("\n3. 生成回答:")
    answer_result = rag_tool.generate_answer("什么是人工智能？")
    print(f"生成回答: {answer_result}")
    
    # 4. 获取知识库统计
    print("\n4. 知识库统计:")
    stats = rag_tool.get_knowledge_stats()
    print(f"统计信息: {stats}")


def demo_utility_tools():
    """演示通用工具"""
    print("\n=== 通用工具演示 ===")
    
    test_text = "这是一个测试文本，包含一些特殊字符！@#$%^&*()，还有邮箱地址：test@example.com 和网址：https://www.example.com"
    
    # 1. 数据处理
    print("\n1. 数据处理:")
    cleaned_text = data_processor.clean_text(test_text)
    print(f"清理后文本: {cleaned_text}")
    
    emails = data_processor.extract_emails(test_text)
    print(f"提取的邮箱: {emails}")
    
    urls = data_processor.extract_urls(test_text)
    print(f"提取的URL: {urls}")
    
    word_count = data_processor.count_words(test_text)
    print(f"单词数量: {word_count}")
    
    summary = data_processor.generate_summary(test_text, max_length=50)
    print(f"文本摘要: {summary}")
    
    # 2. 格式转换
    print("\n2. 格式转换:")
    json_data = '{"name": "张三", "age": 25, "city": "北京"}'
    yaml_result = format_converter.json_to_yaml(json_data)
    print(f"JSON转YAML: {yaml_result}")
    
    # 3. 验证工具
    print("\n3. 验证工具:")
    email_valid = validation_utils.is_valid_email("test@example.com")
    print(f"邮箱验证: {email_valid}")
    
    url_valid = validation_utils.is_valid_url("https://www.example.com")
    print(f"URL验证: {url_valid}")
    
    json_valid = validation_utils.is_valid_json(json_data)
    print(f"JSON验证: {json_valid}")


def demo_tool_agent():
    """演示工具智能体"""
    print("\n=== 工具智能体演示 ===")
    
    # 创建工具智能体
    tool_agent = ToolAgent("工具专家")
    
    # 1. 列出可用工具
    print("\n1. 可用工具列表:")
    tools = tool_agent.list_available_tools()
    for tool in tools:
        print(f"  - {tool['type']}: {tool['name']} - {tool['description']}")
    
    # 2. 执行搜索任务
    print("\n2. 执行搜索任务:")
    search_result = tool_agent.run("搜索人工智能", query="AI发展趋势", max_results=3)
    print(f"搜索结果: {search_result}")
    
    # 3. 执行数据处理任务
    print("\n3. 执行数据处理任务:")
    text = "这是一个需要清理的文本，包含很多特殊字符！@#$%^&*()"
    data_result = tool_agent.run("数据处理清理", text=text)
    print(f"数据处理结果: {data_result}")
    
    # 4. 执行验证任务
    print("\n4. 执行验证任务:")
    validation_result = tool_agent.run("验证邮箱", value="test@example.com")
    print(f"验证结果: {validation_result}")


def main():
    """主函数"""
    print("工具模块演示开始...")
    
    try:
        # 演示各种工具
        demo_mcp_tools()
        demo_rag_tools()
        demo_utility_tools()
        demo_tool_agent()
        
        print("\n=== 演示完成 ===")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")


if __name__ == "__main__":
    main() 