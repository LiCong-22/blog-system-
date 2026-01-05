---
title: "从零搭建 AI 智能博客系统：MCP 自动化发布实战"
description: "详细记录如何用 Astro + Vercel 搭建博客，并实现 AI 自动发布功能"
pubDate: 2026-01-05
updatedDate: 2026-01-05
tags: ["博客", "Astro", "MCP", "AI", "Vercel"]
---

# 从零搭建 AI 智能博客系统

本文详细记录了如何从零搭建一个支持 AI 自动发布的博客系统。

## 1. 技术选型

### 为什么选择这个方案？

| 技术 | 选择理由 |
|------|----------|
| **Astro** | 静态站点生成器，性能好，学习成本低 |
| **Vercel** | 免费托管，自动部署，CDN 加速 |
| **MCP** | AI 协议标准，支持工具调用 |
| **GitHub** | 代码托管，版本控制 |

### 架构图

```
用户 (Claude Desktop/Code)
       │
       │ 对话
       ▼
┌──────────────────┐
│  AI 模型         │ ← 生成对话总结
└────────┬─────────┘
         │
         │ MCP 工具调用
         ▼
┌──────────────────┐
│  MCP Server      │ ← 接收请求，创建文件
└────────┬─────────┘
         │
         │ git push
         ▼
┌──────────────────┐
│  GitHub          │ ← 代码托管
└────────┬─────────┘
         │
         │ 自动部署
         ▼
┌──────────────────┐
│  Vercel          │ ← 静态托管，发布网站
└──────────────────┘
```

## 2. 初始化项目

### 2.1 创建 Astro 项目

```bash
# 创建 Astro 项目
npm create astro@latest blog-system

# 选择模板
- Use a blog template? Yes
- Install dependencies? Yes
- Initialize git? Yes
```

### 2.2 项目结构

```
blog-system/
├── src/
│   ├── content/posts/    # 博客文章 (Markdown)
│   ├── layouts/          # 页面布局
│   ├── pages/            # 页面
│   └── components/       # 组件
├── public/               # 静态资源
├── astro.config.mjs      # Astro 配置
└── package.json
```

## 3. 功能增强

### 3.1 文章 Frontmatter 定义

```typescript
// src/content/config.ts
import { defineCollection, z } from 'astro:content';

const posts = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    password: z.string().optional(), // 加密文章
  }),
});

export const collections = { posts };
```

### 3.2 密码保护功能

在文章 frontmatter 添加 `password` 字段即可加密：

```markdown
---
title: "私有文章"
description: "描述"
pubDate: 2026-01-05
tags: ["私有"]
password: "lc8814"
---
```

### 3.3 搜索功能

```javascript
// 首页搜索实现
const searchPosts = posts.filter(post => {
  const searchStr = (post.data.title + post.data.tags.join(' ')).toLowerCase();
  return searchStr.includes(keyword.toLowerCase());
});
```

### 3.4 TOC 目录

```astro
<nav class="toc">
  {headings.map(heading => (
    <a href={`#${heading.slug}`}>{heading.text}</a>
  ))}
</nav>
```

### 3.5 RSS 订阅

```javascript
// src/pages/rss.xml.js
export async function GET(context) {
  const posts = await getCollection('posts');
  return new Response(rssXml(posts), {
    headers: { 'Content-Type': 'application/xml' }
  });
}
```

## 4. 部署到 Vercel

### 4.1 推送代码到 GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/blog-system-.git
git push -u origin main
```

### 4.2 Vercel 部署

1. 登录 https://vercel.com
2. Import GitHub 仓库
3. Framework Preset 选择 Astro
4. Deploy

**访问地址：** https://blog-system-six-sepia.vercel.app

## 5. MCP Server 实现

### 5.1 什么是 MCP？

**MCP (Model Context Protocol)** 是 Anthropic 推出的 AI 工具调用协议标准。

#### MCP 的核心概念

```
┌─────────────────────────────────────────────────────────┐
│                    MCP 协议层次                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  应用层 (你的应用)                                       │
│      │                                                  │
│      ▼                                                  │
│  MCP Server (我们写的)                                   │
│      │                                                  │
│      ▼                                                  │
│  MCP Client (Claude Desktop/Code)                       │
│      │                                                  │
│      ▼                                                  │
│  AI Model (Claude)                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### MCP vs 传统 API

| 特性 | 传统 API | MCP |
|------|----------|-----|
| 调用方式 | HTTP 请求 | 协议标准化 |
| 工具发现 | 文档查询 | 自动发现 |
| 参数格式 | 各家不同 | JSON Schema |
| 状态管理 | 无 | Session 支持 |

### 5.2 MCP 核心组件

#### 1. Server

MCP 服务器实例，所有工具的容器：

```python
from mcp.server import Server

