import json
import re
from collections import defaultdict

# === STEP 1: Load trending topics ===
with open("trending_topics.json", "r") as f:
    titles = json.load(f)

# === STEP 2: Define categories and smart keyword tags ===
CATEGORIES = {
    "AI": [
        "AI", "artificial intelligence", "ChatGPT", "GPT", "LLM", "machine learning",
        "deep learning", "neural network", "OpenAI", "Anthropic", "Claude", "prompt",
        "AI-generated", "AI model", "Midjourney", "stability ai", "autogen", "transformer"
    ],
    "Cybersecurity": [
        "cyber", "hacking", "hacker", "infosec", "ransomware", "malware", "phishing",
        "exploit", "CVE", "breach", "DDoS", "zero-day", "security", "pentest", "cyberattack"
    ],
    "Finance": [
        "market", "stocks", "earnings", "NASDAQ", "S&P", "Dow", "crypto", "bitcoin",
        "economy", "inflation", "tariff", "trade", "interest rate", "Federal Reserve"
    ],
    "Politics": [
        "Biden", "Trump", "election", "senate", "congress", "government", "democrat",
        "republican", "campaign", "president", "political", "nominee"
    ],
    "Science": [
        "experiment", "research", "neutrino", "particle", "biology", "space", "NASA",
        "quantum", "physics", "science", "telescope"
    ],
    "Tech": [
        "Tesla", "Apple", "Google", "Microsoft", "Meta", "Amazon", "iPhone", "Android",
        "Pixel", "AI chip", "processor", "semiconductor", "technology", "software", "update"
    ]
}

def tag_title(title):
    """Tag title with matching categories."""
    tags = set()
    lower_title = title.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', lower_title):
                tags.add(category)
                break  # one match is enough for this category
    return list(tags)

# === STEP 3: Score and rank titles ===
ranked = []

for title in titles:
    tags = tag_title(title)
    score = len(tags)
    ranked.append({
        "title": title,
        "score": score,
        "tags": tags
    })

# === STEP 4: Sort by score descending ===
ranked_sorted = sorted(ranked, key=lambda x: x["score"], reverse=True)

# === STEP 5: Save output ===
with open("ranked_topics.json", "w") as f:
    json.dump(ranked_sorted, f, indent=2)

print("✅ Ranked titles saved to ranked_topics.json")

# === Optional: Print Top 10 ranked titles ===
print("\n📊 Top Ranked Titles:")
for i, item in enumerate(ranked_sorted[:10], 1):
    print(f"{i}. {item['title']} ({', '.join(item['tags']) or 'Uncategorized'})")
