# -*- coding: utf-8 -*-
"""
API调用工具
"""

import requests
from typing import Dict, Any
from .base import MCPTool


class APICallTool(MCPTool):
    """API调用工具"""
    
    def __init__(self):
        super().__init__(
            name="api_call",
            description="调用外部API"
        )
    
    def execute(self, method: str, url: str, headers: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """执行API调用"""
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers or {},
                json=data,
                timeout=30
            )
            return {
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "description": "HTTP方法"
                },
                "url": {
                    "type": "string",
                    "description": "API URL"
                },
                "headers": {
                    "type": "object",
                    "description": "请求头"
                },
                "data": {
                    "type": "object",
                    "description": "请求数据"
                }
            },
            "required": ["method", "url"]
        } 