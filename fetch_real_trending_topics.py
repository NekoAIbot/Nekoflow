import os
import json
import requests

def load_niches():
    """
    Load niches from niches.json if available;
    otherwise, return a default list of niches.
    """
    niches_file = "niches.json"
    if os.path.isfile(niches_file):
        try:
            with open(niches_file, "r", encoding="utf-8") as f:
                niches = json.load(f)
            # Expecting niches.json to be a JSON list
            if isinstance(niches, list) and niches:
                return niches
            else:
                print("⚠️ niches.json exists but is empty or not in the correct format. Using default niches.")
        except Exception as e:
            print(f"⚠️ Error loading niches.json: {e}. Using default niches.")
    # Default niches if file is missing or has issues
    return ["ai", "tech", "finance", "science", "cybersecurity"]

def initialize_trending_folders(niches):
    """
    Creates the base 'trending_topics' folder and a subfolder for each niche.
    """
    base_dir = "trending_topics"
    os.makedirs(base_dir, exist_ok=True)
    for niche in niches:
        niche_dir = os.path.join(base_dir, niche)
        os.makedirs(niche_dir, exist_ok=True)
        # Optionally, you can add a placeholder topic if the folder is empty.
        if not os.listdir(niche_dir):
            placeholder_path = os.path.join(niche_dir, "sample_topic.txt")
            with open(placeholder_path, "w", encoding="utf-8") as f:
                f.write(f"Example topic for {niche} niche")
            print(f"ℹ️ Created placeholder topic in {niche_dir}")

def fetch_trending_topics_for_niche(niche):
    """
    Fetches trending topics for the given niche.
    
    This sample implementation uses static examples.
    Replace this logic with real API calls to fetch current trending topics.
    """
    topics = []
    if niche.lower() == "ai":
        topics = [
            "AI breakthroughs in 2025: The next generation of machine learning",
            "How GPT-4 is revolutionizing natural language understanding"
        ]
    elif niche.lower() == "tech":
        topics = [
            "New smartphone release sets the stage for mobile innovation",
            "Tech giants invest billions in quantum computing research"
        ]
    elif niche.lower() == "finance":
        topics = [
            "Global stock markets rally amid economic recovery signals",
            "Central banks adjust interest rates to tackle rising inflation"
        ]
    elif niche.lower() == "science":
        topics = [
            "SpaceX launches historic mission to Mars",
            "Breakthrough in renewable energy could change global power dynamics"
        ]
    elif niche.lower() == "cybersecurity":
        topics = [
            "Massive data breach impacts millions worldwide",
            "New cybersecurity tool aims to combat ransomware attacks"
        ]
    else:
        # For any additional niche, you can attempt a simple keyword search
        # or integrate with a news API that supports a query for that niche.
        topics = [
            f"Trending topic example for {niche} #1",
            f"Trending topic example for {niche} #2"
        ]
    return topics

def save_topics_for_niche(niche, topics):
    """
    Saves the list of topics for the given niche as individual text files.
    """
    niche_dir = os.path.join("trending_topics", niche)
    for index, topic in enumerate(topics, start=1):
        # Create a unique filename using the niche and index
        filename = f"{niche}_{index:03d}.txt"
        filepath = os.path.join(niche_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(topic)
        print(f"✅ Saved topic to {filepath}")

def main():
    niches = load_niches()
    print("🚀 Fetching trending topics for all niches in niches.json...")
    initialize_trending_folders(niches)
    for niche in niches:
        print(f"🔍 Fetching for niche: {niche}")
        topics = fetch_trending_topics_for_niche(niche)
        if topics:
            save_topics_for_niche(niche, topics)
        else:
            print(f"⚠️ No results found for: {niche}")
    print("✅ Finished fetching real trending topics!")

if __name__ == "__main__":
    main()
