# -*- coding: utf-8 -*-
"""
文件操作工具
"""

from typing import Dict, Any
from .base import MCPTool
import os


class FileOperationTool(MCPTool):
    """文件操作多方法MCP工具"""
    def __init__(self):
        super().__init__(
            name="file_operation",
            description="执行文件读写追加等多方法操作"
        )
        self._methods = {
            "read_file": {
                "description": "读取文件内容",
                "parameters": {
                    "file_path": {"type": "string", "description": "文件路径"}
                }
            },
            "write_file": {
                "description": "写入文件内容（覆盖）",
                "parameters": {
                    "file_path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "要写入的内容"}
                }
            },
            "append_file": {
                "description": "追加内容到文件末尾",
                "parameters": {
                    "file_path": {"type": "string", "description": "文件路径"},
                    "content": {"type": "string", "description": "要追加的内容"}
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
            if method == "read_file":
                return self.read_file(kwargs)
            elif method == "write_file":
                return self.write_file(kwargs)
            elif method == "append_file":
                return self.append_file(kwargs)
            else:
                return f"未知方法: {method}"
        except Exception as e:
            return f"文件操作失败: {e}"

    def read_file(self, kwargs):
        file_path = kwargs.get("file_path")
        if not file_path:
            return {"success": False, "error": "缺少file_path参数"}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"success": True, "content": content}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, kwargs):
        file_path = kwargs.get("file_path")
        content = kwargs.get("content", "")
        if not file_path:
            return {"success": False, "error": "缺少file_path参数"}
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "message": f"文件 {file_path} 写入成功"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def append_file(self, kwargs):
        file_path = kwargs.get("file_path")
        content = kwargs.get("content", "")
        if not file_path:
            return {"success": False, "error": "缺少file_path参数"}
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "message": f"文件 {file_path} 追加成功"}
        except Exception as e:
            return {"success": False, "error": str(e)} 