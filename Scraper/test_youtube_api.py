#!/usr/bin/env python3

from googleapiclient.discovery import build

def test_youtube_api():
    api_key = "AIzaSyAhGA8gbyxXxH4hCXOO7muvKTyUB1jWev0"
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Test with some known working channels (including government ones)
    channels = {
        'PIB_India': 'UCbRSja_FtHsvi1yghbgzGcQ',  # Original
        'DD_News': 'UCKwuchlWLjN_kL6WbVZ7Xkw',     # Original
        'PMO_India': 'UCOm2JlkEcD24cw2KzNmKLww',   # Original
        'MyGovIndia': 'UCEqG1J5EEFQy7wXYPa7G9Ow',  # Original
        # Let's also try some known working channels for testing
        'Test_Channel': 'UC_x5XG1OV2P6uZZ5FSM9Ttw',  # Google Developers
    }
    
    for channel_name, channel_id in channels.items():
        print(f"\n=== Testing {channel_name} ({channel_id}) ===")
        
        try:
            # Test 1: Get channel details
            channel_request = youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            )
            channel_response = channel_request.execute()
            
            print(f"API Response: {channel_response}")
            
            if 'items' in channel_response and channel_response['items']:
                channel_info = channel_response['items'][0]
                print(f"Channel Title: {channel_info['snippet']['title']}")
                print(f"Subscriber Count: {channel_info['statistics'].get('subscriberCount', 'Hidden')}")
                print(f"Video Count: {channel_info['statistics'].get('videoCount', 'Unknown')}")
                
                # Test 2: Search for recent videos
                search_request = youtube.search().list(
                    part='snippet',
                    channelId=channel_id,
                    maxResults=5,
                    order='date',
                    type='video'
                )
                search_response = search_request.execute()
                
                videos_found = len(search_response.get('items', []))
                print(f"Recent videos found: {videos_found}")
                
                for item in search_response.get('items', []):
                    print(f"  - {item['snippet']['title'][:60]}...")
                    print(f"    Published: {item['snippet']['publishedAt']}")
            else:
                print("Channel not found or no data returned!")
                
        except Exception as e:
            print(f"Error testing {channel_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_youtube_api()