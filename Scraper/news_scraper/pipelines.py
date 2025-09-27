# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
import logging
import hashlib
from datetime import datetime
from scrapy.exceptions import DropItem
from w3lib.html import remove_tags
from urllib.parse import urljoin, urlparse

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class NewsScraperPipeline:
    def process_item(self, item, spider):
        return item









class NewsArticleBasePipeline:
    """Base pipeline with common logging and utility functions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_item(self, item, spider):
        return item










class NewsArticleValidationPipeline(NewsArticleBasePipeline):
    """Validate incoming items and drop invalid ones"""
    
    def process_item(self, item, spider):
        # Validate required fields
        if not item.get('headline'):
            raise DropItem(f"Missing headline in {item.get('url', 'unknown URL')}")
        
        if not item.get('content') and not item.get('summary'):
            raise DropItem(f"Missing both content and summary in {item.get('url', 'unknown URL')}")
        
        # Ensure URL exists and is valid
        if not item.get('url'):
            raise DropItem("Missing URL in item")
        
        # Validate URL format
        try:
            parsed_url = urlparse(item['url'])
            if not parsed_url.scheme or not parsed_url.netloc:
                raise DropItem(f"Invalid URL format: {item['url']}")
        except Exception as e:
            raise DropItem(f"URL validation error: {e}")
        
        # Validate headline length (reasonable limits)
        if len(item['headline']) > 500:
            self.logger.warning(f"Very long headline ({len(item['headline'])} chars) in {item['url']}")
        
        # Validate content length
        if item.get('content') and len(item['content']) < 30:
            self.logger.warning(f"Very short content ({len(item['content'])} chars) in {item['url']}")
        
        return item












class NewsArticleCleaningPipeline(NewsArticleBasePipeline):
    """Clean and normalize article content"""
    
    def process_item(self, item, spider):
        # Clean headline
        if item.get('headline'):
            item['headline'] = self._clean_headline(item['headline'], item.get('source', ''))
        
        # Clean content
        if item.get('content'):
            # Handle Times of India content which is stored as list
            if isinstance(item['content'], list):
                item['content'] = ' '.join([str(p).strip() for p in item['content'] if str(p).strip()])
            item['content'] = self._clean_content(item['content'])
        
        # Clean summary
        if item.get('summary'):
            item['summary'] = self._clean_summary(item['summary'])
            
        # Clean author field
        if item.get('author'):
            item['author'] = self._clean_author(item['author'])
        
        # Clean keywords
        if item.get('keywords'):
            item['keywords'] = self._clean_keywords(item['keywords'])
        
        # Clean image URL
        if item.get('image_url'):
            item['image_url'] = self._clean_image_url(item['image_url'])
        
        return item
    
    def _clean_headline(self, headline, source):
        """Clean headlines by removing source names and standardizing format"""
        if not headline:
            return ""
            
        # Convert to string if not already
        headline = str(headline).strip()
        
        # Remove HTML tags if any
        headline = remove_tags(headline)
        
        # Remove source name from headline
        source_patterns = {
            'NDTV': [r'\s*[-|]\s*NDTV\s*$', r'\s*[-|]\s*NDTV\.com\s*$'],
            'Telegraph India': [r'\s*[-|]\s*Telegraph India\s*$', r'\s*[-|]\s*The Telegraph\s*$'],
            'Indian Express': [r'\s*[-|]\s*The Indian Express\s*$', r'\s*\|\s*Express\s*$', r'\s*[-|]\s*Indian Express\s*$'],
            'Times of India': [r'\s*[-|]\s*Times of India\s*$', r'\s*[-|]\s*TOI\s*$', r'\s*[-|]\s*The Times of India\s*$']
        }
        
        if source in source_patterns:
            for pattern in source_patterns[source]:
                headline = re.sub(pattern, '', headline, flags=re.IGNORECASE)
        
        # Remove extra whitespace and normalize
        headline = re.sub(r'\s+', ' ', headline).strip()
        
        # Fix capitalization if headline is ALL CAPS
        if headline.isupper() and len(headline) > 10:
            headline = headline.title()
        
        # Remove quotes if they wrap the entire headline
        if headline.startswith('"') and headline.endswith('"'):
            headline = headline[1:-1]
        if headline.startswith("'") and headline.endswith("'"):
            headline = headline[1:-1]
        
        return headline.strip()
    
    def _clean_content(self, content):
        """Clean article content"""
        if not content:
            return ""
            
        # Convert to string if not already
        content = str(content)
        
        # Remove any HTML tags that might be present
        content = remove_tags(content)
        
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Remove common footer phrases (case insensitive)
        footer_patterns = [
            r'(?i)follow us on.*$',
            r'(?i)for all the latest.*news.*$',
            r'(?i)download the.*app.*$',
            r'(?i)click here to.*$',
            r'(?i)subscribe to our newsletter.*$',
            r'(?i)follow our.*channel.*$',
            r'(?i)for more news.*visit.*$',
            r'(?i)copyright ©.*$',
            r'(?i)share this article.*$',
            r'(?i)tags:.*$',
            r'(?i)also read:.*$',
            r'(?i)read more:.*$',
            r'(?i)get the latest.*updates.*$',
            r'(?i)stay updated.*$'
        ]
        
        for pattern in footer_patterns:
            content = re.sub(pattern, '', content)
        
        # Remove URLs
        content = re.sub(r'https?://\S+', '', content)
        
        # Remove email addresses
        content = re.sub(r'\S+@\S+\.\S+', '', content)
        
        # Remove excessive punctuation
        content = re.sub(r'[.]{3,}', '...', content)
        content = re.sub(r'[!]{2,}', '!', content)
        content = re.sub(r'[?]{2,}', '?', content)
        
        # Final whitespace cleanup
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def _clean_summary(self, summary):
        """Clean article summary"""
        if not summary:
            return ""
            
        # Convert to string
        summary = str(summary).strip()
        
        # Remove any HTML tags
        summary = remove_tags(summary)
        
        # Normalize whitespace
        summary = re.sub(r'\s+', ' ', summary).strip()
        
        # Remove phrases like "Read full article here" or "Click to read more"
        summary = re.sub(r'(?i)read (full|more|article).*$', '', summary)
        summary = re.sub(r'(?i)click (here|to).*$', '', summary)
        summary = re.sub(r'(?i)continue reading.*$', '', summary)
        
        return summary.strip()
    
    def _clean_author(self, author):
        """Clean author field"""
        if not author:
            return ""
        
        # Convert to string
        author = str(author).strip()
        
        # Remove HTML tags
        author = remove_tags(author)
        
        # Remove prefixes like "By" or "Written by" - fix regex patterns
        author = re.sub(r'(?i)^by\s+', '', author)
        author = re.sub(r'(?i)^written by\s+', '', author)
        author = re.sub(r'(?i)^reported by\s+', '', author)
        author = re.sub(r'(?i)^with inputs from\s+', '', author)
        
        # Remove suffixes like "| Staff Reporter" or similar
        author = re.sub(r'(?i)\|\s*staff.*$', '', author)
        author = re.sub(r'(?i)\|\s*correspondent.*$', '', author)
        
        # Clean up multiple authors separated by commas or 'and'
        author = re.sub(r'\s+and\s+', ', ', author)
        
        return author.strip()
    
    def _clean_keywords(self, keywords):
        """Clean keywords field"""
        if not keywords:
            return ""
        
        # Convert to string
        keywords = str(keywords).strip()
        
        # Remove HTML tags
        keywords = remove_tags(keywords)
        
        # Normalize whitespace
        keywords = re.sub(r'\s+', ' ', keywords).strip()
        
        return keywords
    
    def _clean_image_url(self, image_url):
        """Clean and validate image URL"""
        if not image_url:
            return ""
        
        # Convert to string and strip
        image_url = str(image_url).strip()
        
        # Remove any surrounding quotes
        image_url = image_url.strip('\'"')
        
        # Validate URL format
        try:
            parsed = urlparse(image_url)
            if not parsed.scheme:
                # If no scheme, assume https
                image_url = 'https:' + image_url if image_url.startswith('//') else 'https://' + image_url
        except:
            return ""
        
        return image_url














class NewsArticleEnrichmentPipeline(NewsArticleBasePipeline):
    """Enrich articles with additional data"""
    
    def process_item(self, item, spider):
        # Add timestamp when scraped if not present
        if 'scraped_at' not in item or not item['scraped_at']:
            item['scraped_at'] = datetime.now().isoformat()
        
        # Calculate word count
        content = item.get('content', '')
        if content:
            item['word_count'] = len(str(content).split())
            
            # Calculate estimated reading time (avg 200 words per minute)
            item['read_time'] = max(1, round(item['word_count'] / 200))
        else:
            item['word_count'] = 0
            item['read_time'] = 0
        
        # Process date fields
        if item.get('date_published') and ('date_machine' not in item or not item['date_machine']):
            item['date_machine'] = self._standardize_date(item['date_published'])
        
        # Ensure tags is a list
        if 'tags' not in item:
            item['tags'] = []
        elif item['tags'] and not isinstance(item['tags'], list):
            if isinstance(item['tags'], str):
                # Convert comma-separated string to list
                item['tags'] = [tag.strip() for tag in item['tags'].split(',') if tag.strip()]
            else:
                # Convert to list if it's some other type
                item['tags'] = [str(item['tags'])]
        
        # Extract keywords as tags if no tags present
        if (not item['tags']) and item.get('keywords'):
            if isinstance(item['keywords'], str):
                keywords = [kw.strip() for kw in item['keywords'].split(',') if kw.strip()]
                item['tags'] = keywords[:10]  # Limit to 10 tags
        
        # Ensure all string fields are properly set
        string_fields = ['headline', 'content', 'summary', 'author', 'date_published', 
                        'date_machine', 'keywords', 'image_url', 'category', 'subcategory', 'source']
        
        for field in string_fields:
            if field not in item or item[field] is None:
                item[field] = ""
            else:
                item[field] = str(item[field]).strip()
        
        return item
    
    def _standardize_date(self, date_str):
        """Convert various date formats to ISO format when possible"""
        if not date_str:
            return ""
            
        date_str = str(date_str).strip()
        
        # Already in ISO format
        if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', date_str):
            return date_str
        
        # Common date formats
        date_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%d %b %Y, %H:%M',
            '%B %d, %Y %H:%M',
            '%d %B %Y, %H:%M:%S',
            '%d %b %Y %H:%M:%S',
            '%A %B %d %Y',
            '%a, %b %d, %Y',
            '%Y/%m/%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d %b %Y',
            '%B %d, %Y'
        ]
        
        # Try each format
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        # Try to extract date with regex if standard formats fail
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
            r'(\d{2}/\d{2}/\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{1,2}\s+\w+\s+\d{4})',  # D Month YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    date_part = match.group(1)
                    # Try to parse the extracted date
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d %B %Y', '%d %b %Y']:
                        try:
                            dt = datetime.strptime(date_part, fmt)
                            return dt.isoformat()
                        except ValueError:
                            continue
                except:
                    continue
        
        # Return original if no format matches
        return date_str





















class NewsArticleDeduplicationPipeline(NewsArticleBasePipeline):
    """Deduplicate articles based on URL and content similarity"""
    
    def __init__(self):
        super().__init__()
        self.urls_seen = set()
        self.content_hashes = set()
    
    def process_item(self, item, spider):
        # Check URL duplication
        url = item.get('url', '')
        if url in self.urls_seen:
            raise DropItem(f"Duplicate URL: {url}")
        
        # Create content hash for similarity detection
        content_for_hash = f"{item.get('headline', '')}{item.get('content', '')[:500]}"
        content_hash = hashlib.md5(content_for_hash.encode('utf-8')).hexdigest()
        
        if content_hash in self.content_hashes:
            raise DropItem(f"Duplicate content detected for: {url}")
        
        # Add to seen items
        self.urls_seen.add(url)
        self.content_hashes.add(content_hash)
        
        return item

















class NewsArticleQualityPipeline(NewsArticleBasePipeline):
    """Filter articles based on quality metrics"""
    
    def process_item(self, item, spider):
        # Quality checks
        headline = item.get('headline', '')
        content = item.get('content', '')
        
        # Skip articles with very short headlines
        if len(headline) < 10:
            raise DropItem(f"Headline too short ({len(headline)} chars): {item.get('url')}")
        
        # Skip articles with very short content (unless they have a good summary)
        if len(content) < 100 and len(item.get('summary', '')) < 50:
            raise DropItem(f"Content too short ({len(content)} chars): {item.get('url')}")
        
        # Skip articles that look like error pages
        error_indicators = ['404', 'not found', 'page not found', 'error', 'access denied']
        headline_lower = headline.lower()
        if any(indicator in headline_lower for indicator in error_indicators):
            raise DropItem(f"Looks like error page: {headline}")
        
        # Skip articles with suspicious content
        if 'javascript:void(0)' in content or len(content.split()) < 20:
            raise DropItem(f"Suspicious or too short content: {item.get('url')}")
        
        return item

















class NewsArticleExportPipeline(NewsArticleBasePipeline):
    """Final processing before export - ensures all fields exist with proper defaults"""
    
    def process_item(self, item, spider):
        # Define default values for all fields
        field_defaults = {
            'url': '',
            'headline': '',
            'content': '',
            'summary': '',
            'author': '',
            'date_published': '',
            'date_machine': '',
            'image_url': '',
            'keywords': '',
            'tags': [],
            'category': '',
            'subcategory': '',
            'source': '',
            'scraped_at': datetime.now().isoformat(),
            'word_count': 0,
            'read_time': 0
        }
        
        # Ensure all fields are present with proper defaults
        for field, default_value in field_defaults.items():
            if field not in item or item[field] is None:
                item[field] = default_value
        
        # Final validation - ensure essential fields are not empty
        if not item['url'] or not item['headline']:
            raise DropItem(f"Missing essential fields after processing: {item}")
        
        # Log successful processing
        self.logger.info(f"Successfully processed article: {item['headline'][:50]}...")
        
        return item