# -*- coding: utf-8 -*-
"""
文件操作工具
"""

from typing import Dict, Any
from tools.mcp import mcp
import os

@mcp.tool()
async def read_file(file_path: str):
    if not file_path:
        return {"success": False, "error": "缺少file_path参数"}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def write_file(file_path: str, content: str):
    if not file_path:
        return {"success": False, "error": "缺少file_path参数"}
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"文件 {file_path} 写入成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def append_file(file_path: str, content: str):
    if not file_path:
        return {"success": False, "error": "缺少file_path参数"}
    try:
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "message": f"文件 {file_path} 追加成功"}
    except Exception as e:
        return {"success": False, "error": str(e)} 