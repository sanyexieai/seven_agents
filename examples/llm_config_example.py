# -*- coding: utf-8 -*-
"""
LLM配置使用示例
展示默认配置和手动配置的使用方法
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from agents.data_analysis_agent import DataAnalysisAgent
from config.llm_config import LLMConfig
from config.settings import get_settings


class TestAgent(BaseAgent):
    """测试智能体"""
    
    def _get_agent_description(self) -> str:
        return "测试智能体"


def example_default_config():
    """示例1: 使用默认配置"""
    print("=== 示例1: 使用默认配置 ===\n")
    
    # 创建智能体，不传任何LLM配置，使用默认配置
    agent = TestAgent("默认配置测试")
    
    # 执行任务
    result = agent.run("请简单介绍一下自己")
    print(f"智能体回复: {result}\n")


def example_custom_llm_params():
    """示例2: 使用自定义LLM参数"""
    print("=== 示例2: 使用自定义LLM参数 ===\n")
    
    # 创建智能体，传入自定义LLM参数
    agent = TestAgent(
        "自定义参数测试",
        llm={
            'model': 'gpt-4',
            'temperature': 0.3,
            'max_tokens': 500
        }
    )
    
    # 执行任务
    result = agent.run("请用简洁的语言介绍人工智能")
    print(f"智能体回复: {result}\n")


def example_custom_llm_config():
    """示例3: 使用完全自定义的LLM配置"""
    print("=== 示例3: 使用完全自定义的LLM配置 ===\n")
    
    # 创建自定义LLM配置
    custom_config = LLMConfig(
        api_key="your-custom-api-key",  # 这里需要替换为实际的API密钥
        base_url="https://api.openai.com/v1",
        model="gpt-4",
        max_tokens=800,
        temperature=0.5,
        # 备用API配置
        fallback_api_key="your-fallback-api-key",
        fallback_base_url="https://api.anthropic.com/v1",
        fallback_model="claude-3-sonnet-20240229"
    )
    
    # 创建智能体，传入自定义LLM配置
    agent = TestAgent(
        "自定义配置测试",
        llm_config=custom_config
    )
    
    # 执行任务
    result = agent.run("请详细解释机器学习的基本概念")
    print(f"智能体回复: {result}\n")


def example_different_models():
    """示例4: 使用不同的模型"""
    print("=== 示例4: 使用不同的模型 ===\n")
    
    # 使用GPT-3.5
    agent_gpt35 = TestAgent(
        "GPT-3.5测试",
        llm={'model': 'gpt-3.5-turbo'}
    )
    
    # 使用GPT-4
    agent_gpt4 = TestAgent(
        "GPT-4测试", 
        llm={'model': 'gpt-4'}
    )
    
    # 使用Claude（如果有API密钥）
    settings = get_settings()
    if settings.anthropic_api_key:
        agent_claude = TestAgent(
            "Claude测试",
            llm={
                'api_key': settings.anthropic_api_key,
                'base_url': settings.anthropic_base_url,
                'model': settings.anthropic_model
            }
        )
        
        result_claude = agent_claude.run("请介绍自然语言处理")
        print(f"Claude回复: {result_claude}\n")
    
    # 测试GPT模型
    result_gpt35 = agent_gpt35.run("请介绍自然语言处理")
    print(f"GPT-3.5回复: {result_gpt35}\n")
    
    result_gpt4 = agent_gpt4.run("请介绍自然语言处理")
    print(f"GPT-4回复: {result_gpt4}\n")


def example_data_analysis_agent():
    """示例5: 数据分析智能体的配置"""
    print("=== 示例5: 数据分析智能体配置 ===\n")
    
    # 使用默认配置的数据分析智能体
    agent_default = DataAnalysisAgent("默认数据分析助手")
    
    # 使用自定义配置的数据分析智能体
    agent_custom = DataAnalysisAgent(
        "自定义数据分析助手",
        llm={
            'model': 'gpt-4',
            'temperature': 0.2,  # 更低的温度，更稳定的输出
            'max_tokens': 2000   # 更多的token，支持更复杂的分析
        },
        output_dir="custom_analysis_outputs"
    )
    
    print("数据分析智能体创建完成")
    print(f"默认智能体输出目录: {agent_default.output_dir}")
    print(f"自定义智能体输出目录: {agent_custom.output_dir}\n")


def example_environment_variables():
    """示例6: 环境变量配置"""
    print("=== 示例6: 环境变量配置 ===\n")
    
    # 显示当前环境变量配置
    settings = get_settings()
    
    print("当前环境变量配置:")
    print(f"OPENAI_API_KEY: {'已设置' if settings.openai_api_key else '未设置'}")
    print(f"ANTHROPIC_API_KEY: {'已设置' if settings.anthropic_api_key else '未设置'}")
    print(f"OPENAI_BASE_URL: {settings.openai_base_url}")
    print(f"ANTHROPIC_BASE_URL: {settings.anthropic_base_url}")
    print(f"DEFAULT_LLM_MODEL: {settings.default_llm_model}")
    print(f"DEFAULT_LLM_TEMPERATURE: {settings.default_llm_temperature}")
    print(f"DEFAULT_LLM_MAX_TOKENS: {settings.default_llm_max_tokens}")
    print(f"LLM_MAX_RETRIES_PRIMARY: {settings.llm_max_retries_primary}")
    print(f"LLM_MAX_RETRIES_FALLBACK: {settings.llm_max_retries_fallback}")
    print(f"LLM_RETRY_DELAY_SECONDS: {settings.llm_retry_delay_seconds}")
    print(f"LLM_CONTENT_FILTER_ERROR_CODE: {settings.llm_content_filter_error_code}")
    print(f"LLM_CONTENT_FILTER_ERROR_FIELD: {settings.llm_content_filter_error_field}\n")


def main():
    """主函数"""
    print("🤖 LLM配置使用示例\n")
    
    # 检查环境变量
    settings = get_settings()
    if not settings.openai_api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        print("示例: export OPENAI_API_KEY=your-api-key")
        return
    
    try:
        # 示例1: 默认配置
        example_default_config()
        
        # 示例2: 自定义参数
        example_custom_llm_params()
        
        # 示例3: 自定义配置（需要API密钥）
        # example_custom_llm_config()
        
        # 示例4: 不同模型
        example_different_models()
        
        # 示例5: 数据分析智能体
        example_data_analysis_agent()
        
        # 示例6: 环境变量
        example_environment_variables()
        
        print("✅ 所有示例运行完成!")
        
    except Exception as e:
        print(f"❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 