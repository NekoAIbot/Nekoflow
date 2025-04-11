import requests

def fetch_reddit_titles(subreddit="technology", limit=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    try:
        response = requests.get(url, headers=headers)
        posts = response.json()["data"]["children"]
        return [post["data"]["title"] for post in posts]
    except Exception as e:
        print(f"❌ Failed to fetch Reddit posts: {e}")
        return []

if __name__ == "__main__":
    print("\n🔥 Top Posts on r/technology:\n")
    for i, title in enumerate(fetch_reddit_titles(), 1):
        print(f"{i}. {title}")
