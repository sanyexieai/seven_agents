# -*- coding: utf-8 -*-
"""
文件操作工具
"""

from typing import Dict, Any
from .base import MCPTool


class FileOperationTool(MCPTool):
    """文件操作工具"""
    
    def __init__(self):
        super().__init__(
            name="file_operation",
            description="执行文件读写操作"
        )
    
    def execute(self, operation: str, file_path: str, content: str = None) -> Dict[str, Any]:
        """执行文件操作"""
        try:
            if operation == "read":
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"success": True, "content": content}
            
            elif operation == "write":
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content or "")
                return {"success": True, "message": f"文件 {file_path} 写入成功"}
            
            elif operation == "append":
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(content or "")
                return {"success": True, "message": f"文件 {file_path} 追加成功"}
            
            else:
                return {"success": False, "error": f"不支持的操作: {operation}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "append"],
                    "description": "文件操作类型"
                },
                "file_path": {
                    "type": "string",
                    "description": "文件路径"
                },
                "content": {
                    "type": "string",
                    "description": "文件内容（写操作时使用）"
                }
            },
            "required": ["operation", "file_path"]
        } 