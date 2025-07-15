import os
import importlib
import pkgutil
from mcp.server.fastmcp import FastMCP
from tools.mcp.base import MCPTool

MCP = FastMCP("AllToolsDemo")
registered_tools = []

# 自动遍历 tools/mcp 目录，查找所有 MCPTool 子类
mcp_dir = os.path.join(os.path.dirname(__file__), "tools", "mcp")
for finder, name, ispkg in pkgutil.iter_modules([mcp_dir]):
    if name in ("base", "__init__"):  # 跳过基类和init
        continue
    module_path = f"tools.mcp.{name}"
    module = importlib.import_module(module_path)
    # 查找所有MCPTool子类
    for attr in dir(module):
        obj = getattr(module, attr)
        if isinstance(obj, type) and issubclass(obj, MCPTool) and obj is not MCPTool:
            tool_instance = obj()
            if hasattr(tool_instance, "get_methods"):
                for method_name, method_schema in tool_instance.get_methods().items():
                    # 注册handler而不是getattr
                    def make_handler(tool, mname):
                        def handler(**kwargs):
                            return tool.execute(mname, **kwargs)
                        return handler
                    MCP.tool(name=f"{obj.__name__}.{method_name}")(make_handler(tool_instance, method_name))
                    registered_tools.append(f"{obj.__name__}.{method_name}")

if __name__ == "__main__":
    print("==============================")
    print("MCP服务即将启动！")
    print("服务名称: AllToolsDemo")
    print("监听端口: 8080 (默认)")
    print("自动注册的工具方法:")
    for t in registered_tools:
        print(f"  - {t}")
    print("==============================")
    MCP.run() 