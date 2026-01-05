"""
MCP Server - 博客发布服务
支持 stdio 模式（本地）和 HTTP 模式（远程）
"""

import asyncio
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from blog_tool import create_blog_post, list_blog_posts


server = Server("blog-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="create_blog_post",
            description="创建一篇新的博客文章，自动保存为 Markdown 并提交到 GitHub，触发 Vercel 部署。",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "文章标题"},
                    "content": {"type": "string", "description": "文章正文 (Markdown)"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "标签列表"},
                    "description": {"type": "string", "description": "简短描述"}
                },
                "required": ["title", "content"]
            }
        ),
        Tool(
            name="list_blog_posts",
            description="列出所有博客文章",
            inputSchema={"type": "object", "properties": {}}
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "create_blog_post":
            result = create_blog_post(
                title=arguments["title"],
                content=arguments["content"],
                tags=arguments.get("tags", []),
                description=arguments.get("description", "")
            )
            response = f"""博客已创建！

**标题**: {arguments['title']}
**文件**: {result['filename']}

GitHub: {result['url']}

已推送到 GitHub，Vercel 将自动部署。"""
            return [TextContent(type="text", text=response)]

        elif name == "list_blog_posts":
            result = list_blog_posts()
            if result["count"] == 0:
                return [TextContent(type="text", text="暂无文章")]
            posts_list = "\n".join([f"- **{p['title']}**" for p in result["posts"]])
            return [TextContent(type="text", text=f"已有 {result['count']} 篇文章：\n\n{posts_list}")]

        return [TextContent(type="text", text=f"未知工具: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"错误: {str(e)}")]


async def run_stdio():
    """stdio 模式 - 用于本地调用"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


async def handle_http_request(request):
    """处理 HTTP 请求 - MCP JSON-RPC over HTTP"""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        msg_id = body.get("id")

        # 初始化响应
        response = {
            "jsonrpc": "2.0",
            "id": msg_id
        }

        if method == "initialize":
            response["result"] = {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "serverInfo": {"name": "blog-mcp-server", "version": "1.0.0"}
            }

        elif method == "notifications/initialized":
            response = None

        elif method == "tools/list":
            tools = await list_tools()
            response["result"] = {"tools": [
                {
                    "name": t.name,
                    "description": t.description,
                    "inputSchema": t.inputSchema
                }
                for t in tools
            ]}

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            result = await call_tool(tool_name, tool_args)
            response["result"] = {"content": [
                {"type": "text", "text": r.text}
                for r in result
            ]}

        else:
            response["error"] = {"code": -32601, "message": f"Unknown method: {method}"}

        if response:
            return response

    except Exception as e:
        return {"jsonrpc": "2.0", "id": msg_id or None, "error": {"code": -32603, "message": str(e)}}

    return None


async def run_http(host: str, port: int):
    """HTTP 模式 - 使用 aiohttp 实现 MCP HTTP 传输"""
    try:
        import aiohttp
    except ImportError:
        print("错误: 需要安装 aiohttp")
        print("运行: pip install aiohttp")
        return

    from aiohttp import web

    app = web.Application()

    # SSE endpoint for Claude Desktop
    async def sse_handler(request):
        """SSE 端点 - 用于 MCP 实时通信"""
        response = web.StreamResponse(
            status=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
            }
        )

        async def send_event(data, event=None):
            await response.prepare(request)
            message = f"event: {event}\n" if event else ""
            message += f"data: {json.dumps(data)}\n\n"
            await response.write(message.encode())

        # 发送初始化
        await send_event({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {
                "capabilities": {}
            }
        })

        # 保持连接，处理消息
        try:
            while True:
                # 简单的轮询，实际应该用消息队列
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

        return response

    # POST endpoint for tool calls
    async def message_handler(request):
        """消息端点 - 处理 JSON-RPC 请求"""
        try:
            result = await handle_http_request(request)
            if result:
                return web.json_response(result)
            return web.Response(status=204)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    # GET endpoint for health check / capabilities
    async def info_handler(request):
        """信息端点"""
        return web.json_response({
            "name": "blog-mcp-server",
            "version": "1.0.0",
            "endpoints": {
                "sse": "/sse",
                "message": "/message"
            }
        })

    app.router.add_get("/sse", sse_handler)
    app.router.add_post("/message", message_handler)
    app.router.add_get("/", info_handler)

    print(f"MCP HTTP 服务器启动: http://{host}:{port}")
    print(f"  - SSE: http://{host}:{port}/sse")
    print(f"  - 消息: http://{host}:{port}/message")
    print("\n使用 cloudflared 暴露到公网:")
    print(f"  cloudflared tunnel --url http://{host}:{port}")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        await runner.cleanup()


async def main():
    parser = argparse.ArgumentParser(description="Blog MCP Server")
    parser.add_argument(
        "--mode",
        choices=["stdio", "http"],
        default="stdio",
        help="运行模式: stdio (默认, 本地), http (远程)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP 模式下的监听地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="HTTP 模式下的监听端口 (默认: 8080)"
    )

    args = parser.parse_args()

    if args.mode == "http":
        await run_http(args.host, args.port)
    else:
        await run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
