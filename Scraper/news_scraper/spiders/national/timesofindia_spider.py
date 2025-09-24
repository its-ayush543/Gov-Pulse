
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


class TimesOfIndiaSpider(scrapy.Spider):
    
    name = "timesofindia-spider"

    allowed_domains = ['timesofindia.indiatimes.com', 'm.timesofindia.com']
    start_urls = [
        "https://timesofindia.indiatimes.com/business/india-business",
        "https://m.timesofindia.com/business/india-business"
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
        content_selectors = [ 'div.ga-headlines .Normal', 'div[data-articlebody]', '.okf2Z .bEqpj', '.article_content', 'div.Normal','.content']
        
        content_paragraphs = []
        
        for selector in content_selectors:
            paragraphs = response.css(f'{selector} ::text').getall()
            if paragraphs:
                content_paragraphs = paragraphs
                break
        
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
            'category': 'business',
            'subcategory': 'india-business'
        }
        
        # Only yield if we have at least a headline and some content
        if article_data['headline'] and (article_data['content'] or article_data['summary']):
            yield article_data
        else:
            # Log for debugging purposes
            self.logger.warning(f"Skipping article with insufficient data: {response.url}")

    def parse_error(self, failure):
        # Handle request failures
        self.logger.error(f"Request failed: {failure.request.url}")