# -*- coding: utf-8 -*-
"""
MCP工具测试示例
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.mcp import (
    MCPTool,
    MCPClient,
    MCPToolManager,
    WebSearchTool,
    FileOperationTool,
    APICallTool,
)
from tools.mcp_tools import mcp_tool_manager


def test_mcp_tools_import():
    """测试MCP工具导入"""
    print("=== 测试MCP工具导入 ===")
    try:
        from tools.mcp import MCPTool, WebSearchTool, FileOperationTool, APICallTool
        print("✅ MCP工具导入成功")
        return True
    except Exception as e:
        print(f"❌ MCP工具导入失败: {e}")
        return False


def test_web_search_tool():
    """测试网络搜索工具"""
    print("\n=== 测试网络搜索工具 ===")
    try:
        tool = WebSearchTool()
        result = tool.execute(query="人工智能", max_results=3)
        print(f"✅ 网络搜索工具执行成功")
        print(f"   查询: {result['query']}")
        print(f"   结果数量: {result['total_results']}")
        return True
    except Exception as e:
        print(f"❌ 网络搜索工具执行失败: {e}")
        return False


def test_file_operation_tool():
    """测试文件操作工具"""
    print("\n=== 测试文件操作工具 ===")
    try:
        tool = FileOperationTool()
        test_file = "test_file.txt"
        test_content = "这是一个测试文件的内容"
        
        # 测试写入
        result = tool.execute(operation="write", file_path=test_file, content=test_content)
        print(f"✅ 文件写入: {result['success']}")
        
        # 测试读取
        result = tool.execute(operation="read", file_path=test_file)
        print(f"✅ 文件读取: {result['success']}")
        print(f"   内容: {result['content']}")
        
        # 测试追加
        result = tool.execute(operation="append", file_path=test_file, content="\n追加的内容")
        print(f"✅ 文件追加: {result['success']}")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return True
    except Exception as e:
        print(f"❌ 文件操作工具执行失败: {e}")
        return False


def test_api_call_tool():
    """测试API调用工具"""
    print("\n=== 测试API调用工具 ===")
    try:
        tool = APICallTool()
        result = tool.execute(
            method="GET",
            url="https://httpbin.org/json"
        )
        print(f"✅ API调用工具执行成功")
        print(f"   状态码: {result['status_code']}")
        return True
    except Exception as e:
        print(f"❌ API调用工具执行失败: {e}")
        return False


def test_mcp_tool_manager():
    """测试MCP工具管理器"""
    print("\n=== 测试MCP工具管理器 ===")
    try:
        # 获取工具列表
        tools = mcp_tool_manager.list_tools()
        print(f"✅ 工具管理器获取工具列表成功")
        print(f"   工具数量: {len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # 测试工具执行
        result = mcp_tool_manager.execute_tool("web_search", {"query": "测试", "max_results": 2})
        print(f"✅ 工具管理器执行工具成功")
        print(f"   结果: {result['total_results']} 个结果")
        
        return True
    except Exception as e:
        print(f"❌ 工具管理器测试失败: {e}")
        return False


def test_mcp_client():
    """测试MCP客户端"""
    print("\n=== 测试MCP客户端 ===")
    try:
        # 创建客户端（这里使用示例URL）
        client = MCPClient("https://example.com/api")
        print("✅ MCP客户端创建成功")
        
        # 注册客户端到管理器
        mcp_tool_manager.register_mcp_client("test_client", client)
        print("✅ MCP客户端注册成功")
        
        return True
    except Exception as e:
        print(f"❌ MCP客户端测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🤖 MCP工具测试\n")
    
    # 测试导入
    if not test_mcp_tools_import():
        return
    
    # 测试各个工具
    test_web_search_tool()
    test_file_operation_tool()
    test_api_call_tool()
    
    # 测试工具管理器
    test_mcp_tool_manager()
    
    # 测试客户端
    test_mcp_client()
    
    print("\n✅ 所有MCP工具测试完成!")


if __name__ == "__main__":
    main() 