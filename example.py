import argparse
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.requests import Request
from starlette.routing import Mount, Route
from mcp.server import Server
import uvicorn
 
# 初始化 FastMCP 实例
mcp = FastMCP("api-mcp-calc")
 
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

 
# 创建 Starlette 应用
def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    sse = SseServerTransport("/messages/")
    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )
 
    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )
 
# 主程序入口
if __name__ == "__main__":

    # 创建并运行 Starlette 应用
    starlette_app = create_starlette_app( mcp._mcp_server, debug=True)
    uvicorn.run(starlette_app, host='0.0.0.0', port=18080)