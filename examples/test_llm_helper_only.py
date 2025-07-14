# -*- coding: utf-8 -*-
"""
LLMHelper单独测试示例
不依赖CodeExecutor，只测试LLMHelper功能
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.utils.llm_helper import LLMHelper
from config.llm_config import LLMConfig
from config.settings import get_settings


def test_llm_helper_import():
    """测试LLMHelper导入"""
    print("=== 测试LLMHelper导入 ===")
    try:
        from agents.utils.llm_helper import LLMHelper
        from config.llm_config import LLMConfig
        print("✅ LLMHelper导入成功")
        return True
    except Exception as e:
        print(f"❌ LLMHelper导入失败: {e}")
        return False


def test_llm_config():
    """测试LLM配置"""
    print("\n=== 测试LLM配置 ===")
    try:
        # 从设置创建配置
        config = LLMConfig.from_settings()
        print(f"✅ 配置创建成功")
        print(f"   - 模型: {config.model}")
        print(f"   - 最大token: {config.max_tokens}")
        print(f"   - 温度: {config.temperature}")
        print(f"   - API密钥: {'已设置' if config.api_key else '未设置'}")
        return config
    except Exception as e:
        print(f"❌ 配置创建失败: {e}")
        return None


def test_llm_helper_creation(config):
    """测试LLMHelper创建"""
    print("\n=== 测试LLMHelper创建 ===")
    try:
        if not config.api_key:
            print("⚠️ 未设置API密钥，跳过实际调用测试")
            return None
        
        llm = LLMHelper(config)
        print("✅ LLMHelper创建成功")
        return llm
    except Exception as e:
        print(f"❌ LLMHelper创建失败: {e}")
        return None


def test_llm_call(llm):
    """测试LLM调用"""
    print("\n=== 测试LLM调用 ===")
    if not llm:
        print("⚠️ LLM未创建，跳过调用测试")
        return
    
    try:
        # 测试同步调用
        response = llm.call("请用一句话介绍人工智能")
        print(f"✅ 同步调用成功")
        print(f"   回复: {response[:100]}...")
        
        # 测试YAML解析
        yaml_response = llm.call("请用YAML格式回答：列出三个编程语言")
        parsed = llm.parse_yaml_response(yaml_response)
        print(f"✅ YAML解析成功")
        print(f"   解析结果: {parsed}")
        
    except Exception as e:
        print(f"❌ LLM调用失败: {e}")


def test_langchain_integration():
    """测试LangChain集成"""
    print("\n=== 测试LangChain集成 ===")
    try:
        from langchain_core.language_models.llms import LLM
        from agents.utils.llm_helper import LLMHelper
        
        # 检查是否继承自LangChain LLM
        llm = LLMHelper(LLMConfig(api_key="test"))
        if isinstance(llm, LLM):
            print("✅ LLMHelper正确继承自LangChain LLM")
        else:
            print("❌ LLMHelper未正确继承LangChain LLM")
            
        # 检查是否有必需的方法
        required_methods = ['_call', '_acall', '_llm_type']
        for method in required_methods:
            if hasattr(llm, method):
                print(f"✅ 方法 {method} 存在")
            else:
                print(f"❌ 方法 {method} 缺失")
                
    except Exception as e:
        print(f"❌ LangChain集成测试失败: {e}")


def main():
    """主函数"""
    print("🤖 LLMHelper单独测试\n")
    
    # 测试导入
    if not test_llm_helper_import():
        return
    
    # 测试配置
    config = test_llm_config()
    if not config:
        return
    
    # 测试LLMHelper创建
    llm = test_llm_helper_creation(config)
    
    # 测试LLM调用
    test_llm_call(llm)
    
    # 测试LangChain集成
    test_langchain_integration()
    
    print("\n✅ 所有测试完成!")


if __name__ == "__main__":
    main() 