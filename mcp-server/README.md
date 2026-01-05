# Blog MCP Server with Cloudflare Tunnel

将 MCP 服务通过 Cloudflare Tunnel 暴露到公网，实现远程 AI 设备可调用。

## 架构

```
远程设备 (Claude Desktop)
       │
       ▼ HTTPS
┌──────────────────┐
│  Cloudflare      │  ← Tunnel
│  全球网络         │
└────────┬─────────┘
         │
         ▼ (加密隧道)
┌──────────────────┐
│  家庭服务器       │
│  ├─ cloudflared  │
│  └─ MCP Server   │
└──────────────────┘
```

## 快速开始

### 1. 安装 cloudflared (WSL/Linux)

```bash
# 在 WSL 中下载
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O cloudflared

# 安装到系统路径
sudo mv cloudflared /usr/local/bin/
sudo chmod +x /usr/local/bin/cloudflared

# 验证安装
cloudflared --version
```

### 2. 安装 MCP 服务依赖

```bash
cd mcp-server
source .venv/bin/activate  # 激活虚拟环境

# 如果没有 pip，先安装
python -m ensurepip --upgrade 2>/dev/null || true

# 安装依赖
pip install -r requirements.txt
```

### 3. 本地测试 HTTP 模式

```bash
# 启动 MCP HTTP 服务 (默认端口 8080)
python server.py --mode http

# 或指定端口
python server.py --mode http --port 9000
```

### 4. 启动 Tunnel

**方式一：临时测试（前台运行）**

```bash
# 新开一个终端，启动 tunnel
cloudflared tunnel --url http://localhost:8080
```

成功后显示类似：
```
2024-01-01T00:00:00Z INF Starting tunnel...
2024-01-01T00:00:00Z INF Tunnel credentials file: /home/user/.cloudflared/*.json
2024-01-01T00:00:00Z INF + proxying to http://localhost:8080
2024-01-01T00:00:00Z INF + Starting metrics server on 127.0.0.1:port
2024-01-01T00:00:00ZINF The tunnel has started. Visit https://random-name.trycloudflare.com
```

**方式二：后台服务（推荐）**

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
WorkingDirectory=/path/to/blog-system/mcp-server
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

# 查看状态
sudo systemctl status cloudflared-tunnel

# 查看日志
journalctl -u cloudflared-tunnel -f
```

### 5. 获取公网地址

查看 tunnel 日志，找到类似：
```
The tunnel has started. Visit https://random-name.trycloudflare.com
```

这就是你的 MCP 服务公网地址！

## 使用方式

### 方式一：MCP Inspector 测试

```bash
# 安装 mcp inspector
npm install -g @modelcontextprotocol/inspector

# 测试连接
npx @modelcontextprotocol/inspector http https://你的域名.trycloudflare.com
```

### 方式二：配置 Claude Desktop

在 Claude Desktop 的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "blog-remote": {
      "url": "https://你的域名.trycloudflare.com/sse"
    }
  }
}
```

### 方式三：其他 MCP Client

任何支持 HTTP 传输的 MCP Client 都可以连接：
```
https://你的域名.trycloudflare.com
```

## 命令参考

```bash
# 启动 MCP HTTP 服务
python server.py --mode http                    # 默认 8080 端口
python server.py --mode http --port 9000        # 自定义端口

# 启动 tunnel
cloudflared tunnel --url http://localhost:8080

# 后台运行 tunnel
nohup cloudflared tunnel --url http://localhost:8080 > tunnel.log 2>&1 &
```

## 故障排除

### Tunnel 启动失败
- 检查 cloudflared 是否正确安装
- 确保端口 8080 没有被占用

### 连接超时
- 确认家庭服务器防火墙允许出站
- 检查 cloudflared 日志：`journalctl -u cloudflared-tunnel`

### MCP 调用失败
- 确认 MCP 服务正在运行：`curl http://localhost:8080/sse`
- 检查 MCP 服务日志

## 安全建议

1. **使用 token 验证**（进阶）
   - 在 MCP 服务添加 API Key 验证
   - 只允许授权客户端连接

2. **HTTPS 自动启用**
   - Cloudflare Tunnel 自动提供 HTTPS
   - 无需额外配置

3. **访问日志**
   - 通过 Cloudflare Dashboard 查看访问记录
