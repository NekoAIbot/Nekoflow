import os
import json
import requests

# Configuration for the API endpoint for text generation.
# Update this URL if your Text Generation Web UI is hosted elsewhere.
TEXTGEN_API_URL = os.getenv("TEXTGEN_API_URL", "http://127.0.0.1:5000/v1/completions")

# Define all current and future niches here. (You can later load/update from niches.json)
niches = ["ai", "tech", "finance", "science", "cybersecurity"]

def call_textgen_api(prompt):
    """
    Calls the Text Generation Web UI API with the given prompt.
    Expects the JSON response to have a "results" key.
    """
    payload = {
        "prompt": prompt,
        "max_length": 1024,
        "temperature": 0.9,
        "top_p": 0.95,
        "do_sample": True,
        "num_return_sequences": 1,
        # The API might require a 'stop' parameter; adjust as needed.
        "pad_token_id": None  # If needed, set this to the appropriate EOS token ID.
    }
    try:
        response = requests.post(TEXTGEN_API_URL, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Error calling textgen API: {e}")
        return None

    try:
        result = response.json()
        # Expecting a structure like: {"results": [{"text": "generated text"}]}
        generated_text = result["results"][0]["text"].strip()
        return generated_text
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"❌ Error processing API response: {e}")
        print(f"❌ Full API response: {response.text}")
        return None

def generate_refined_script(topic, niche):
    """Generates a YouTube-ready script based on the input topic using the TextGen API."""
    prompt = (
        f"Write a high-quality, human-like YouTube video script for the {niche} niche "
        f"based on this topic:\n\n"
        f"Title: {topic.strip()}\n\n"
        f"The script should be engaging, natural, educational, and optimized for viewer retention. "
        f"Use a friendly tone and a storytelling style with facts, structure, and personality.\n\n"
        f"Script:\n"
    )
    generated = call_textgen_api(prompt)
    if generated is None:
        return None
    # Remove the prompt from the generated text if it was echoed back by the API.
    if generated.startswith(prompt):
        return generated[len(prompt):].strip()
    return generated.strip()

def process_niche(niche):
    """Processes all topic files under a niche and generates refined scripts."""
    niche_dir = os.path.join("trending_topics", niche)
    output_dir = os.path.join("generated_scripts", niche)
    os.makedirs(output_dir, exist_ok=True)

    # Process all .txt files in the niche directory
    for filename in os.listdir(niche_dir):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(niche_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            topic = f.read().strip()

        # Check for placeholders: if the topic is still the default (or very short), skip it.
        if "Example topic for" in topic or len(topic) < 10:
            print(f"⚠️ Placeholder topic in {filename}, skipping...")
            continue

        print(f"📝 Generating script for: {filename}")
        refined_script = generate_refined_script(topic, niche)
        if refined_script is None:
            print(f"❌ Failed to generate script for: {filename}")
            continue

        output_path = os.path.join(output_dir, filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(refined_script)
        print(f"✅ Saved: {output_path}")

def initialize_folders():
    """Creates missing folders for all niches and adds a placeholder if empty."""
    for niche in niches:
        niche_dir = os.path.join("trending_topics", niche)
        os.makedirs(niche_dir, exist_ok=True)

        # Add a placeholder topic if folder is empty
        if not os.listdir(niche_dir):
            placeholder_path = os.path.join(niche_dir, "sample_topic.txt")
            with open(placeholder_path, "w", encoding="utf-8") as f:
                f.write(f"Example topic for {niche} niche")
            print(f"ℹ️ Created placeholder in {niche_dir}")

def main():
    print("\n🚀 Generating refined YouTube scripts...\n")
    initialize_folders()

    for niche in niches:
        print(f"\n🔍 Niche: {niche}")
        niche_dir = os.path.join("trending_topics", niche)
        # Check if there is at least one non-placeholder topic file
        files = [fn for fn in os.listdir(niche_dir) if fn.endswith(".txt")]
        if not files:
            print(f"⚠️ No topics found in {niche_dir}. Skipping...")
            continue

        process_niche(niche)

if __name__ == "__main__":
    main()
