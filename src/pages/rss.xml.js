import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
	const posts = await getCollection('posts');

	return rss({
		title: '我的博客 | 记录思考与学习',
		description: '记录与AI的对话、学习笔记和思考',
		site: context.site || 'https://my-blog-system-tau.vercel.app',
		items: posts.map((post) => ({
			title: post.data.title,
			pubDate: post.data.pubDate,
			description: post.data.description,
			link: `/posts/${post.id}/`,
			categories: post.data.tags,
		})),
		_customData: `<language>zh-CN</language>`,
	});
}
