#!/usr/bin/env python3
"""测试 MCP 图片上传功能"""

import sys
sys.path.insert(0, '.')

import base64
from blog_tool import upload_image

# 图片路径
image_path = "/tmp/test_image.jpeg"
filename = "2026-01-05-test-image.jpeg"

# 读取并编码图片
with open(image_path, "rb") as f:
    base64_content = base64.b64encode(f.read()).decode('utf-8')

print(f"图片大小: {len(base64_content)} 字节 (Base64)")

# 调用 MCP 的 upload_image
result = upload_image(filename=filename, base64_content=base64_content)

print("="*50)
print("MCP 上传图片结果:")
print("="*50)
print(f"文件名: {result['filename']}")
print(f"路径: {result['path']}")
print(f"GitHub: {result['url']}")
print("="*50)
