import feedparser

import feedparser

def fetch_google_news_titles():
    rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)

    titles = []
    for entry in feed.entries[:10]:
        titles.append(entry.title)
    return titles

if __name__ == "__main__":
    print("\n📰 Google News RSS:\n")
    titles = fetch_google_news_titles()
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")
