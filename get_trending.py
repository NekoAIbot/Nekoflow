from pytrends.request import TrendReq

def fetch_trending_topics(region='nigeria'):
    # Google Trends fallback (static mock for now)
    print("⚠️ Google Trends not available, using fallback data.")
    return [
        "AI takes over creative industry",
        "NVIDIA RTX 5090D world record",
        "Netflix Black Mirror Game",
        "Trump AI policy controversy",
        "Nintendo Switch 2 leak"
    ]

if __name__ == "__main__":
    topics = fetch_trending_topics()
    print("\n🔥 Trending Google Searches:")
    for i, topic in enumerate(topics[:10], 1):
        print(f"{i}. {topic}")
