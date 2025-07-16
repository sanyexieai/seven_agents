import anyio
import click
from tools.mcp import mcp

# 只需import所有工具模块，确保装饰器注册生效
import tools.mcp.google_news_search
import tools.mcp.file_operation
import tools.mcp.api_call
import tools.mcp.database_operation

# 不要在本文件再创建mcp实例，确保全局唯一

@click.command()
@click.option("--port", default=8080, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="sse",
    help="Transport type",
)
def main(port: int, transport: str) -> int:
    print("==============================")
    print("MCP服务即将启动！")
    print("==============================")

    if transport == "sse":
        from mcp.server.sse import SseServerTransport
        from starlette.applications import Starlette
        from starlette.responses import Response
        from starlette.routing import Mount, Route
        import uvicorn

        sse = SseServerTransport("/messages/")

        async def handle_sse(request):
            try:
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    await mcp._mcp_server.run(
                        streams[0], streams[1], mcp._mcp_server.create_initialization_options(),
                    )
            except (GeneratorExit, RuntimeError) as e:
                print(f'[SSE] 流关闭异常: {e}')
            return Response()

        starlette_app = Starlette(
            debug=True,
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET", "POST"]),
                Mount("/messages/", app=sse.handle_post_message),
            ],
        )

        uvicorn.run(starlette_app, host="0.0.0.0", port=port)
    else:
        # STDIO模式直接用FastMCP同步run方法
        mcp.run("stdio")

    return 0

if __name__ == "__main__":
    main() 