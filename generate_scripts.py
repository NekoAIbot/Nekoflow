import os
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import torch

# Load model and tokenizer once at the start
print("🧠 Loading GPT-Neo 1.3B locally...")
model_name = "EleutherAI/gpt-neo-1.3B"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name)
device = torch.device("cpu")
model.to(device)
print("✅ Model loaded!")

# Define all current and future niches here
niches = ["ai", "tech", "finance", "science", "cybersecurity"]

def generate_refined_script(topic, niche):
    """Generates a YouTube-ready script based on the input topic using GPT-Neo."""
    prompt = (
        f"Write a high-quality, human-like YouTube video script for the {niche} niche "
        f"based on this topic:\n\n"
        f"Title: {topic.strip()}\n\n"
        f"The script should be engaging, natural, educational, and optimized for viewer retention. "
        f"Use a friendly tone and storytelling style with facts, structure, and personality.\n\n"
        f"Script:\n"
    )

    inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True).to(device)
    outputs = model.generate(
        **inputs,
        max_length=1024,
        temperature=0.9,
        top_p=0.95,
        do_sample=True,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id,
    )

    script = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return script[len(prompt):].strip()

def process_niche(niche):
    """Processes all topics under a niche and generates scripts."""
    niche_dir = os.path.join("trending_topics", niche)
    output_dir = os.path.join("generated_scripts", niche)
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(niche_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(niche_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                topic = f.read().strip()

            print(f"📝 Generating script for: {filename}")
            script = generate_refined_script(topic, niche)

            output_path = os.path.join(output_dir, filename)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(script)

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

if __name__ == "__main__":
    print("\n🚀 Generating refined YouTube scripts...\n")
    initialize_folders()

    for niche in niches:
        print(f"\n🔍 Niche: {niche}")
        niche_dir = os.path.join("trending_topics", niche)

        if not os.listdir(niche_dir):
            print(f"⚠️ No topics found in {niche_dir}. Skipping...")
            continue

        process_niche(niche)
