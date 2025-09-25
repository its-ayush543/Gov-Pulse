# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass





import scrapy


class NewsArticle(scrapy.Item):
    # Core article information
    url = scrapy.Field()
    headline = scrapy.Field()
    content = scrapy.Field()
    summary = scrapy.Field()
    
    # Publication details
    author = scrapy.Field()
    date_published = scrapy.Field()
    date_machine = scrapy.Field()  # Machine-readable date format
    
    # Media and metadata
    image_url = scrapy.Field()
    keywords = scrapy.Field()
    tags = scrapy.Field()
    
    # Categorization
    category = scrapy.Field()
    subcategory = scrapy.Field()
    source = scrapy.Field()
    
    # Additional metadata
    scraped_at = scrapy.Field()  # Timestamp when scraped
    word_count = scrapy.Field()  # Content word count
    read_time = scrapy.Field()   # Estimated reading time



