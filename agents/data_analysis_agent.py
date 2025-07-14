# -*- coding: utf-8 -*-
"""
数据分析智能体
"""

import os
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent
from .utils.code_executor import CodeExecutor
from .utils.extract_code import extract_code_from_response
from .utils.format_execution_result import format_execution_result


class DataAnalysisAgent(BaseAgent):
    """数据分析智能体，支持代码执行和数据分析"""
    
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        
        # 初始化代码执行器
        self.output_dir = kwargs.get('output_dir', 'data_analysis_outputs')
        self.code_executor = CodeExecutor(output_dir=self.output_dir)
        
        # 设置提示词模板
        self.prompt_template = """你是一个专业的数据分析助手。请根据用户的需求进行数据分析。

用户需求: {user_input}

请提供以下内容：
1. 分析思路
2. 所需的Python代码（使用pandas、numpy、matplotlib等库）
3. 代码执行结果的解释

请用YAML格式回复：
```yaml
analysis_plan: "分析思路描述"
code: |
  # 你的Python代码
  import pandas as pd
  import numpy as np
  import matplotlib.pyplot as plt
  # ... 其他代码
explanation: "代码执行结果的解释"
```

如果用户提供了数据文件路径，请先读取数据，然后进行分析。"""

    def analyze_data(self, user_input: str, data_file_path: str = None) -> Dict[str, Any]:
        """
        执行数据分析
        
        Args:
            user_input: 用户分析需求
            data_file_path: 数据文件路径（可选）
            
        Returns:
            分析结果字典
        """
        try:
            # 创建会话目录
            session_dir = os.path.join(self.output_dir, user_input)
            os.makedirs(session_dir, exist_ok=True)
            self.logger.info(f"创建会话目录: {session_dir}")
            
            # 如果有数据文件，先设置到执行环境
            if data_file_path and os.path.exists(data_file_path):
                self.code_executor.set_variable('data_file_path', data_file_path)
                self.logger.info(f"设置数据文件路径: {data_file_path}")
            
            # 构建完整提示词
            full_prompt = self.prompt_template.format(user_input=user_input)
            
            # 调用LLM获取分析代码
            response = self.llm.call(full_prompt)
            self.logger.info("获取到LLM分析响应")
            
            # 提取代码
            code = extract_code_from_response(response)
            if not code:
                return {
                    'success': False,
                    'error': '无法从响应中提取代码',
                    'response': response
                }
            
            # 执行代码
            self.logger.info("开始执行分析代码")
            result = self.code_executor.execute_code(code)
            
            # 格式化结果
            formatted_result = format_execution_result(result)
            
            # 保存结果到会话目录
            result_file = os.path.join(session_dir, 'analysis_result.json')
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'user_input': user_input,
                    'code': code,
                    'execution_result': result,
                    'formatted_result': formatted_result,
                    'session_dir': session_dir
                }, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'session_dir': session_dir,
                'code': code,
                'execution_result': result,
                'formatted_result': formatted_result,
                'llm_response': response
            }
            
        except Exception as e:
            self.logger.error(f"数据分析失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """获取分析历史"""
        history = []
        if os.path.exists(self.output_dir):
            for session_dir in os.listdir(self.output_dir):
                if session_dir.startswith('session_'):
                    result_file = os.path.join(self.output_dir, session_dir, 'analysis_result.json')
                    if os.path.exists(result_file):
                        try:
                            with open(result_file, 'r', encoding='utf-8') as f:
                                history.append(json.load(f))
                        except Exception as e:
                            self.logger.error(f"读取历史记录失败: {e}")
        return history
    
    def reset_environment(self):
        """重置代码执行环境"""
        self.code_executor.reset_environment()
        self.logger.info("代码执行环境已重置")
    
    def set_data_file(self, file_path: str):
        """设置数据文件路径"""
        if os.path.exists(file_path):
            self.code_executor.set_variable('data_file_path', file_path)
            self.logger.info(f"设置数据文件: {file_path}")
        else:
            self.logger.error(f"数据文件不存在: {file_path}")
    
    def get_environment_info(self) -> str:
        """获取执行环境信息"""
        return self.code_executor.get_environment_info()
    
    def _get_agent_description(self) -> str:
        return "数据分析与可视化专家，擅长多源数据融合分析。" 