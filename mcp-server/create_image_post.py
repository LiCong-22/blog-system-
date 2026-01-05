#!/usr/bin/env python3
"""创建包含图片的测试博客文章"""

import sys
sys.path.insert(0, '.')

from blog_tool import create_blog_post

content = """# MCP 图片上传测试

这是一篇使用 MCP 上传图片功能的测试文章。

## 测试图片

![MCP 测试图片](./images/2026-01-05-test-image.jpeg)

## 功能说明

通过 MCP 的 `upload_image` 工具上传图片：

1. **上传图片**：调用 `upload_image(filename, base64_content)`
2. **获取路径**：得到返回的相对路径 `./images/filename.jpeg`
3. **在文章中引用**：使用 `![描述](./images/filename.jpeg)`

## 图片信息

- 文件名：2026-01-05-test-image.jpeg
- 大小：383KB
- 格式：JPEG

## 总结

MCP 图片上传功能正常工作！"""

result = create_blog_post(
    title='MCP 图片上传测试',
    content=content,
    tags=['测试', 'MCP', '图片'],
    description='测试 MCP 图片上传功能'
)

print("="*50)
print("MCP 创建博客结果:")
print("="*50)
print(f"标题: {result['filename']}")
print(f"路径: {result['filepath']}")
print(f"URL: {result['url']}")
print("="*50)
