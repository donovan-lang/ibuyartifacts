#!/usr/bin/env python3
"""
fetch_artifacts.py - Fetch content for iBuyArtifacts platform
Handles KDP books and YouTube videos for Harold Carver hub
"""

import json
import os
import requests
from typing import List, Dict, Any
from datetime import datetime

# Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = 'UCxK8bQvZ9f3J2mN4pL6rT8w'  # Harold Carver channel ID - update with actual ID
OUTPUT_FILE = 'artifacts_data.json'
BOOKS_FILE = 'books_data.json'

def fetch_json(url: str, params: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Fetch JSON data from a URL with optional query parameters
    
    Args:
        url: The base URL to fetch from
        params: Optional query parameters as a dictionary
        
    Returns:
        Parsed JSON response as dictionary
    """
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from {url}: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {url}: {e}")
        return {}

def fetch_youtube_books_data() -> List[Dict[str, Any]]:
    """
    Query YouTube Data API for Harold Carver channel videos
    
    Returns:
        List of video dictionaries with title, link, thumbnail, etc.
    """
    if not YOUTUBE_API_KEY:
        print("Warning: YOUTUBE_API_KEY not set. Skipping YouTube fetch.")
        return []
    
    youtube_videos = []
    page_token = None
    
    # Fetch videos from Harold Carver channel
    while True:
        params = {
            'part': 'snippet,statistics',
            'channelId': CHANNEL_ID,
            'order': 'date',
            'maxResults': 50,
            'key': YOUTUBE_API_KEY
        }
        
        if page_token:
            params['pageToken'] = page_token
        
        url = 'https://www.googleapis.com/youtube/v3/search'
        response = fetch_json(url, params)
        
        if not response or 'items' not in response:
            break
        
        # Process each video item
        for item in response.get('items', []):
            video_type = item.get('id', {}).get('kind')
            
            # Only process video items (not playlists or channels)
            if video_type != 'youtube#video':
                continue
            
            video_id = item.get('id', {}).get('videoId')
            snippet = item.get('snippet', {})
            
            # Fetch detailed video info for statistics
            video_detail_url = 'https://www.googleapis.com/youtube/v3/videos'
            video_detail_params = {
                'part': 'statistics',
                'id': video_id,
                'key': YOUTUBE_API_KEY
            }
            video_detail = fetch_json(video_detail_url, video_detail_params)
            
            statistics = video_detail.get('items', [{}])[0].get('statistics', {})
            
            video_data = {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'video_link': f'https://www.youtube.com/watch?v={video_id}',
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'source': 'youtube'
            }
            
            youtube_videos.append(video_data)
        
        # Check if there are more pages
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    
    return youtube_videos

def fetch_kdp_books_data() -> List[Dict[str, Any]]:
    """
    Load KDP books data from books_data.json
    
    Returns:
        List of book dictionaries
    """
    try:
        with open(BOOKS_FILE, 'r') as f:
            books = json.load(f)
        return books
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading books data: {e}")
        return []

def merge_artifacts(books: List[Dict], videos: List[Dict]) -> List[Dict]:
    """
    Merge books and videos into a single artifacts list
    
    Args:
        books: List of book dictionaries
        videos: List of video dictionaries
        
    Returns:
        Combined list with all artifacts
    """
    artifacts = []
    
    # Add books with source tag
    for book in books:
        book['source'] = 'kdp'
        artifacts.append(book)
    
    # Add videos with source tag
    for video in videos:
        artifacts.append(video)
    
    # Sort by date (published_at or created_at)
    artifacts.sort(key=lambda x: x.get('published_at', x.get('created_at', '')), reverse=True)
    
    return artifacts

def save_artifacts(artifacts: List[Dict], filename: str = OUTPUT_FILE):
    """
    Save artifacts to JSON file
    
    Args:
        artifacts: List of artifact dictionaries
        filename: Output filename
    """
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'total_count': len(artifacts),
        'books_count': len([a for a in artifacts if a.get('source') == 'kdp']),
        'videos_count': len([a for a in artifacts if a.get('source') == 'youtube']),
        'artifacts': artifacts
    }
    
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Saved {len(artifacts)} artifacts to {filename}")

def main():
    """
    Main function to fetch and merge all content
    """
    print("Starting iBuyArtifacts content fetch...")
    
    # Fetch KDP books
    print("Fetching KDP books...")
    books = fetch_kdp_books_data()
    print(f"Found {len(books)} books")
    
    # Fetch YouTube videos
    print("Fetching YouTube videos...")
    videos = fetch_youtube_books_data()
    print(f"Found {len(videos)} videos")
    
    # Merge all artifacts
    print("Merging artifacts...")
    all_artifacts = merge_artifacts(books, videos)
    
    # Save to output file
    save_artifacts(all_artifacts)
    
    print("Content fetch complete!")

if __name__ == '__main__':
    main()
