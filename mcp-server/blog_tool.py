"""
博客发布工具 - MCP Server
功能：接收 AI 发送的博客内容，自动创建 Markdown 文件并提交到 GitHub
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path
from github import Github
from dotenv import load_dotenv
import json


class BlogPublisher:
    """博客发布器"""

    def __init__(self):
        load_dotenv()
        self.blog_path = os.getenv("BLOG_PATH", "/data/ulixc616/SVW_Dispaly/blog-system")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_owner = os.getenv("GITHUB_OWNER", "LiCong-22")
        self.github_repo = os.getenv("GITHUB_REPO", "blog-system-")

    def generate_filename(self, title: str) -> str:
        """根据标题生成文件名"""
        import re
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = safe_title.strip().lower().replace(' ', '-')
        safe_title = safe_title[:50]
        return f"{date_str}-{safe_title}.md"

    def format_markdown(self, title: str, content: str, tags: list = None, description: str = "") -> str:
        """格式化 Markdown 文件内容"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        tags_str = json.dumps(tags or [], ensure_ascii=False)

        return f"""---
title: "{title}"
description: "{description or title}"
pubDate: {date_str}
updatedDate: {date_str}
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

        os.chdir(self.blog_path)
        subprocess.run(["git", "add", str(filepath)], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Add post: {title}"], check=True, capture_output=True)
        subprocess.run(["git", "push"], check=True, capture_output=True)

        return {
            "success": True,
            "filename": filename,
            "filepath": str(filepath),
            "url": f"https://github.com/{self.github_owner}/{self.github_repo}/blob/main/src/content/posts/{filename}"
        }

    def list_posts(self) -> list:
        """列出所有文章"""
        posts_dir = Path(self.blog_path) / "src" / "content" / "posts"
        if not posts_dir.exists():
            return []

        posts = []
        for f in posts_dir.glob("*.md"):
            content = f.read_text(encoding='utf-8')
            import re
            title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else f.name
            posts.append({"filename": f.name, "title": title, "path": str(f)})

        return posts


BLOG_PUBLISHER = BlogPublisher()


def create_blog_post(title: str, content: str, tags: list = None, description: str = "") -> dict:
    """创建博客文章"""
    return BLOG_PUBLISHER.create_post(title, content, tags, description)


def list_blog_posts() -> dict:
    """列出所有博客文章"""
    posts = BLOG_PUBLISHER.list_posts()
    return {"posts": posts, "count": len(posts)}
