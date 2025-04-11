import os
from dotenv import load_dotenv
import openai
from combine_sources import combine_sources

# ✅ Load environment variables only once
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ OPENAI_API_KEY not found in .env. Exiting.")
    exit()

# ✅ Initialize OpenAI client (correct for v1.0+)
client = openai.OpenAI(api_key=api_key)

def generate_script(title):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful and engaging YouTube content writer. Write a compelling video script based on the headline."
                },
                {
                    "role": "user",
                    "content": f"Write a YouTube script for this headline:\n\n{title}"
                }
            ],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error generating script:\n\n{str(e)}"

def main():
    print("📡 Gathering trending topics...\n")
    trending_titles = combine_sources()

    if not trending_titles:
        print("❌ No trending titles found.")
        return

    print("\n🧩 Combined Trending Titles:")
    for i, title in enumerate(trending_titles[:15], 1):
        print(f"{i}. {title}")

    print("\n🧠 Generating scripts...\n")
    for i, title in enumerate(trending_titles[:3], 1):  # Limit to top 3 scripts
        print(f"\n📝 Script {i}: {title}")
        script = generate_script(title)
        print(script)

if __name__ == "__main__":
    main()
