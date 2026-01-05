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



## 2. 使用的库和 API

| 库/模块 | 用途 |
|---------|------|
| mcp.server | MCP 协议核心 |
| mcp.types | 定义 Tool、TextContent |
| PyGithub | GitHub API 交互 |
| python-dotenv | 环境变量管理 |
| aiohttp | HTTP 服务器 |

## 3. MCP 开发流程



## 4. 核心 API 详解



## 5. JSON-RPC 协议



## 6. 两种传输模式

| 模式 | 命令 | 场景 |
|------|------|------|
| stdio | python server.py | 本地 Claude Desktop |
| HTTP | python server.py --mode http | 远程（配合 cloudflared） |

## 7. 文件结构



## 总结

MCP 的核心是：**定义工具 → 处理调用 → 执行业务 → 返回结果**
