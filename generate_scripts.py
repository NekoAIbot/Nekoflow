# generate_scripts.py
import os
import json
import re
from pathlib import Path
from time import sleep
import requests
from dotenv import load_dotenv

load_dotenv()

LOCAL_LLM_URL = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:5000/v1")
MAX_SCRIPTS_PER_NICHE = 3  # default, adjustable later via config

def clean_filename(text):
    return re.sub(r'[^\w\s-]', '', text).strip().lower().replace(' ', '_')

def get_ranked_titles(filepath="ranked_topics.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_prompt(title, tags):
    niche = tags[0] if tags else "General"
    prompt = f"""You're a professional script writer for a trending {niche} YouTube channel.

Generate a compelling script for the following video title:
"{title}"

Structure:
- Hook the viewer in the first 10 seconds
- Present the key points clearly
- Add an interesting perspective
- Wrap up with a memorable or thought-provoking line

Be concise, engaging, and informative.
"""
    return prompt.strip()

def generate_script(title, tags):
    prompt = generate_prompt(title, tags)
    try:
        response = requests.post(
            f"{LOCAL_LLM_URL}/completions",
            json={
                "prompt": prompt,
                "max_tokens": 600,  # lower token count for speed
                "temperature": 0.8,
                "stop": None
            },
            timeout=90  # increase timeout to 90 seconds
        )
        response.raise_for_status()
        return response.json()["choices"][0]["text"].strip()
    except Exception as e:
        print(f"❌ Generation error for '{title}': {e}")
        return None

def save_script(script, title, tags):
    tag_folder = clean_filename(tags[0]) if tags else "uncategorized"
    filename = clean_filename(title) + ".txt"
    output_dir = Path("generated_scripts") / tag_folder
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / filename, "w", encoding="utf-8") as f:
        f.write(script)
    print(f"✅ Saved: {output_dir / filename}")

def main():
    print("🧠 Smart Script Generator")
    titles_by_tag = {}

    for entry in get_ranked_titles():
        for tag in entry["tags"]:
            tag = clean_filename(tag)
            if tag not in titles_by_tag:
                titles_by_tag[tag] = []
            titles_by_tag[tag].append(entry)

    for tag, entries in titles_by_tag.items():
        print(f"\n🎯 Generating scripts for niche: {tag.upper()} (max {MAX_SCRIPTS_PER_NICHE})")
        for entry in entries[:MAX_SCRIPTS_PER_NICHE]:
            title = entry["title"]
            tags = entry["tags"]
            print(f"⚡ Generating script for: {title} {tags}")
            script = generate_script(title, tags)
            if script:
                save_script(script, title, tags)
            sleep(2)  # avoid hammering the LLM

if __name__ == "__main__":
    main()
