"""
YouTube Video Spider for GovPulse
Scrapes government-related YouTube channels and analyzes sentiment
"""

import scrapy
from googleapiclient.discovery import build
from datetime import datetime
import re
import logging

# Optional imports for enhanced features
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_AVAILABLE = True
except ImportError:
    TRANSCRIPT_AVAILABLE = False
    
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class YouTubeGovernmentSpider(scrapy.Spider):
    name = "ytvideo-spider"
    
    # Government and news channels to monitor
    GOVERNMENT_CHANNELS = {
        'Times of India': 'UCckHqySbfy5FcPP6MD_S-Yg',
        # 'PIB_India': 'UCbRSja_FtHsvi1yghbgzGcQ',  # PIB India
        # 'DD_News': 'UCKwuchlWLjN_kL6WbVZ7Xkw',      # DD News
        # 'PMO_India': 'UCOm2JlkEcD24cw2KzNmKLww',   # PMO India
        # 'MyGovIndia': 'UCEqG1J5EEFQy7wXYPa7G9Ow',  # MyGov India
        # Add more channels as needed
    }
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 2,
        'ROBOTSTXT_OBEY': False
    }
    
    def __init__(self, youtube_api_key=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Use provided API key or fallback to hardcoded one
        self.youtube_api_key = youtube_api_key or "AIzaSyAhGA8gbyxXxH4hCXOO7muvKTyUB1jWev0"
        
        if not self.youtube_api_key:
            raise ValueError("YouTube API key required. Set YOUTUBE_API_KEY environment variable")
        
        # Initialize YouTube API client
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            self.logger.info("YouTube API client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube API: {e}")
            raise
        
        # Initialize sentiment analyzer if available
        self.sentiment_analyzer = None
        if TRANSFORMERS_AVAILABLE:
            try:
                self.logger.info("Loading sentiment analysis model...")
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1
                )
                self.logger.info("Sentiment analyzer loaded successfully")
            except Exception as e:
                self.logger.warning(f"Could not load sentiment analyzer: {e}")
        else:
            self.logger.warning("Transformers not available - sentiment analysis disabled")
    
    def start_requests(self):
        """Start scraping YouTube channels"""
        self.logger.info("Starting YouTube channel scraping...")
        for channel_name, channel_id in self.GOVERNMENT_CHANNELS.items():
            self.logger.info(f"Queuing channel: {channel_name}")
            yield scrapy.Request(
                url=f'https://www.youtube.com/channel/{channel_id}',
                callback=self.parse_channel,
                meta={
                    'channel_name': channel_name,
                    'channel_id': channel_id
                }
            )
    
    async def start(self):
        """Modern async start method for Scrapy 2.13+"""
        self.logger.info("Starting YouTube channel scraping (async)...")
        for channel_name, channel_id in self.GOVERNMENT_CHANNELS.items():
            self.logger.info(f"Queuing channel: {channel_name}")
            yield scrapy.Request(
                url=f'https://www.youtube.com/channel/{channel_id}',
                callback=self.parse_channel,
                meta={
                    'channel_name': channel_name,
                    'channel_id': channel_id
                }
            )
    
    def parse_channel(self, response):
        """Parse YouTube channel and get videos"""
        channel_id = response.meta['channel_id']
        channel_name = response.meta['channel_name']
        
        self.logger.info(f"Parsing channel: {channel_name} ({channel_id})")
        
        # Get latest videos from channel using YouTube API
        try:
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=50,  
                order='date',
                type='video'
            )
            response_data = request.execute()
            
            videos_found = len(response_data.get('items', []))
            self.logger.info(f"Found {videos_found} videos for channel {channel_name}")
            
            for item in response_data.get('items', []):
                video_id = item['id']['videoId']
                video_data = {
                    'video_id': video_id,
                    'channel_name': channel_name,
                    'channel_id': channel_id,
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url']
                }
                
                self.logger.info(f"Processing video: {video_data['title'][:50]}...")
                
                # Get full video details and analyze
                yield from self.analyze_video(video_data)
        
        except Exception as e:
            self.logger.error(f"Error fetching videos for {channel_name}: {e}")
            # Yield a dummy item to show the spider is working
            yield {
                'error': f"Could not fetch videos for {channel_name}: {str(e)}",
                'channel': channel_name,
                'channel_id': channel_id,
                'scraped_at': datetime.now().isoformat(),
                'source': 'youtube_error'
            }
    
    def analyze_video(self, video_data):
        """Analyze video sentiment from transcript"""
        video_id = video_data['video_id']
        
        # Start with basic video data
        basic_data = {
            'video_id': video_id,
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'channel': video_data['channel_name'],
            'title': video_data['title'],
            'headline': video_data['title'],  # Add headline for pipeline compatibility
            'description': video_data['description'][:500],  # Limit description length
            'content': video_data['description'][:1000],  # Add content field
            'published_at': video_data['published_at'],
            'thumbnail': video_data['thumbnail'],
            'ministry': self.classify_ministry(video_data['title'], video_data['description']),
            'scraped_at': datetime.now().isoformat(),
            'source': 'youtube',
            'language': 'english'
        }
        
        # Try to get video statistics
        try:
            stats = self.get_video_stats(video_id)
            basic_data.update(stats)
        except Exception as e:
            self.logger.warning(f"Could not get stats for {video_id}: {e}")
            basic_data.update({
                'views': 0,
                'likes': 0,
                'comments': 0,
                'duration': ''
            })
        
        # Try to get transcript and analyze sentiment
        transcript_text = ""
        sentiment = {'label': 'NEUTRAL', 'score': 0.0, 'reason': 'No analysis available'}
        
        if TRANSCRIPT_AVAILABLE:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=['en', 'hi']
                )
                transcript_text = ' '.join([entry['text'] for entry in transcript])
                
                # Analyze sentiment if transformer is available
                if self.sentiment_analyzer and transcript_text:
                    sentiment = self.analyze_sentiment(transcript_text)
                else:
                    # Simple keyword-based sentiment for fallback
                    sentiment = self.simple_sentiment_analysis(transcript_text)
                    
            except Exception as e:
                self.logger.info(f"Could not get transcript for {video_id}: {e}")
                # Use title and description for simple sentiment analysis
                text_for_analysis = f"{video_data['title']} {video_data['description']}"
                sentiment = self.simple_sentiment_analysis(text_for_analysis)
        
        # Add transcript and sentiment data
        basic_data.update({
            'transcript': transcript_text[:1000] if transcript_text else "",
            'transcript_length': len(transcript_text),
            'word_count': len(transcript_text.split()) if transcript_text else 0,
            'sentiment': sentiment
        })
        
        yield basic_data
    
    def get_video_stats(self, video_id):
        """Get video statistics using YouTube API"""
        try:
            request = self.youtube.videos().list(
                part='statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                stats = response['items'][0]['statistics']
                duration = response['items'][0]['contentDetails']['duration']
                return {
                    'viewCount': int(stats.get('viewCount', 0)),
                    'likeCount': int(stats.get('likeCount', 0)),
                    'commentCount': int(stats.get('commentCount', 0)),
                    'duration': duration
                }
        except Exception as e:
            self.logger.error(f"Error getting stats for {video_id}: {e}")
        
        return {}
    
    def simple_sentiment_analysis(self, text):
        """Simple keyword-based sentiment analysis as fallback"""
        if not text:
            return {'label': 'NEUTRAL', 'score': 0.0, 'method': 'keyword_fallback'}
        
        text_lower = text.lower()
        
        # Define positive and negative keywords
        positive_words = [
            'good', 'great', 'excellent', 'success', 'achieve', 'progress', 'improve',
            'benefit', 'positive', 'development', 'growth', 'innovation', 'welfare',
            'prosperity', 'advance', 'reform', 'modernize', 'digital', 'scheme'
        ]
        
        negative_words = [
            'bad', 'poor', 'crisis', 'problem', 'issue', 'concern', 'challenge',
            'corruption', 'fraud', 'scam', 'delay', 'failure', 'decline', 'protest',
            'violence', 'conflict', 'poverty', 'unemployment', 'inflation'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {
                'label': 'POSITIVE',
                'score': min(0.9, 0.5 + (positive_count - negative_count) * 0.1),
                'method': 'keyword_fallback',
                'positive_keywords': positive_count,
                'negative_keywords': negative_count
            }
        elif negative_count > positive_count:
            return {
                'label': 'NEGATIVE',
                'score': min(0.9, 0.5 + (negative_count - positive_count) * 0.1),
                'method': 'keyword_fallback',
                'positive_keywords': positive_count,
                'negative_keywords': negative_count
            }
        else:
            return {
                'label': 'NEUTRAL',
                'score': 0.5,
                'method': 'keyword_fallback',
                'positive_keywords': positive_count,
                'negative_keywords': negative_count
            }
    
    def analyze_sentiment(self, text, chunk_size=512):
        """Analyze sentiment of text"""
        if not text or len(text.strip()) == 0:
            return {'label': 'NEUTRAL', 'score': 0.0}
        
        # Split into chunks
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            current_length += len(word) + 1
            if current_length > chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Analyze each chunk
        results = []
        for chunk in chunks[:10]:  # Limit to 10 chunks
            try:
                result = self.sentiment_analyzer(chunk[:512])[0]
                results.append(result)
            except:
                continue
        
        if not results:
            return {'label': 'NEUTRAL', 'score': 0.0}
        
        # Aggregate
        positive = sum(1 for r in results if r['label'] == 'POSITIVE')
        negative = sum(1 for r in results if r['label'] == 'NEGATIVE')
        avg_score = sum(r['score'] for r in results) / len(results)
        
        overall = 'POSITIVE' if positive > negative else ('NEGATIVE' if negative > positive else 'NEUTRAL')
        
        return {
            'label': overall,
            'score': round(avg_score, 3),
            'positive_segments': positive,
            'negative_segments': negative,
            'total_segments': len(results)
        }
    
    def classify_ministry(self, title, description):
        """Classify video to relevant ministry/department"""
        text = (title + ' ' + description).lower()
        
        ministry_keywords = {
            'Health': ['health', 'medical', 'hospital', 'doctor', 'covid', 'vaccine', 'ayushman'],
            'Education': ['education', 'school', 'university', 'student', 'teacher', 'exam'],
            'Finance': ['budget', 'tax', 'economy', 'finance', 'gst', 'banking'],
            'Railways': ['railway', 'train', 'rail', 'station', 'metro'],
            'Defence': ['defence', 'army', 'navy', 'air force', 'military', 'soldier'],
            'Agriculture': ['farmer', 'agriculture', 'crop', 'farming', 'kisan'],
            'Home Affairs': ['police', 'security', 'law', 'order', 'crime'],
            'External Affairs': ['foreign', 'international', 'diplomacy', 'embassy'],
            'IT': ['digital', 'technology', 'internet', 'cyber', 'ai', 'startup'],
            'Environment': ['environment', 'climate', 'pollution', 'forest', 'green']
        }
        
        for ministry, keywords in ministry_keywords.items():
            if any(keyword in text for keyword in keywords):
                return ministry
        
        return 'General'


# Quick usage script
if __name__ == "__main__":
    """
    Quick setup:
    1. pip install youtube-transcript-api google-api-python-client transformers torch
    2. Get YouTube API key from https://console.cloud.google.com/
    3. Set environment variable: export YOUTUBE_API_KEY="your_key_here"
    4. Run: scrapy crawl youtube-government-spider -o youtube_analysis.json
    """
    pass



