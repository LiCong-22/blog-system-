"""
MCP Server - 博客发布服务
通过 MCP 协议提供博客管理工具
"""

import asyncio
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


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
