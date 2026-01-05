---
title: "MCP Server 设计解析"
description: "深入理解 MCP 协议架构和开发流程"
pubDate: 2026-01-05
updatedDate: 2026-01-05
tags: ["MCP", "AI", "Python", "架构设计"]
---

# MCP Server 设计解析

本文深入介绍 MCP (Model Context Protocol) Server 的架构设计和开发流程。

## 1. 核心架构

```
AI (Claude)          MCP Server          业务逻辑
    │                   │                   │
    │  list_tools      │                   │
    │ ───────────────► │                   │
    │                  │ ── 查询 ─────────►│
    │                  │ ◄── 返回工具列表──│
    │  返回工具描述     │                   │
    │ ◄─────────────── │                   │
    │                   │                   │
    │  call_tool       │                   │
    │ ───────────────► │                   │
    │                  │ ── 调用 ─────────►│
    │                  │   创建 md 文件     │
    │                  │   git push        │
    │                  │ ◄── 返回结果 ──── │
    │  返回执行结果     │                   │
    │ ◄─────────────── │                   │
```

## 2. 使用的库和 API

| 库/模块 | 用途 |
|---------|------|
| mcp.server | MCP 协议核心 |
| mcp.types | 定义 Tool、TextContent |
| PyGithub | GitHub API 交互 |
| python-dotenv | 环境变量管理 |
| aiohttp | HTTP 服务器 |

## 3. MCP 开发流程

```
1. 安装依赖
   pip install mcp PyGithub python-dotenv aiohttp

2. 创建 Server 实例
   server = Server('my-mcp-server')

3. 定义工具 (list_tools)
   - 工具名 name
   - 描述 description
   - 输入参数 inputSchema (JSON Schema)

4. 实现工具逻辑 (call_tool)
   - 根据 name 分发
   - 调用业务函数
   - 返回 TextContent[]

5. 选择传输模式
   - stdio: 标准输入输出 (本地)
   - HTTP: 网络传输 (远程)

6. 配置客户端
   Claude Desktop / Claude Code 添加 MCP 配置
```

## 4. 核心 API 详解

```python
# 创建服务器
server = Server('blog-mcp-server')

# 定义工具
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name='create_blog_post',
            description='创建博客文章',
            inputSchema={
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': '文章标题'},
                    'content': {'type': 'string', 'description': '文章内容'}
                },
                'required': ['title', 'content']
            }
        )
    ]

# 处理工具调用
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == 'create_blog_post':
        result = create_blog_post(...)
        return [TextContent(type='text', text=result)]
```

## 5. JSON-RPC 协议

```json
// 请求
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_blog_post",
    "arguments": {"title": "标题", "content": "内容"}
  }
}

// 响应
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {"content": [{"type": "text", "text": "成功"}]}
}
```

## 6. 两种传输模式

| 模式 | 命令 | 场景 |
|------|------|------|
| stdio | python server.py | 本地 Claude Desktop |
| HTTP | python server.py --mode http | 远程（配合 cloudflared） |

## 7. 文件结构

```
mcp-server/
├── server.py      # MCP Server (协议层)
├── blog_tool.py   # 业务逻辑层
├── requirements.txt
└── README.md
```

## 总结

MCP 的核心是：**定义工具 → 处理调用 → 执行业务 → 返回结果**
