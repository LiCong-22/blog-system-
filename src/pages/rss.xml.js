import { getCollection } from 'astro:content';

export async function GET() {
	const posts = await getCollection('posts');
	const site = 'https://my-blog-system-tau.vercel.app';

	const xml = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
	<title>我的博客 | 记录思考与学习</title>
	<link>${site}</link>
	<description>记录与AI的对话、学习笔记和思考</description>
	<language>zh-CN</language>
	<atom:link href="${site}/rss.xml" rel="self" type="application/rss+xml" />
	${posts.map(post => `
	<item>
		<title><![CDATA[${post.data.title}]]></title>
		<link>${site}/posts/${post.id}/</link>
		<guid>${site}/posts/${post.id}/</guid>
		<description><![CDATA[${post.data.description}]]></description>
		<pubDate>${post.data.pubDate.toUTCString()}</pubDate>
		${post.data.tags.map(tag => `<category><![CDATA[${tag}]]></category>`).join('')}
	</item>`).join('')}
</channel>
</rss>`;

	return new Response(xml, {
		headers: {
			'Content-Type': 'application/xml',
		},
	});
}
