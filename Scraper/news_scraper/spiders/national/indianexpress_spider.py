
import scrapy

class IndianExpressSpider(scrapy.Spider):

    name = 'indianexpress-spider'
    allowed_domains = ['indianexpress.com']

    start_urls = ['https://indianexpress.com/section/india/']


    def parse( self, response ):

        articles = response.css('div.articles')
        # will get 25 articles on that page 

        for article in articles :

            articleUrl =  article.css('.img-context h2.title a::attr(href)').get()

            yield response.follow( articleUrl , callback=self.parse_article_page )
            # yield { 'link' : articleUrl }



       # Going to the next page for next 25 articles 
        pagination = response.css('ul.page-numbers')
        nextpage_url = pagination.css('li a.next::attr(href)').get()


        if nextpage_url:

            yield response.follow( nextpage_url , callback = self.parse )





    




    def parse_article_page( self,response) :

        newsArticle = response.css('.ie_single_story_container')

        headline = newsArticle.css('h1#main-heading-article::text').get()

        synposis = newsArticle.css('h2.synopsis::text').get()
        
        date_time_published  = newsArticle.css('span[itemprop="dateModified"]::text').get()
        date_time_machineform = newsArticle.css('span[itemprop="dateModified"]::attr(content)').get()

        agency =  newsArticle.css('div#storycenterbyline a::text').get()

        body_content = response.xpath( 'normalize-space(string(//div[@id="pcl-full-content"]))').get()



        yield {
            'headline' : headline , 
            'synposis' : synposis , 
            'publishing date & time' : date_time_published , 
            'agency' : agency , 
            'content' : body_content
        }




        

        











        





    