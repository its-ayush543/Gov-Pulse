

import scrapy
import re
import json
from urllib.parse import urljoin
from news_scraper.items import NewsArticle


class TelegraphSpider(scrapy.Spider):
    
    name = "telegraph-spider"
    
    allowed_domains = ['telegraphindia.com', 'www.telegraphindia.com']
    start_urls = [
        "https://www.telegraphindia.com/west-bengal/kolkata"
    ]

    def parse(self, response):
        # Extract articles from the main listing page
        
        # Method 1: Extract from main story listing
        story_links = response.css('ul.storylisting li a::attr(href)').getall()
        for link in story_links:
            if link:
                absolute_url = urljoin(response.url, link)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Method 2: Extract from article links in various sections
        article_selectors = [
            'a[href*="/west-bengal/kolkata/"]',
            'a[href*="/video/"]',
            'a[href*="/india/"]',
            'a[href*="/opinion/"]',
            'h2 a, h3 a',
            '.storylisting a',
            '.lblisting a',
            '.ymalisting a'
        ]
        
        for selector in article_selectors:
            links = response.css(f'{selector}::attr(href)').getall()
            for link in links:
                if link and not link.startswith('javascript:') and '/cid/' in link:
                    absolute_url = urljoin(response.url, link)
                    yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Handle pagination
        current_page = self.get_page_number(response.url)
        
        # Check for next page link
        next_page_link = response.css('.paginationbox a.nxtpvr::attr(href)').get()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)
        
        # Alternative pagination - try incrementing page number up to 20 pages
        elif current_page < 20:
            # Check if there are articles on current page before proceeding
            if story_links or response.css('ul.storylisting li'):
                next_page = current_page + 1
                next_url = f"https://www.telegraphindia.com/west-bengal/kolkata/page-{next_page}"
                yield response.follow(next_url, callback=self.parse)

    def get_page_number(self, url):
        """Extract page number from URL"""
        match = re.search(r'page-(\d+)', url)
        return int(match.group(1)) if match else 1

    def parse_article_page(self, response):
        # Extract article data from individual article pages
        
        # Extract headline/title
        headline = (
            response.css('h1::text').get() or
            response.css('.articletsection h1::text').get() or
            response.css('meta[property="og:title"]::attr(content)').get() or
            response.css('title::text').get() or
            ""
        )
        
        # Extract article body/content - Telegraph specific selectors
        content_selectors = [
            'article#contentbox p',
            '.articlemidbox p',
            '.articlebox p',
            'article p',
            '.content p',
            '[id="contentbox"] p'
        ]
        
        content_paragraphs = []
        
        for selector in content_selectors:
            paragraphs = response.css(f'{selector}::text').getall()
            if paragraphs:
                # Filter out ads and navigation text
                cleaned_paragraphs = []
                for p in paragraphs:
                    text = p.strip()
                    if (text and len(text) > 30 and 
                        not any(skip_word in text.lower() for skip_word in 
                            ['advertisement', 'read more', 'click here', 'subscribe', 
                             'follow us', 'share', 'tweet', 'facebook', 'whatsapp',
                             'story:', 'video producer:', 'video editor:'])):
                        cleaned_paragraphs.append(text)
                if cleaned_paragraphs:
                    content_paragraphs = cleaned_paragraphs
                    break
        
        # Clean and join content
        content = ' '.join(content_paragraphs)
        
        # Extract publication date/time
        date_published = (
            response.css('.publishdate::text').get() or
            response.css('.publishbynowtxt::text').get() or
            response.css('meta[property="article:published_time"]::attr(content)').get() or
            response.css('time::attr(datetime)').get() or
            response.css('[datetime]::attr(datetime)').get() or
            ""
        )
        
        # Extract author/byline
        author_selectors = [
            'meta[name="author"]::attr(content)',
            '.publishbynowtxt:contains("By")::text',
            '.byline::text',
            '.author::text'
        ]
        
        author = ""
        for selector in author_selectors:
            author_text = response.css(selector).get()
            if author_text:
                # Clean "By" prefix if present
                author = author_text.replace('By ', '').strip()
                break
        
        # Extract summary/description
        summary = (
            response.css('h2.mt-24::text').get() or
            response.css('.articletsection h2::text').get() or
            response.css('meta[name="description"]::attr(content)').get() or
            response.css('meta[property="og:description"]::attr(content)').get() or
            ""
        )
        
        # Extract keywords
        keywords = (
            response.css('meta[name="keywords"]::attr(content)').get() or
            response.css('meta[name="news_keywords"]::attr(content)').get() or
            ""
        )
        
        # Extract image URL
        image_url = (
            response.css('meta[property="og:image"]::attr(content)').get() or
            response.css('.leadimgebox img::attr(src)').get() or
            response.css('.leadimgebox img::attr(data-src)').get() or
            response.css('figure img::attr(src)').get() or
            response.css('figure img::attr(data-src)').get() or
            ""
        )
        
        # Extract related topics/tags
        tags = []
        tag_elements = response.css('.relatedtopicbox .ategbox a::text').getall()
        if tag_elements:
            tags = [tag.strip() for tag in tag_elements if tag.strip()]
        
        # Determine category and subcategory from URL
        category = "kolkata"
        subcategory = ""
        
        if '/video/' in response.url:
            subcategory = "video"
        elif '/opinion/' in response.url:
            category = "opinion"
            subcategory = "kolkata"
        elif '/business/' in response.url:
            category = "business"
            subcategory = "kolkata"
        elif '/sports/' in response.url:
            category = "sports"
            subcategory = "kolkata"

        # Build the article data dictionary
        article_data = {
            'url': response.url,
            'headline': headline.strip() if headline else "",
            'content': content.strip() if content else "",
            'summary': summary.strip() if summary else "",
            'author': author.strip() if author else "",
            'date_published': date_published.strip() if date_published else "",
            'keywords': keywords.strip() if keywords else "",
            'image_url': image_url.strip() if image_url else "",
            # 'tags': tags,
            'category': category,
            'subcategory': subcategory,
            'source': 'Telegraph India'
        }


        # 2. Create an instance of your NewsArticle item
        newsArticle = NewsArticle()

        # 3. Populate the item's fields from the dictionary
        newsArticle['url'] = article_data['url']
        newsArticle['headline'] = article_data['headline']
        newsArticle['content'] = article_data['content']
        newsArticle['summary'] = article_data['summary']
        newsArticle['author'] = article_data['author']
        newsArticle['date_published'] = article_data['date_published']
        newsArticle['keywords'] = article_data['keywords']
        newsArticle['image_url'] = article_data['image_url']
        newsArticle['category'] = article_data['category']
        newsArticle['subcategory'] = article_data['subcategory']
        newsArticle['source'] = article_data['source']
        
        # 4. Yield the populated item to be processed by your pipelines
        yield newsArticle
        


        def parse_error(self, failure):
            # Handle request failures
            self.logger.error(f"Request failed: {failure.request.url}")
            
            # Log additional failure information
            if hasattr(failure.value, 'response'):
                self.logger.error(f"HTTP Status: {failure.value.response.status}")