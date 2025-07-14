# -*- coding: utf-8 -*-
"""
LLM配置模块
"""

import os
from dataclasses import dataclass
from typing import Optional
from .settings import get_settings


@dataclass
class LLMConfig:
    """LLM配置类"""
    
    # 主API配置
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # 备用API配置（可选）
    fallback_api_key: Optional[str] = None
    fallback_base_url: Optional[str] = None
    fallback_model: Optional[str] = None
    
    # 重试配置
    max_retries_primary: int = 1
    max_retries_fallback: int = 1
    retry_delay_seconds: float = 1.0
    
    # 内容过滤配置
    content_filter_error_code: str = "1301"
    content_filter_error_field: str = "contentFilter"
    
    @classmethod
    def from_settings(cls) -> 'LLMConfig':
        """从应用设置创建LLM配置"""
        settings = get_settings()
        
        return cls(
            api_key=settings.openai_api_key or "",
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            model=settings.default_llm_model,
            max_tokens=settings.default_llm_max_tokens,
            temperature=settings.default_llm_temperature,
            # 备用API配置
            fallback_api_key=settings.anthropic_api_key,
            fallback_base_url=os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com/v1'),
            fallback_model=os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
            # 重试配置
            max_retries_primary=int(os.getenv('LLM_MAX_RETRIES_PRIMARY', '1')),
            max_retries_fallback=int(os.getenv('LLM_MAX_RETRIES_FALLBACK', '1')),
            retry_delay_seconds=float(os.getenv('LLM_RETRY_DELAY_SECONDS', '1.0')),
            # 内容过滤配置
            content_filter_error_code=os.getenv('LLM_CONTENT_FILTER_ERROR_CODE', '1301'),
            content_filter_error_field=os.getenv('LLM_CONTENT_FILTER_ERROR_FIELD', 'contentFilter')
        )
    
    @classmethod
    def create_openai_config(cls, api_key: str, model: str = "gpt-3.5-turbo") -> 'LLMConfig':
        """创建OpenAI配置"""
        return cls(
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            model=model
        )
    
    @classmethod
    def create_anthropic_config(cls, api_key: str, model: str = "claude-3-sonnet-20240229") -> 'LLMConfig':
        """创建Anthropic配置"""
        return cls(
            api_key=api_key,
            base_url="https://api.anthropic.com/v1",
            model=model
        ) 