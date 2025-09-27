
import scrapy
import re
import json
from urllib.parse import urljoin
from news_scraper.items import NewsArticle


class NdtvSpider(scrapy.Spider):
    
    name = "ndtv-spider"
    
    allowed_domains = ['ndtv.com', 'www.ndtv.com']
    start_urls = [
        "https://www.ndtv.com/opinion-search/government"
    ]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def parse(self, response):
        # Extract articles from the opinion search page
        
        # Method 1: Extract from main article listings
        article_links = response.css('a[href*="/opinion/"]::attr(href)').getall()
        
        for link in article_links:
            if link and not link.startswith('javascript:'):
                absolute_url = urljoin(response.url, link)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Method 2: Extract from card listings (common NDTV structure)
        card_articles = response.css('.crd-d_v1-li a, .nws-lst_li a, .lst-pg_li a')
        for card in card_articles:
            article_url = card.css('::attr(href)').get()
            if article_url and '/opinion/' in article_url:
                absolute_url = urljoin(response.url, article_url)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Method 3: Extract from featured opinion articles
        featured_articles = response.css('.OpnFt_li a, .ft-opn_li a')
        for featured in featured_articles:
            article_url = featured.css('::attr(href)').get()
            if article_url and '/opinion/' in article_url:
                absolute_url = urljoin(response.url, article_url)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Method 4: Extract from any div containing opinion links
        opinion_containers = response.css('div[class*="opn"] a, div[class*="Opn"] a')
        for container in opinion_containers:
            article_url = container.css('::attr(href)').get()
            if article_url and '/opinion/' in article_url and not article_url.startswith('javascript:'):
                absolute_url = urljoin(response.url, article_url)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Handle pagination
        current_page = self.get_page_number(response.url)
        
        # Try to find next page button/link
        next_page_link = response.css('a[href*="page="]::attr(href)').get()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)
        
        # If no explicit next page link found, try incrementing page number
        if current_page < 20:  # Limit to prevent infinite pagination
            next_page = current_page + 1
            next_url = f"https://www.ndtv.com/opinion-search/government?page={next_page}"
            
            # Check if there are articles on current page before proceeding
            if article_links or card_articles or featured_articles:
                yield response.follow(next_url, callback=self.parse)

    def get_page_number(self, url):
        """Extract page number from URL"""
        match = re.search(r'page=(\d+)', url)
        return int(match.group(1)) if match else 1

    def parse_article_page(self, response):
        # Extract article data from individual opinion article pages
        
        # Extract headline/title
        headline = (
            response.css('h1.sp-ttl::text').get() or
            response.css('h1.articletitle::text').get() or
            response.css('h1::text').get() or
            response.css('.pst-ttl::text').get() or
            response.css('title::text').get() or
            ""
        )
        
        # Extract article body/content - NDTV specific selectors
        content_selectors = [
            '.sp-cn .fullstory',
            '.ins_storybody',
            '.pst-cnt',
            'div[itemprop="articleBody"]',
            '.story_content',
            '.article_content',
            '.fullstory'
        ]
        
        content_paragraphs = []
        
        for selector in content_selectors:
            paragraphs = response.css(f'{selector} ::text').getall()
            if paragraphs:
                # Filter out navigation text and clean content
                cleaned_paragraphs = []
                for p in paragraphs:
                    text = p.strip()
                    if text and len(text) > 10 and not any(skip_word in text.lower() for skip_word in 
                        ['advertisement', 'read more', 'click here', 'subscribe', 'follow us']):
                        cleaned_paragraphs.append(text)
                if cleaned_paragraphs:
                    content_paragraphs = cleaned_paragraphs
                    break
        
        # Clean and join content
        content = ' '.join(content_paragraphs)
        
        # Extract publication date/time
        date_published = (
            response.css('time::attr(datetime)').get() or
            response.css('.pst-by_tm::text').get() or
            response.css('.sp-descp .pst-by::text').get() or
            response.css('.publish_on::text').get() or
            response.css('[datetime]::attr(datetime)').get() or
            response.css('meta[property="article:published_time"]::attr(content)').get() or
            ""
        )
        
        # Extract author
        author = (
            response.css('.pst-by_nm a::text').get() or
            response.css('.sp-descp .pst-by a::text').get() or
            response.css('.author::text').get() or
            response.css('.byline::text').get() or
            response.css('meta[name="author"]::attr(content)').get() or
            ""
        )
        
        # Extract summary/description
        summary = (
            response.css('meta[name="description"]::attr(content)').get() or
            response.css('meta[property="og:description"]::attr(content)').get() or
            response.css('.sp-descp::text').get() or
            response.css('.article_summary::text').get() or
            ""
        )
        
        # Extract keywords
        keywords = (
            response.css('meta[name="keywords"]::attr(content)').get() or
            response.css('meta[name="news_keywords"]::attr(content)').get() or
            response.css('meta[property="article:tag"]::attr(content)').get() or
            ""
        )
        
        # Extract image URL if available
        image_url = (
            response.css('meta[property="og:image"]::attr(content)').get() or
            response.css('.sp-img img::attr(src)').get() or
            response.css('.leadmedia img::attr(src)').get() or
            response.css('img::attr(data-src)').get() or
            response.css('.article_image img::attr(src)').get() or
            ""
        )
        
        # Extract tags/categories specific to opinion articles
        tags = []
        tag_elements = response.css('.sp-tgs a::text, .article_tags a::text').getall()
        if tag_elements:
            tags = [tag.strip() for tag in tag_elements if tag.strip()]

        # Build the article data dictionary
        article_data = {
            'url': response.url,
            'headline': headline,
            'content': content,
            'summary': summary,
            'author': author,
            'date_published': date_published,
            'keywords': keywords,
            'image_url': image_url,
            # 'tags': tags,
            'category': 'opinion',
            'subcategory': 'government',
            'source': 'NDTV'
        }
        
        newsArticle = NewsArticle(**article_data)
            



    def parse_error(self, failure):
        # Handle request failures
        self.logger.error(f"Request failed: {failure.request.url}")
        
        # Log additional failure information
        if hasattr(failure.value, 'response'):
            self.logger.error(f"HTTP Status: {failure.value.response.status}")