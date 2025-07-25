# -*- coding: utf-8 -*-
"""
LLM调用辅助模块 - LangChain集成版本
"""

import asyncio
import yaml
import os
import datetime
from typing import Any, List, Optional, Dict
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from config.llm_config import LLMConfig
from .fallback_openai_client import AsyncFallbackOpenAIClient


class LLMHelper(LLM):
    """LLM调用辅助类，继承LangChain LLM，支持同步和异步调用"""
    
    config: LLMConfig
    client: AsyncFallbackOpenAIClient
    llm_log_path: str
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, config: LLMConfig = None):
        # 先创建客户端和日志路径
        client = AsyncFallbackOpenAIClient(
            primary_api_key=config.api_key,
            primary_base_url=config.base_url,
            primary_model_name=config.model,
            fallback_api_key=config.fallback_api_key,
            fallback_base_url=config.fallback_base_url,
            fallback_model_name=config.fallback_model,
            max_retries_primary=config.max_retries_primary,
            max_retries_fallback=config.max_retries_fallback,
            retry_delay_seconds=config.retry_delay_seconds,
            content_filter_error_code=config.content_filter_error_code,
            content_filter_error_field=config.content_filter_error_field
        )
        llm_log_path = os.path.join(os.getcwd(), 'llm_calls.log')
        
        # 调用父类初始化，传入所有必需字段
        super().__init__(
            config=config,
            client=client,
            llm_log_path=llm_log_path
        )
    
    @property
    def _llm_type(self) -> str:
        """返回LLM类型"""
        return "llm_helper"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """LangChain LLM的核心调用方法"""
        return self.call(prompt, **kwargs)
    
    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """LangChain LLM的异步调用方法"""
        return await self.async_call(prompt, **kwargs)
    
    def log_llm_call(self, prompt, system_prompt, response):
        try:
            print(f"LLM日志写入路径: {self.llm_log_path}")
            with open(self.llm_log_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*40}\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
                if system_prompt:
                    f.write(f"[System Prompt]:\n{system_prompt}\n")
                f.write(f"[User Prompt]:\n{prompt}\n")
                f.write(f"[LLM Response]:\n{response}\n")
        except Exception as e:
            print(f"写入llm_calls.log失败: {e}")

    async def async_call(self, prompt: str, system_prompt: str = None, max_tokens: int = None, temperature: float = None) -> str:
        """异步调用LLM"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {}
        if max_tokens is not None:
            kwargs['max_tokens'] = max_tokens
        else:
            kwargs['max_tokens'] = self.config.max_tokens
            
        if temperature is not None:
            kwargs['temperature'] = temperature
        else:
            kwargs['temperature'] = self.config.temperature
            
        try:
            response = await self.client.chat_completions_create(
                messages=messages,
                **kwargs
            )
            result = response.choices[0].message.content
            self.log_llm_call(prompt, system_prompt, result)
            return result
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return ""
    def call(self, prompt: str, system_prompt: str = None, max_tokens: int = None, temperature: float = None) -> str:
        """同步调用LLM"""
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果事件循环正在运行（如在Jupyter中），使用nest_asyncio
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    result = asyncio.run(self.async_call(prompt, system_prompt, max_tokens, temperature))
                except ImportError:
                    # 如果没有nest_asyncio，使用create_task
                    task = asyncio.create_task(self.async_call(prompt, system_prompt, max_tokens, temperature))
                    # 等待任务完成
                    import concurrent.futures
                    import threading
                    
                    result = None
                    exception = None
                    
                    def run_task():
                        nonlocal result, exception
                        try:
                            new_loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(new_loop)
                            result = new_loop.run_until_complete(self.async_call(prompt, system_prompt, max_tokens, temperature))
                            new_loop.close()
                        except Exception as e:
                            exception = e
                    
                    thread = threading.Thread(target=run_task)
                    thread.start()
                    thread.join()
                    
                    if exception:
                        raise exception
            else:
                # 如果事件循环未运行，直接使用asyncio.run
                result = asyncio.run(self.async_call(prompt, system_prompt, max_tokens, temperature))
            self.log_llm_call(prompt, system_prompt, result)
            return result
        except RuntimeError:
            # 如果没有事件循环，创建新的
            result = asyncio.run(self.async_call(prompt, system_prompt, max_tokens, temperature))
            self.log_llm_call(prompt, system_prompt, result)
            return result
    
    def parse_yaml_response(self, response: str) -> dict:
        """解析YAML格式的响应"""
        try:
            # 提取```yaml和```之间的内容
            if '```yaml' in response:
                start = response.find('```yaml') + 7
                end = response.find('```', start)
                yaml_content = response[start:end].strip()
            elif '```' in response:
                start = response.find('```') + 3
                end = response.find('```', start)
                yaml_content = response[start:end].strip()
            else:
                yaml_content = response.strip()
            
            return yaml.safe_load(yaml_content)
        except Exception as e:
            print(f"YAML解析失败: {e}")
            print(f"原始响应: {response}")
            return {}
    
    def parse_code_block_response(self, response: str) -> dict:
        """
        兼容 LLM 输出的 ```json、```yaml、``` 代码块，优先用json解析，失败再用yaml
        """
        import re
        import json
        content = response.strip()
        # 提取代码块内容
        match = re.search(r"```(?:json|yaml)?\s*([\s\S]*?)```", content)
        if match:
            content = match.group(1).strip()
        # 先尝试json解析
        try:
            return json.loads(content)
        except Exception:
            pass
        # 再尝试yaml解析
        try:
            import yaml
            return yaml.safe_load(content)
        except Exception as e:
            print(f"代码块解析失败: {e}")
            print(f"原始响应: {response}")
            return {}
    
    async def close(self):
        """关闭客户端"""
        await self.client.close()