server = Server("blog-mcp-server")
```

#### 2. Tool

工具定义，包含名称、描述和参数模式：

```python
from mcp.types import Tool

Tool(
    name="create_blog_post",
    description="创建博客文章，自动保存并推送到 GitHub",
    inputSchema={
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "文章标题"},
            "content": {"type": "string", "description": "文章内容"},
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "标签列表"
            }
        },
        "required": ["title", "content"]
    }
)
```

#### 3. list_tools 装饰器

AI 查询可用工具时调用：

```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [tool1, tool2, tool3]
```

#### 4. call_tool 装饰器

AI 调用工具时触发：

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "create_blog_post":
        result = do_something(arguments)
        return [TextContent(type="text", text=result)]
```

### 5.3 JSON-RPC 2.0 协议

MCP 基于 **JSON-RPC 2.0** 协议通信：

#### 请求格式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_blog_post",
    "arguments": {
      "title": "文章标题",
      "content": "文章内容..."
    }
  }
}
```

#### 响应格式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "博客已创建！..."
      }
    ]
  }
}
```

#### 错误格式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error"
  }
}
```

### 5.4 安装依赖

```bash
cd mcp-server
pip install mcp>=1.0.0 PyGithub python-dotenv aiohttp
```

### 5.5 完整 Server 实现

```python
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

from blog_tool import create_blog_post, list_blog_posts, upload_image

server = Server("blog-mcp-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """返回所有可用工具"""
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
        ),
        Tool(
            name="upload_image",
            description="上传图片到博客，保存到 posts/images 目录",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名"},
                    "content": {"type": "string", "description": "Base64 编码的图片内容"}
                },
                "required": ["filename", "content"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """处理工具调用"""
    try:
        if name == "create_blog_post":
            result = create_blog_post(
                title=arguments["title"],
                content=arguments["content"],
                tags=arguments.get("tags", []),
                description=arguments.get("description", "")
            )
            response = f"博客已创建！\n\n文件: {result['filename']}"
            return [TextContent(type="text", text=response)]

        elif name == "list_blog_posts":
            result = list_blog_posts()
            posts_list = "\n".join([f"- {p['title']}" for p in result["posts"]])
            return [TextContent(type="text", text=f"已有 {result['count']} 篇文章：\n\n{posts_list}")]

        elif name == "upload_image":
            result = upload_image(
                filename=arguments["filename"],
                base64_content=arguments["content"]
            )
            return [TextContent(type="text", text=f"图片已上传：{result['path']}")]

    except Exception as e:
        return [TextContent(type="text", text=f"错误: {str(e)}")]

async def run_stdio():
    """stdio 模式 - 用于本地调用"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

async def run_http(host: str, port: int):
    """HTTP 模式 - 用于远程调用"""
    from aiohttp import web

    app = web.Application()

    async def sse_handler(request):
        """SSE 端点"""
        response = web.StreamResponse(
            status=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
            }
        )
        await response.prepare(request)
        await response.write(b"data: {\"type\": \"message\"}\n\n")
        return response

    async def message_handler(request):
        """消息端点"""
        body = await request.json()
        # 处理 JSON-RPC 请求...
        return web.json_response({"jsonrpc": "2.0", "result": {}})

    app.router.add_get("/sse", sse_handler)
    app.router.add_post("/message", message_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f"MCP HTTP 服务器: http://{host}:{port}")

    while True:
        await asyncio.sleep(3600)

