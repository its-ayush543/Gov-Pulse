
# import scrapy

# class IndianExpressSpider(scrapy.Spider):

#     name = 'indianexpress-spider'

#     allowed_domains = ['indianexpress.com']
#     start_urls = ['https://indianexpress.com/section/india/' , 'https://indianexpress.com/section/india/']


#     def parse( self, response ):

#         articles = response.css('div.articles')
#         # will get 25 articles on that page 

#         for article in articles :

#             articleUrl =  article.css('.img-context h2.title a::attr(href)').get()

#             yield response.follow( articleUrl , callback=self.parse_article_page )
#             # yield { 'link' : articleUrl }



#        # Going to the next page for next 25 articles 
#         pagination = response.css('ul.page-numbers')
#         nextpage_url = pagination.css('li a.next::attr(href)').get()


#         if nextpage_url:

#             yield response.follow( nextpage_url , callback = self.parse )





    


#     def parse_article_page( self,response) :

#         newsArticle = response.css('.ie_single_story_container')

#         url = response.url 
#         headline = newsArticle.css('h1#main-heading-article::text').get()
#         description = newsArticle.css('h2.synopsis::text').get()
#         date_time_published  = newsArticle.css('span[itemprop="dateModified"]::text').get()
#         date_time_machineform = newsArticle.css('span[itemprop="dateModified"]::attr(content)').get()
#         agency =  newsArticle.css('span.auth-nm::text ,div#storycenterbyline a::text').get()
#         body_content = response.xpath( 'normalize-space(string(//div[@id="pcl-full-content"]))').get()



#         yield {
#             'url': url ,
#             'title' : headline , 
#             'description' : description  , 
#             'publishing date & time' : date_time_published , 
#             'publishing_date_machine': date_time_machineform ,
#             'agency' : agency , 
#             'content' : body_content
#         }





import scrapy
import re
import json
from urllib.parse import urljoin
from news_scraper.items import NewsArticle



class IndianExpressSpider(scrapy.Spider):
    
    name = "indianexpress-spider"
    allowed_domains = ['indianexpress.com']
    start_urls = [
        "https://indianexpress.com/section/india/",
        "https://indianexpress.com/section/business/",
        "https://indianexpress.com/section/political-pulse/"
    ]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def parse(self, response):
        # Extract articles from the main listing page
        
        # Method 1: Extract from main articles container
        articles = response.css('div.articles')
        for article in articles:
            article_url = article.css('.img-context h2.title a::attr(href)').get()
            if article_url:
                absolute_url = urljoin(response.url, article_url)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Method 2: Extract from featured articles or other article containers
        featured_articles = response.css('.featured-articles a, .other-stories a')
        for item in featured_articles:
            article_url = item.css('::attr(href)').get()
            if article_url and 'article' in article_url:
                absolute_url = urljoin(response.url, article_url)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Method 3: Extract from any other article links on the page
        all_article_links = response.css('a::attr(href)').getall()
        for link in all_article_links:
            if link and ('article' in link or '/explained/' in link or '/opinion/' in link):
                # Filter for relevant sections
                if any(section in link for section in ['/india/', '/business/', '/explained/', '/opinion/', '/political-pulse/']):
                    absolute_url = urljoin(response.url, link)
                    yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Follow pagination if exists
        pagination = response.css('ul.page-numbers')
        next_page = pagination.css('li a.next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article_page(self, response):
        # Extract article data from individual article pages
        
        # Try multiple selectors as the site structure may vary
        article_data = {}
        
        # Extract headline/title
        headline = (
            response.css('h1#main-heading-article::text').get() or
            response.css('h1.native_story_title::text').get() or
            response.css('h1::text').get() or
            response.css('title::text').get() or
            ""
        )
        
        # Extract article body/content - Use your original working method first, then fallbacks
        content = ""
        
        # Method 1: Your original working XPath (most reliable for Indian Express)
        content = response.xpath('normalize-space(string(//div[@id="pcl-full-content"]))').get()
        
        # Method 2: Fallback CSS selectors
        if not content or len(content) < 100:
            content_selectors = [
                'div#pcl-full-content ::text',
                'div.full-details ::text',
                '.ie_single_story_container .full-details ::text',
                'div.story-element-text ::text',
                '.story-content ::text'
            ]
            
            for selector in content_selectors:
                content_paragraphs = response.css(selector).getall()
                if content_paragraphs:
                    content = ' '.join([p.strip() for p in content_paragraphs if p.strip()])
                    if len(content) > 100:  # Ensure we get substantial content
                        break
        
        # Method 3: Additional fallback with paragraph extraction
        if not content or len(content) < 100:
            content_paragraphs = response.css('.ie_single_story_container p::text, .story-element-text p::text, .full-details p::text').getall()
            content = ' '.join([p.strip() for p in content_paragraphs if p.strip()])
        
        # Extract publication date/time
        date_published = (
            response.css('span[itemprop="dateModified"]::text').get() or
            response.css('.publish-details time::text').get() or
            response.css('time::attr(datetime)').get() or
            response.css('[datetime]::attr(datetime)').get() or
            ""
        )
        
        # Extract machine readable date
        date_machine = (
            response.css('span[itemprop="dateModified"]::attr(content)').get() or
            response.css('time::attr(datetime)').get() or
            response.css('[datetime]::attr(datetime)').get() or
            ""
        )
        
        # Extract author/agency
        author = (
            response.css('span.auth-nm::text').get() or
            response.css('div#storycenterbyline a::text').get() or
            response.css('.author-name::text').get() or
            response.css('.byline::text').get() or
            ""
        )
        
        # Extract summary/description
        summary = (
            response.css('h2.synopsis::text').get() or
            response.css('meta[name="description"]::attr(content)').get() or
            response.css('.story-summary::text').get() or
            response.css('.excerpt::text').get() or
            ""
        )
        
        # Extract keywords
        keywords = (
            response.css('meta[name="keywords"]::attr(content)').get() or
            response.css('meta[name="news_keywords"]::attr(content)').get() or
            ""
        )
        
        # Extract image URL if available
        image_url = (
            response.css('.ie_single_story_container img::attr(src)').get() or
            response.css('.story-image img::attr(src)').get() or
            response.css('img::attr(data-src)').get() or
            response.css('img::attr(src)').get() or
            ""
        )
        
        # Determine category and subcategory from URL
        url_path = response.url.lower()
        category = "general"
        subcategory = ""
        
        if '/business/' in url_path:
            category = "business"
            subcategory = "business"
        elif '/india/' in url_path:
            category = "india"
            subcategory = "national"
        elif '/political-pulse/' in url_path:
            category = "politics"
            subcategory = "political-pulse"
        elif '/explained/' in url_path:
            category = "explained"
            subcategory = "analysis"
        elif '/opinion/' in url_path:
            category = "opinion"
            subcategory = "editorial"


        # Creating a NewsArticle Item 
        newsArticle = NewsArticle( )

        # and injecting the raw scraped data into the item just created 
        newsArticle['url'] = response.url
        newsArticle['headline'] = headline
        newsArticle['content'] = content
        newsArticle['summary'] = summary
        newsArticle['author'] = author
        newsArticle['date_published'] = date_published
        newsArticle['date_machine'] = date_machine
        newsArticle['keywords'] = keywords
        newsArticle['image_url'] = image_url
        newsArticle['category'] = category
        newsArticle['subcategory'] = subcategory
        newsArticle['source'] = 'Indian Express'

       # Yielding the Item to be then processed by Piplines 
        yield newsArticle 
        

    def parse_error(self, failure):
        # Handle request failures
        self.logger.error(f"Request failed: {failure.request.url}")





        





    