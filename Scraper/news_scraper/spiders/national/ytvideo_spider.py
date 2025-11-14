"""Minimal YouTube spider: fetch recent videos and emit NewsArticle-compatible items.
Removes sentiment, transcript and classification for simplicity."""

import os
import scrapy
from googleapiclient.discovery import build
from datetime import datetime
from html import unescape


class YouTubeGovernmentSpider(scrapy.Spider):
    name = "ytvideo-spider"

    GOVERNMENT_CHANNELS = {
        'Times of India': 'UCckHqySbfy5FcPP6MD_S-Yg',
        # Add more channel IDs as needed
    }

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 2,
        'ROBOTSTXT_OBEY': False
    }

    def __init__(self, youtube_api_key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.youtube_api_key = youtube_api_key or os.getenv("YOUTUBE_API_KEY") or "AIzaSyAhGA8gbyxXxH4hCXOO7muvKTyUB1jWev0"
        if not self.youtube_api_key:
            raise ValueError("Missing YouTube API key")
        self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)

    def start_requests(self):
        for channel_name, channel_id in self.GOVERNMENT_CHANNELS.items():
            yield scrapy.Request(
                url=f'https://www.youtube.com/channel/{channel_id}',
                callback=self.parse_channel,
                meta={'channel_name': channel_name, 'channel_id': channel_id},
                dont_filter=True
            )

    async def start(self):  # Scrapy 2.13+ compatibility
        async for r in self._start_iter():
            yield r

    async def _start_iter(self):
        for channel_name, channel_id in self.GOVERNMENT_CHANNELS.items():
            yield scrapy.Request(
                url=f'https://www.youtube.com/channel/{channel_id}',
                callback=self.parse_channel,
                meta={'channel_name': channel_name, 'channel_id': channel_id},
                dont_filter=True
            )

    def parse_channel(self, response):
        channel_id = response.meta['channel_id']
        channel_name = response.meta['channel_name']
        try:
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=10,
                order='date',
                type='video'
            )
            data = request.execute()
            for item in data.get('items', []):
                snippet = item['snippet']
                video_id = item['id']['videoId']
                title_raw = snippet.get('title', '')
                title = unescape(title_raw).strip()
                description = (snippet.get('description') or '').strip()
                published = snippet.get('publishedAt', '')
                # Build NewsArticle-compatible item
                yield {
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'headline': title,
                    'content': description,
                    'summary': description[:200],
                    'author': '',
                    'date_published': published,
                    'image_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                    'keywords': '',
                    'tags': [],
                    'category': 'video',
                    'subcategory': channel_name,
                    'source': 'youtube',
                    'scraped_at': datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"YouTube API error for {channel_name}: {e}")


if __name__ == "__main__":
    pass