async def main():
    parser = argparse.ArgumentParser(description="Blog MCP Server")
    parser.add_argument("--mode", choices=["stdio", "http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    if args.mode == "http":
        await run_http(args.host, args.port)
    else:
        await run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
```

### 5.6 业务逻辑实现

```python
"""
博客发布工具 - MCP Server
功能：接收 AI 发送的博客内容，自动创建 Markdown 文件并提交到 GitHub
"""

import os
import subprocess
import base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import json

class BlogPublisher:
    """博客发布器"""

    def __init__(self):
        load_dotenv()
        self.blog_path = os.getenv("BLOG_PATH", "/data/ulixc616/SVW_Dispaly/blog-system")
        self.images_dir = Path(self.blog_path) / "src" / "content" / "posts" / "images"

    def generate_filename(self, title: str) -> str:
        """根据标题生成文件名"""
        import re
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = safe_title.strip().lower().replace(' ', '-')[:50]
        return f"{date_str}-{safe_title}.md"

    def format_markdown(self, title: str, content: str, tags: list = None, description: str = "") -> str:
        """格式化 Markdown 文件内容"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        tags_str = json.dumps(tags or [], ensure_ascii=False)

        return f"""---
title: "{title}"
description: "{description or title}"
pubDate: {date_str}
tags: {tags_str}
---

{content}
"""

    def create_post(self, title: str, content: str, tags: list = None, description: str = "") -> dict:
        """创建博客文章"""
        filename = self.generate_filename(title)
        markdown_content = self.format_markdown(title, content, tags, description)
        posts_dir = Path(self.blog_path) / "src" / "content" / "posts"

        posts_dir.mkdir(parents=True, exist_ok=True)
        filepath = posts_dir / filename
        filepath.write_text(markdown_content, encoding='utf-8')

        # Git 提交
        os.chdir(self.blog_path)
        subprocess.run(["git", "add", str(filepath)], check=True)
        subprocess.run(["git", "commit", "-m", f"Add post: {title}"], check=True)
        subprocess.run(["git", "push"], check=True)

        return {"success": True, "filename": filename, "url": f"https://github.com/..."}

    def upload_image(self, filename: str, base64_content: str) -> dict:
        """上传图片"""
        self.images_dir.mkdir(parents=True, exist_ok=True)
        image_data = base64.b64decode(base64_content)
        filepath = self.images_dir / filename
        filepath.write_bytes(image_data)

        os.chdir(self.blog_path)
        subprocess.run(["git", "add", str(filepath)], check=True)
        subprocess.run(["git", "commit", "-m", f"Add image: {filename}"], check=True)
        subprocess.run(["git", "push"], check=True)

        return {"success": True, "path": f"./images/{filename}"}

BLOG_PUBLISHER = BlogPublisher()

def create_blog_post(title, content, tags=None, description=""):
    return BLOG_PUBLISHER.create_post(title, content, tags, description)

def upload_image(filename, base64_content):
    return BLOG_PUBLISHER.upload_image(filename, base64_content)
```

### 5.7 传输模式

MCP 支持两种传输模式：

#### 1. Stdio 模式（标准输入输出）

用于**本地调用**，Claude Desktop 直接通过 stdin/stdout 与 Server 通信：

```bash
# 启动
python server.py

# 通信方式
# Claude → stdin: JSON-RPC 请求
# Claude ← stdout: JSON-RPC 响应
```

**优点：** 简单直接，无需网络配置

**缺点：** 只能本地使用

#### 2. HTTP + SSE 模式

用于**远程调用**，通过 HTTP 传输：

```
┌─────────────────────────────────────────────────────────┐
│                  HTTP + SSE 模式                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Claude ──POST /message ──► MCP Server                  │
│                                 │                       │
│                                 ▼                       │
│                            处理请求                      │
│                                 │                       │
│                                 ▼                       │
│  Claude ◄── SSE /sse ◄──────── MCP Server               │
│           (长连接推送结果)                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**SSE (Server-Sent Events)：**
- 单向通信：Server → Client
- 基于 HTTP 长连接
- 自动重连机制
- 适合实时推送

**启动命令：**

```bash
python server.py --mode http --port 8080
```

**优点：** 支持远程访问

**缺点：** 需要公网暴露（配合 tunnel 使用）

## 6. 远程访问：Cloudflare Tunnel

### 6.1 问题背景

家庭服务器在内网，外部无法直接访问：

```
┌─────────────┐      ❌ 无法访问       ┌─────────────┐
│ 家庭服务器   │ ◄─────────────────── │  远程设备    │
│ (内网 IP)   │                       │ (外网)       │
└─────────────┘                       └─────────────┘
```

### 6.2 解决方案：内网穿透

内网穿透的核心思想：

```
┌─────────────┐                        ┌─────────────┐
│ 家庭服务器   │ ─── 加密隧道 ─────────►│  Cloudflare │
└─────────────┘                        └──────┬──────┘
                                               │
                                               ▼
                                         ┌─────────────┐
                                         │  公网域名    │
                                         │ trycloudflare│
                                         └──────┬──────┘
                                                │
                                                ▼
┌─────────────┐                        ┌─────────────┐
│ 家庭服务器   │ ◄─────────────────── │  远程设备    │
│ (内网 IP)   │ ◄──── HTTPS ───────── │ (外网)       │
└─────────────┘                        └─────────────┘
```

### 6.3 Cloudflare Tunnel 原理

```
1. cloudflared 进程在家庭服务器运行
2. 与 Cloudflare 建立持久 TLS 连接
3. Cloudflare 分配临时域名: xxx.trycloudflare.com
4. 外部请求 → Cloudflare → 隧道 → 家庭服务器
```

**技术特点：**
- 零配置公网访问
- 自动 HTTPS（Cloudflare 证书）
- DDoS 防护
- 免费使用

### 6.4 安装 cloudflared

**Linux (WSL):**

```bash
# 下载
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64

# 安装
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# 验证
cloudflared --version
```

**macOS:**

```bash
brew install cloudflare/cloudflare/cloudflared
```

**Windows:**

下载 exe 文件：https://github.com/cloudflare/cloudflared/releases

### 6.5 启动 Tunnel

**方式一：临时测试**

```bash
# 确保 MCP 服务先启动
python server.py --mode http

# 新终端启动 tunnel
cloudflared tunnel --url http://localhost:8080
```

输出：
```
INF Starting tunnel...
INF Tunnel credentials: /home/user/.cloudflared/xxxxx.json
INF + Proxying to http://localhost:8080
INF The tunnel has started!
INF Visit https://random-name.trycloudflare.com
```

**方式二：后台服务（生产环境）**

创建 systemd 服务：

```bash
sudo nano /etc/systemd/system/cloudflared-tunnel.service
```

内容：
```ini
[Unit]
Description=Cloudflare Tunnel for MCP Server
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/path/to/mcp-server
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:8080
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-tunnel
sudo systemctl start cloudflared-tunnel

# 查看日志
journalctl -u cloudflared-tunnel -f
```

### 6.6 常见问题

| 问题 | 解决方案 |
|------|----------|
| Tunnel 启动失败 | 检查端口是否被占用 |
| 连接超时 | 检查防火墙出站规则 |
| Token 过期 | 重新登录 cloudflared |
| 域名变更 | Tunnel 重启会分配新域名 |

### 6.7 其他内网穿透方案对比

| 方案 | 成本 | 难度 | 稳定性 |
|------|------|------|--------|
| **Cloudflare Tunnel** | 免费 | 低 | 高 |
| **Ngrok** | 免费/付费 | 低 | 高 |
| **Frp** | 需 VPS | 中 | 高 |
| **ZeroTier** | 免费 | 中 | 中 |

## 7. 配置远程 AI 客户端

### 7.1 Claude Desktop 配置

配置文件位置：
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

配置内容：
```json
{
  "mcpServers": {
    "blog-remote": {
      "url": "https://random-name.trycloudflare.com/sse"
    }
  }
}
```

### 7.2 Claude Code CLI 配置

```bash
# 添加 MCP 服务器
claude mcp add blog-remote -s http --url "https://random-name.trycloudflare.com"

# 查看已配置
claude mcp list

# 删除
claude mcp remove blog-remote
```

### 7.3 测试连接

访问 `https://random-name.trycloudflare.com` 应该返回：
```json
{
  "name": "blog-mcp-server",
  "version": "1.0.0"
}
```

## 8. 功能特性

### 已实现功能

- [x] Markdown 文章管理
- [x] 标签分类
- [x] 搜索功能
- [x] TOC 目录
- [x] 阅读时间估算
- [x] RSS 订阅
- [x] 密码保护
- [x] 图片上传
- [x] MCP 自动化发布

### 文章结构

```
src/content/posts/
├── images/              # 图片目录
│   └── 2026-01-05-*.jpeg
├── 2026-01-05-*.md      # 博客文章
└── welcome.md           # 欢迎文章
```

## 9. 常用命令

```bash
# 开发
npm run dev

# 构建
npm run build

# MCP 本地模式
python server.py

# MCP HTTP 模式
python server.py --mode http

# 启动 tunnel
cloudflared tunnel --url http://localhost:8080

# 上传图片测试
python upload_test.py
```

## 10. 总结

### 技术栈总结

| 层级 | 技术 | 作用 |
|------|------|------|
| 前端 | Astro | 静态站点生成 |
| 托管 | Vercel | 免费部署托管 |
| AI 协议 | MCP | 工具调用标准 |
| 代码托管 | GitHub | 版本控制 |
| 内网穿透 | Cloudflare | 远程访问 |

### 核心优势

1. **AI 集成** - 通过 MCP，AI 可以自动创建和发布文章
2. **零运维** - Vercel 自动部署，无需服务器
3. **免费托管** - Vercel 免费层够个人使用
4. **远程访问** - Cloudflare Tunnel 实现任意设备访问
5. **扩展性强** - 可以继续添加新功能

### 后续优化方向

- 添加评论系统 (Giscus/Utterances)
- 部署到私有服务器
- 添加图片图床 (Cloudinary/Imgur)
- 多作者支持
- CI/CD 优化

---

**博客地址：** https://blog-system-six-sepia.vercel.app

**RSS 订阅：** https://blog-system-six-sepia.vercel.app/rss.xml

**GitHub：** https://github.com/LiCong-22/blog-system-
