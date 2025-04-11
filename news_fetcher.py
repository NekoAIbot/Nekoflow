import os
import requests
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news_titles(category="technology", country="us", language="en"):
    url = f"https://newsdata.io/api/1/news?apikey={NEWS_API_KEY}&category={category}&country={country}&language={language}"
    try:
        response = requests.get(url)
        data = response.json()
        articles = data.get("results", [])
        return [article["title"] for article in articles if "title" in article][:5]
    except Exception as e:
        print(f"❌ Failed to fetch news: {e}")
        return []

if __name__ == "__main__":
    print("\n📰 Trending Tech News:\n")
    titles = fetch_news_titles()
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
