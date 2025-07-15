# -*- coding: utf-8 -*-
"""
API调用工具
"""

from tools.mcp import mcp
import requests

def _format_response(resp):
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

@mcp.tool(description="发起GET请求，返回响应内容")
async def api_get(url: str, headers: dict = None):
    headers = headers or {}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool(description="发起POST请求，支持JSON数据体")
async def api_post(url: str, headers: dict = None, data: dict = None):
    headers = headers or {}
    data = data or {}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool(description="发起PUT请求，支持JSON数据体")
async def api_put(url: str, headers: dict = None, data: dict = None):
    headers = headers or {}
    data = data or {}
    try:
        resp = requests.put(url, headers=headers, json=data, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool(description="发起DELETE请求")
async def api_delete(url: str, headers: dict = None):
    headers = headers or {}
    try:
        resp = requests.delete(url, headers=headers, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool(description="发起PATCH请求，支持JSON数据体")
async def api_patch(url: str, headers: dict = None, data: dict = None):
    headers = headers or {}
    data = data or {}
    try:
        resp = requests.patch(url, headers=headers, json=data, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)} 