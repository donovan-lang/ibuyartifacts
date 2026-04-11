#!/usr/bin/env python3
"""
fetch_artifacts.py - Fetch content for iBuyArtifacts platform
Handles KDP books and YouTube videos for Harold Carver hub

YouTube data update modes:
  - Default (deploy): reads from local youtube_data.json (no API calls)
  - FORCE_UPDATE=true: fetches fresh data from YouTube API and updates youtube_data.json
    Use this in scheduled jobs (GitHub Actions cron) to keep data current.

Graceful degradation: when YouTube API quota is exhausted, falls back
to cached/static youtube_data.json so the pipeline proceeds.
"""

import json
import os
import sys
import requests
from typing import List, Dict, Any
from datetime import datetime

# Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
FORCE_UPDATE = os.getenv('FORCE_UPDATE', '').lower() == 'true'
CHANNEL_ID = 'UCxK8bQvZ9f3J2mN4pL6rT8w'  # Harold Carver channel ID - update with actual ID
OUTPUT_FILE = 'artifacts_data.json'
BOOKS_FILE = 'books_data.json'
YOUTUBE_DATA_FILE = 'youtube_data.json'

# Static fallback data — used when no cached file exists and API is unavailable
FALLBACK_VIDEOS = [
    {
        "videoId": "xn2I-lF9LHU",
        "title": "Oda Nobunaga: Japan's Revolutionary Warlord | History Unveiled",
        "thumbnail": "https://i9.ytimg.com/vi/xn2I-lF9LHU/hqdefault.jpg",
        "publishedAt": "2026-04-04T15:03:28Z",
        "description": "Dive into the life of Oda Nobunaga, the revolutionary warlord who reshaped 16th-century Japan."
    },
    {
        "videoId": "kL17PPSLAMc",
        "title": "The Peasants' Revolt: England's Forgotten Uprising",
        "thumbnail": "https://i9.ytimg.com/vi/kL17PPSLAMc/hqdefault.jpg",
        "publishedAt": "2026-04-04T15:02:42Z",
        "description": "The dramatic story of the 1381 Peasants' Revolt, when common people challenged the monarchy."
    },
    {
        "videoId": "umLHUHzXTSk",
        "title": "The Peasants' Revolt: England's Forgotten Uprising",
        "thumbnail": "https://i9.ytimg.com/vi/umLHUHzXTSk/hqdefault.jpg",
        "publishedAt": "2026-04-04T15:02:19Z",
        "description": "Uncover the pivotal moment in English history when common people challenged the monarchy."
    },
    {
        "videoId": "wLFGAxmzots",
        "title": "Greek Fire: The Ancient Superweapon That Saved an Empire",
        "thumbnail": "https://i9.ytimg.com/vi/wLFGAxmzots/hqdefault.jpg",
        "publishedAt": "2026-04-04T15:01:38Z",
        "description": "Discover the mysterious Greek Fire, Byzantium's most devastating weapon."
    }
]


class YouTubeQuotaExceeded(Exception):
    """Raised when YouTube API returns a quota-exceeded error."""
    pass


def fetch_json(url: str, params: Dict[str, str] = None) -> Dict[str, Any]:
    """Fetch JSON from a URL. Raises YouTubeQuotaExceeded on 403 quota errors."""
    try:
        response = requests.get(url, params=params, timeout=30)

        # Detect quota / rate-limit errors before raise_for_status
        if response.status_code == 403:
            try:
                err_body = response.json()
            except (json.JSONDecodeError, ValueError):
                err_body = {}
            errors = err_body.get('error', {}).get('errors', [])
            quota_reasons = {'quotaExceeded', 'rateLimitExceeded', 'dailyLimitExceeded'}
            for err in errors:
                if err.get('reason') in quota_reasons:
                    raise YouTubeQuotaExceeded(
                        f"YouTube API quota exceeded: {err.get('reason')} — {err.get('message', '')}"
                    )

        response.raise_for_status()
        return response.json()
    except YouTubeQuotaExceeded:
        raise  # propagate without swallowing
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from {url}: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {url}: {e}")
        return {}


def load_cached_youtube_data() -> List[Dict[str, Any]]:
    """Load videos from the existing youtube_data.json cache, or return static fallback."""
    try:
        with open(YOUTUBE_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        videos = data if isinstance(data, list) else data.get('videos', [])
        if videos:
            print(f"  Loaded {len(videos)} videos from cached {YOUTUBE_DATA_FILE}")
            return videos
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    print(f"  No cache found — using {len(FALLBACK_VIDEOS)} static fallback videos")
    return FALLBACK_VIDEOS


def save_youtube_data(videos: List[Dict[str, Any]]):
    """Write youtube_data.json in the format the frontend expects."""
    with open(YOUTUBE_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump({"videos": videos}, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(videos)} videos to {YOUTUBE_DATA_FILE}")


def fetch_youtube_books_data() -> List[Dict[str, Any]]:
    """
    Query YouTube Data API for Harold Carver channel videos.
    On quota error: stops immediately and returns fallback data.
    """
    if not YOUTUBE_API_KEY:
        print("Warning: YOUTUBE_API_KEY not set. Using fallback YouTube data.")
        return load_cached_youtube_data()

    youtube_videos = []
    page_token = None

    try:
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

            for item in response.get('items', []):
                video_type = item.get('id', {}).get('kind')
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

            page_token = response.get('nextPageToken')
            if not page_token:
                break

    except YouTubeQuotaExceeded as e:
        print(f"\n⚠ WARNING: {e}")
        print("  Stopping API calls immediately — no retries.")
        if youtube_videos:
            print(f"  Keeping {len(youtube_videos)} videos fetched before quota hit.")
        else:
            print("  Falling back to cached/static YouTube data.")
            youtube_videos = load_cached_youtube_data()

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
    """Main function to fetch and merge all content."""
    print("Starting iBuyArtifacts content fetch...")

    # Fetch KDP books
    print("Fetching KDP books...")
    books = fetch_kdp_books_data()
    print(f"Found {len(books)} books")

    # YouTube videos: only hit the API when FORCE_UPDATE=true (scheduled job)
    # Otherwise, read from local youtube_data.json (fast, no API quota usage)
    if FORCE_UPDATE:
        print("FORCE_UPDATE=true — fetching fresh YouTube data from API...")
        videos = fetch_youtube_books_data()
        print(f"Fetched {len(videos)} videos from API")

        # Save youtube_data.json for the frontend
        frontend_videos = []
        for v in videos:
            frontend_videos.append({
                'videoId': v.get('video_id') or v.get('videoId', ''),
                'title': v.get('title', ''),
                'thumbnail': v.get('thumbnail', ''),
                'publishedAt': v.get('published_at') or v.get('publishedAt', ''),
                'description': v.get('description', '')
            })
        save_youtube_data(frontend_videos)
    else:
        print("Reading YouTube data from local youtube_data.json (set FORCE_UPDATE=true to refresh)...")
        videos = load_cached_youtube_data()
        print(f"Loaded {len(videos)} videos from cache")

    # Merge all artifacts
    print("Merging artifacts...")
    all_artifacts = merge_artifacts(books, videos)

    # Save to output file
    save_artifacts(all_artifacts)

    print("Content fetch complete!")
    sys.exit(0)

if __name__ == '__main__':
    main()
