import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

nltk.download('punkt')

def cluster_topics(topics, num_clusters=3):
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(topics)
    model = KMeans(n_clusters=num_clusters, random_state=42)
    model.fit(X)
    
    clustered = {}
    for i, label in enumerate(model.labels_):
        clustered.setdefault(label, []).append(topics[i])
    
    return clustered

# Test it with sample headlines
if __name__ == "__main__":
    sample_topics = [
        "Trump Suspends Nvidia Export Ban After $1M Dinner",
        "Trump Tariffs May Accelerate AI Automation",
        "Star Citizen Breaks Crowdfunding Record Again",
        "Nintendo Hoards Switch 2 Consoles in US",
        "Disinformation Is Spreading Online Rapidly"
    ]
    
    grouped = cluster_topics(sample_topics)
    print("\n🧠 Clustered Topics:")
    for group, items in grouped.items():
        print(f"\n📦 Group {group + 1}:")
        for topic in items:
            print(f" - {topic}")
