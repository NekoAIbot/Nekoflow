from local_script_generator import load_local_model, generate_script
from combine_sources import combine_sources
import os

# Set mode to "fast" which means using GPT-Neo 1.3B (adjust if needed)
model_name = "EleutherAI/gpt-neo-1.3B"

# Fetch live trending titles (real headlines)
titles = combine_sources()

if not titles:
    print("No trending titles found. Please check your sources.")
    exit()

print("Live Trending Titles:")
for i, t in enumerate(titles, 1):
    print(f"{i}. {t}")

# Load the selected model
generator = load_local_model(model_name)
print("Model loaded. Generating scripts...")

# Create folder to save generated scripts
os.makedirs("scripts", exist_ok=True)

# Number of scripts to generate for testing
limit = 3

for i, title in enumerate(titles[:limit], start=1):
    print(f"\n📌 Generating Script {i} for headline:\n{title}\n")
    prompt = f"""
You are a skilled YouTube scriptwriter specializing in tech content.

Write an engaging, complete, and compelling YouTube script based on the following headline:
"{title}"

Guidelines:
- Begin with a bold hook to capture attention.
- Provide a concise summary of the headline.
- Use simple, dramatic language that appeals to a tech-savvy audience.
- Include both emotional and factual angles.
- End with a clear call-to-action (like, comment, and subscribe).

Keep the entire script under 250 words.
Begin now:
"""
    script = generate_script(prompt, generator)

    # Clean-up: Remove everything before (or including) "Begin now:" if echoed back.
    if "Begin now:" in script:
        script = script.split("Begin now:")[-1].strip()
    
    # Append a call to action if missing
    if "subscribe" not in script.lower():
        script += "\n\n💬 Don't forget to like, comment, and subscribe!"
    
    filename = f"script_{i}.txt"
    with open(os.path.join("scripts", filename), "w", encoding="utf-8") as f:
        f.write(f"{title}\n\n{script}")

    print(f"✅ Script {i} saved as {filename}")
