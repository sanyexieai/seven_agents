# -*- coding: utf-8 -*-
"""
API调用工具
"""

import requests
from typing import Dict, Any
from .base import MCPTool

class APICallTool(MCPTool):
    """API调用多方法MCP工具"""
    def __init__(self):
        super().__init__(
            name="api_call",
            description="调用外部API，支持GET/POST/PUT/DELETE/PATCH多方法"
        )
        self._methods = {
            "get": {
                "description": "GET请求",
                "parameters": {
                    "url": {"type": "string", "description": "API URL"},
                    "headers": {"type": "object", "description": "请求头", "required": False}
                }
            },
            "post": {
                "description": "POST请求",
                "parameters": {
                    "url": {"type": "string", "description": "API URL"},
                    "headers": {"type": "object", "description": "请求头", "required": False},
                    "data": {"type": "object", "description": "请求数据", "required": False}
                }
            },
            "put": {
                "description": "PUT请求",
                "parameters": {
                    "url": {"type": "string", "description": "API URL"},
                    "headers": {"type": "object", "description": "请求头", "required": False},
                    "data": {"type": "object", "description": "请求数据", "required": False}
                }
            },
            "delete": {
                "description": "DELETE请求",
                "parameters": {
                    "url": {"type": "string", "description": "API URL"},
                    "headers": {"type": "object", "description": "请求头", "required": False}
                }
            },
            "patch": {
                "description": "PATCH请求",
                "parameters": {
                    "url": {"type": "string", "description": "API URL"},
                    "headers": {"type": "object", "description": "请求头", "required": False},
                    "data": {"type": "object", "description": "请求数据", "required": False}
                }
            }
        }

    def get_methods(self) -> Dict[str, Any]:
        return self._methods

    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "methods": self.get_methods()
        }

    def get_parameters(self) -> Dict[str, Any]:
        return self.get_methods()

    def execute(self, method: str, **kwargs):
        if not method or method not in self._methods:
            return f"不支持的方法: {method}"
        try:
            if method == "get":
                return self.get_request(kwargs)
            elif method == "post":
                return self.post_request(kwargs)
            elif method == "put":
                return self.put_request(kwargs)
            elif method == "delete":
                return self.delete_request(kwargs)
            elif method == "patch":
                return self.patch_request(kwargs)
            else:
                return f"未知方法: {method}"
        except Exception as e:
            return f"API调用失败: {e}"

    def get_request(self, kwargs):
        url = kwargs.get("url")
        headers = kwargs.get("headers", {})
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            return self._format_response(resp)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def post_request(self, kwargs):
        url = kwargs.get("url")
        headers = kwargs.get("headers", {})
        data = kwargs.get("data", {})
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            return self._format_response(resp)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def put_request(self, kwargs):
        url = kwargs.get("url")
        headers = kwargs.get("headers", {})
        data = kwargs.get("data", {})
        try:
            resp = requests.put(url, headers=headers, json=data, timeout=30)
            return self._format_response(resp)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_request(self, kwargs):
        url = kwargs.get("url")
        headers = kwargs.get("headers", {})
        try:
            resp = requests.delete(url, headers=headers, timeout=30)
            return self._format_response(resp)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def patch_request(self, kwargs):
        url = kwargs.get("url")
        headers = kwargs.get("headers", {})
        data = kwargs.get("data", {})
        try:
            resp = requests.patch(url, headers=headers, json=data, timeout=30)
            return self._format_response(resp)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _format_response(self, resp):
        try:
            data = resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
        except Exception:
            data = resp.text
        return {
            "success": resp.ok,
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "data": data
        } 