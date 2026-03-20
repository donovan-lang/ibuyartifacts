"""
Fetch 20 real artifact records from the Met Museum Open Access API (CC0 public domain).
Uses urllib.request only -- no external dependencies.
"""

import json
import time
import urllib.request
import urllib.parse
import sys

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
    })
    url = f"{SEARCH_URL}?{params}"
    data = fetch_json(url)
    return data.get("objectIDs") or []


def fetch_object(object_id):
    """Fetch full object details by ID."""
    url = f"{OBJECT_URL}/{object_id}"
    return fetch_json(url)


def main():
    results = []
    seen_ids = set()
    total_expected = sum(len(v) for v in CATEGORIES.values())
    count = 0

    for category, queries in CATEGORIES.items():
        for query in queries:
            count += 1
            print(f"[{count}/{total_expected}] {category} -- searching: \"{query}\" ... ", end="", flush=True)

            try:
                object_ids = search_objects(query)
                time.sleep(DELAY)
            except Exception as e:
                print(f"SEARCH FAILED: {e}")
                continue

            if not object_ids:
                print("no results")
                continue

            # Pick the first ID we haven't already used
            chosen_id = None
            for oid in object_ids:
                if oid not in seen_ids:
                    chosen_id = oid
                    break
            if chosen_id is None:
                print("all results already used")
                continue

            try:
                obj = fetch_object(chosen_id)
                time.sleep(DELAY)
            except Exception as e:
                print(f"OBJECT FETCH FAILED (id={chosen_id}): {e}")
                continue

            seen_ids.add(chosen_id)

            record = {
                "objectID": chosen_id,
                "category": category,
                "searchQuery": query,
                "title": obj.get("title", ""),
                "culture": obj.get("culture", ""),
                "period": obj.get("period", ""),
                "objectDate": obj.get("objectDate", ""),
                "medium": obj.get("medium", ""),
                "dimensions": obj.get("dimensions", ""),
                "primaryImageSmall": obj.get("primaryImageSmall", ""),
                "primaryImage": obj.get("primaryImage", ""),
                "department": obj.get("department", ""),
                "objectURL": obj.get("objectURL", ""),
                "isPublicDomain": obj.get("isPublicDomain", False),
            }
            results.append(record)
            print(f"OK -- \"{record['title'][:60]}\"")

    # Save results
    out_path = "C:/Users/PC/Documents/Claude/Projects/ibuyartifacts/artifacts_data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nDone. {len(results)} artifacts saved to {out_path}")


if __name__ == "__main__":
    main()
