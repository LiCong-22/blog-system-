# 博客系统 (Astro + Vercel)

这是用 Astro 静态站点生成器 + Vercel 部署的博客系统。

## 项目结构

```
blog-system/
├── src/content/posts/    # 博客文章 (Markdown)
├── mcp-server/           # MCP 自动发布工具
└── public/               # 静态资源
```

## 发布文章

当用户要求"把对话总结成博客"、"发布文章"时：

### 方式1：使用 MCP（推荐）
启动 MCP Server 后，调用 `create_blog_post` 工具。

### 方式2：手动创建
1. 在 `src/content/posts/` 创建 Markdown 文件
2. 文件格式：
```markdown
---
title: "文章标题"
description: "简短描述"
pubDate: 2026-01-05
tags: ["标签1", "标签2"]
# password: "密码"    # 可选：加密文章
---

# 文章内容...
```
3. 提交到 GitHub：`git add` → `git commit` → `git push`
4. Vercel 会自动部署

## 加密文章

如需加密文章，在 frontmatter 中添加 `password` 字段：

```markdown
---
title: "私有文章"
description: "描述"
pubDate: 2026-01-05
tags: ["私有"]
password: "lc8814"
---
```

访问时需要输入密码解锁，解锁状态保存在 localStorage。

## 常用命令

```bash
npm run dev      # 本地开发
npm run build    # 构建生产版本
```

## 链接

- 博客：https://my-blog-system-tau.vercel.app
- RSS：https://my-blog-system-tau.vercel.app/rss.xml
- 仓库：https://github.com/LiCong-22/blog-system-
