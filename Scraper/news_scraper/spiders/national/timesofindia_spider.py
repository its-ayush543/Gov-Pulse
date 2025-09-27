
# import scrapy
# import re 
# import json 


# class TimesOfIndiaSpider(scrapy.Spider):
    
#     name = "timesofindia-spider"
#     allowed_domains = ['timesofindia.indiatimes.com']
#     start_urls = ["https://timesofindia.indiatimes.com/business/india-business"]


#     def parse(self , response) :

#         content = response.css('.pepH5 .wRxdF')
#         articles = content.css('figure')

#         for article in articles :

#             articleUrl = article.css('a::attr(href)').get()

#             # yield response.follow(articleUrl , callback=self.parse_article_page )
#             yield { 'link':articleUrl}




    


#     # def parse_article_page (self,response):
       
#     #    main_article = response.css('.okf2Z')

#     #    headline = main_article.css('.pZFl7 h1 span::text').get()
#     #    agency = main_article.css('.t8vf3 .xf8Pm a::text').get()
#     #    date_time_published = main_article.css('.t8vf3 .xf8Pm span::text').get()
#     #    date_time_machineform = main_article.css('.t8vf3 .xf8Pm span::content').get()
       
#     #    summmary = main_article.css('div.M1rHh::text').get()

        




import scrapy
import re
import json
from urllib.parse import urljoin
from news_scraper.items import NewsArticle 

class TimesOfIndiaSpider(scrapy.Spider):
    
    name = "timesofindia-spider"

    allowed_domains = ['timesofindia.indiatimes.com', 'm.timesofindia.com']
    start_urls = [
        "https://timesofindia.indiatimes.com/business/india-business",
        "https://m.timesofindia.com/business/india-business", 
        "https://timesofindia.indiatimes.com/business/infrastructure" ,
    ]
    
    # custom_settings = {
    #     'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    # }





    def parse(self, response):
        # Extract articles from the main listing page
        
        # Method 1: Extract from lead article
        lead_article = response.css('.leadimg a')
        if lead_article:
            article_url = lead_article.css('::attr(href)').get()
            if article_url:
                absolute_url = urljoin(response.url, article_url)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Method 2: Extract from news items list
        news_items = response.css('li.news_items a, .remaning_news li a')
        for item in news_items:
            article_url = item.css('::attr(href)').get()
            if article_url and '/articleshow/' in article_url:
                absolute_url = urljoin(response.url, article_url)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Method 3: Extract from any other article links on the page
        all_article_links = response.css('a[href*="/articleshow/"]::attr(href)').getall()
        for link in all_article_links:
            if '/business/' in link or '/india-business/' in link:
                absolute_url = urljoin(response.url, link)
                yield response.follow(absolute_url, callback=self.parse_article_page)
        
        # Follow pagination if exists
        next_page = response.css('a.more_btn::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)









    def parse_article_page(self, response):
        # Extract article data from individual article pages
        
        # Try multiple selectors as the site structure may vary
        article_data = {}
        
        # Extract headline/title
        headline = (
            response.css('h1.articletitle::text').get() or
            response.css('h1::text').get() or
            response.css('.pZFl7 h1 span::text').get() or
            response.css('title::text').get() or
            ""
        )
        
        # Extract article body/content
        content_selectors = [ 'div.ga-headlines .Normal', 'div[data-articlebody]', '.okf2Z .bEqpj', '.article_content', 'div.Normal','.content''div._s30J clearfix',
        'div.clearfix div',
        'span[data-articlebody="1"]',
        '.ga-headlines div',
        'article div',
        '.story-content',
        '.article-body']
        
        content_paragraphs = []
        
        for selector in content_selectors:
            paragraphs = response.css(f'{selector}::text').getall()
            if paragraphs and len(' '.join(paragraphs)) > 100:  # Ensure substantial content
                content_paragraphs = paragraphs
                break
    
    # If still no content, try a broader approach
        if not content_paragraphs:
        # Try extracting all paragraph text
            all_paragraphs = response.css('p::text').getall()
            if all_paragraphs:
            # Filter out navigation and footer content
             filtered_paragraphs = [
                p.strip() for p in all_paragraphs 
                if len(p.strip()) > 20 and 
                not any(skip in p.lower() for skip in ['subscribe', 'follow', 'share', 'advertisement'])
            ]
            if len(' '.join(filtered_paragraphs)) > 100:
                content_paragraphs = filtered_paragraphs
        

        # Clean and join content
        content = ' '.join([p.strip() for p in content_paragraphs if p.strip()])
        
        # Extract publication date/time
        date_published = ( response.css('.publish_on::text').get() or
            response.css('.t8vf3 .xf8Pm span::text').get() or
            response.css('time::attr(datetime)').get() or
            response.css('[datetime]::attr(datetime)').get() or
            ""
        )
        
        # Extract author/agency
        author = (
            response.css('.author::text').get() or
            response.css('.t8vf3 .xf8Pm a::text').get() or
            response.css('.byline::text').get() or
            ""
        )
        
        # Extract summary/description
        summary = (
            response.css('meta[name="description"]::attr(content)').get() or
            response.css('.M1rHh::text').get() or
            response.css('.summary::text').get() or
            ""
        )
        
        # Extract keywords
        keywords = (  response.css('meta[name="keywords"]::attr(content)').get() or response.css('meta[name="news_keywords"]::attr(content)').get() or "" )
        
        # Extract image URL if available
        image_url = (  response.css('.leadmedia img::attr(src)').get() or response.css('img::attr(data-src)').get() or response.css('img::attr(src)').get() or "" )
        


        # 2. Create an instance of your NewsArticle item
        newsArticle = NewsArticle()

        # 3. Populate the item's fields from the dictionary
        newsArticle['url'] = response.url
        newsArticle['headline'] = headline
        newsArticle['content'] = content_paragraphs
        newsArticle['summary'] = summary
        newsArticle['author'] = author
        newsArticle['date_published'] = date_published
        newsArticle['keywords'] = keywords
        newsArticle['image_url'] = image_url
        newsArticle['category'] = 'business' 
        newsArticle['subcategory'] = 'india-business' 
        newsArticle['source'] = 'Times of India'
        
        # 4. Yield the populated item to be processed by your pipelines
        yield newsArticle




    def parse_error(self, failure):
        # Handle request failures
        self.logger.error(f"Request failed: {failure.request.url}")