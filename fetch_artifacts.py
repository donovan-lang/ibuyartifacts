"""
Fetch 20 real artifact records from the Met Museum Open Access API (CC0 public domain).
Uses urllib.request only -- no external dependencies.
Also fetches YouTube video data for Harold Carver books.
"""

import json
import time
import urllib.request
import urllib.parse
import os

SEARCH_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects"
TIMEOUT = 10
DELAY = 0.2

CATEGORIES = {
    "Egyptian": [
        "egyptian scarab",
        "egyptian amulet",
        "canopic jar",
        "ushabti",
    ],
    "Roman": [
        "roman coin",
        "roman glass vessel",
        "roman bronze",
        "roman oil lamp",
    ],
    "Greek": [
        "greek amphora",
        "greek helmet bronze",
        "terracotta figurine greek",
        "greek kylix",
    ],
    "Mesopotamian": [
        "cylinder seal mesopotamia",
        "cuneiform tablet",
        "sumerian bronze",
    ],
    "Asian": [
        "tang dynasty horse",
        "jade bi disc",
        "shang bronze vessel",
    ],
    "Pre-Columbian": [
        "maya ceramic vessel",
        "moche portrait vessel",
    ],
}

# YouTube API Configuration
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
YOUTUBE_CHANNEL_ID = "UC_x5XG1OV2P6uZZ5FSM9Ttwg"  # Harold Carver channel ID (placeholder)
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"


def fetch_json(url):
    """Fetch JSON from a URL with timeout."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_objects(query):
    """Search the Met API for public-domain objects with images."""
    params = urllib.parse.urlencode({
        "isPublicDomain": "true",
        "hasImages": "true",
        "q": query,
        "limit": 5,
    })
    url = f"{SEARCH_URL}?{params}"
    try:
        data = fetch_json(url)
        return data.get("objectIDs", [])
    except Exception as e:
        print(f"Error searching for '{query}': {e}")
        return []


def get_object_details(object_id):
    """Fetch full details for a single object."""
    url = f"{OBJECT_URL}/{object_id}"
    try:
        return fetch_json(url)
    except Exception as e:
        print(f"Error fetching object {object_id}: {e}")
        return None


def fetch_artifacts():
    """Fetch artifacts from Met API."""
    artifacts = []
    for category, queries in CATEGORIES.items():
        for query in queries:
            object_ids = search_objects(query)
            for oid in object_ids[:2]:  # Limit to 2 per query
                obj = get_object_details(oid)
                if obj:
                    artifacts.append({
                        "title": obj.get("title", "Unknown"),
                        "category": category,
                        "object_number": obj.get("objectNumber", ""),
                        "accession_number": obj.get("accessionNumber", ""),
                        "image_url": obj.get("primaryImage", {}).get("jpg", {}).get("fullsize"),
                        "description": obj.get("objectDescription", "")
                    })
            time.sleep(DELAY)
    return artifacts


def fetch_youtube_books_data():
    """
    Fetch YouTube videos related to Harold Carver books.
    Returns a list of video objects with title, video_id, and book_slug mapping.
    """
    if not YOUTUBE_API_KEY:
        print("Warning: YOUTUBE_API_KEY not set. Skipping YouTube fetch.")
        return []

    videos = []
    book_slugs = [
        "dead_sea_scrolls",
        "punic_wars",
        "epic_of_gilgamesh",
        "gobekli_tepe_v1",
        "gobekli_tepe_v2",
        "sumer",
        "book_of_enoch"
    ]

    # Search for videos by Harold Carver related to books
    search_params = urllib.parse.urlencode({
        "part": "snippet",
        "channelId": YOUTUBE_CHANNEL_ID,
        "key": YOUTUBE_API_KEY,
        "maxResults": 50,
        "order": "date"
    })
    search_url = f"{YOUTUBE_API_URL}/search?{search_params}"

    try:
        search_data = fetch_json(search_url)
        video_ids = [item["id"]["videoId"] for item in search_data.get("items", []) 
                     if item["id"]["kind"] == "youtube#video"]

        # Get detailed info for each video
        if video_ids:
            details_params = urllib.parse.urlencode({
                "part": "snippet,contentDetails",
                "id": ",".join(video_ids[:10]),  # Limit to 10 videos
                "key": YOUTUBE_API_KEY
            })
            details_url = f"{YOUTUBE_API_URL}/videos?{details_params}"
            details_data = fetch_json(details_url)

            for item in details_data.get("items", []):
                snippet = item.get("snippet", {})
                title = snippet.get("title", "")
                video_id = item.get("id", "")
                
                # Try to map video to book slug based on title keywords
                matched_slug = None
                for slug in book_slugs:
                    if slug.replace("_", " ").lower() in title.lower():
                        matched_slug = slug
                        break
                
                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "book_slug": matched_slug,
                    "published_at": snippet.get("publishedAt", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
                })
                time.sleep(DELAY)
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")

    return videos


def update_books_with_youtube():
    """Update books_data.json with YouTube video links."""
    try:
        with open("books_data.json", "r") as f:
            books = json.load(f)
    except FileNotFoundError:
        print("books_data.json not found.")
        return

    youtube_videos = fetch_youtube_books_data()
    
    # Create a mapping of book_slug to video data
    video_map = {}
    for video in youtube_videos:
        if video["book_slug"]:
            if video["book_slug"] not in video_map:
                video_map[video["book_slug"]] = []
            video_map[video["book_slug"]].append(video)

    # Update books with YouTube links
    updated = False
    for book in books:
        slug = book.get("slug")
        if slug and slug in video_map:
            book["youtube_videos"] = video_map[slug]
            updated = True

    if updated:
        with open("books_data.json", "w") as f:
            json.dump(books, f, indent=2)
        print(f"Updated {len(video_map)} books with YouTube video links.")
    else:
        print("No books updated with YouTube links.")


if __name__ == "__main__":
    # Fetch artifacts
    artifacts = fetch_artifacts()
    print(f"Fetched {len(artifacts)} artifacts from Met API.")
    
    # Update books with YouTube data
    update_books_with_youtube()
    
    # Save artifacts
    with open("artifacts_data.json", "w") as f:
        json.dump(artifacts, f, indent=2)
    print("Saved artifacts to artifacts_data.json")