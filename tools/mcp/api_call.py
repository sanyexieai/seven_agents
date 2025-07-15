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

@mcp.tool()
async def get(url: str, headers: dict = None):
    headers = headers or {}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def post(url: str, headers: dict = None, data: dict = None):
    headers = headers or {}
    data = data or {}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def put(url: str, headers: dict = None, data: dict = None):
    headers = headers or {}
    data = data or {}
    try:
        resp = requests.put(url, headers=headers, json=data, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def delete(url: str, headers: dict = None):
    headers = headers or {}
    try:
        resp = requests.delete(url, headers=headers, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def patch(url: str, headers: dict = None, data: dict = None):
    headers = headers or {}
    data = data or {}
    try:
        resp = requests.patch(url, headers=headers, json=data, timeout=30)
        return _format_response(resp)
    except Exception as e:
        return {"success": False, "error": str(e)} 