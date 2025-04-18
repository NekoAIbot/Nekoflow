#!/usr/bin/env python3
import os
import argparse
from pathlib import Path

import openai
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️  Please set OPENAI_API_KEY in your .env")
    exit(1)

openai.api_key = OPENAI_API_KEY

def generate_script(topic: str, fast: bool = False) -> str:
    """
    Call OpenAI's Chat Completion endpoint to get a video script for `topic`.
    If --fast is passed, you could adjust `max_tokens` or skip certain steps.
    """
    # system prompt can be as elaborate as you like:
    system_prompt = (
        "You are a professional video script writer for short-form social media content. "
        "Given a topic, produce a clear, engaging script outline with sections: hook, body, call-to-action."
    )

    user_prompt = f"Write a concise video script for the topic:\n\n\"{topic}\"\n\nFormat as plain text."

    # you can tweak model, temperature, max_tokens, etc.
    params = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 600,
    }
    if fast:
        params["max_tokens"] = 300  # example: shorter scripts in fast mode

    resp = openai.chat.completions.create(**params)
    # pick the first choice:
    return resp.choices[0].message["content"]

def main(fast: bool):
    src_root  = Path("trending_topics")
    out_root  = Path("video_scripts")
    out_root.mkdir(exist_ok=True)

    for niche_dir in src_root.iterdir():
        if not niche_dir.is_dir():
            continue
        for txt_file in sorted(niche_dir.glob("*.txt")):
            topic = txt_file.read_text(encoding="utf-8", errors="ignore").strip()
            short_name = f"{niche_dir.name}__{txt_file.stem}"
            print(f"✍️  Generating script for {short_name}…", end=" ")

            try:
                script = generate_script(topic, fast=fast)
                out_path = out_root / f"{short_name}.md"
                out_path.write_text(script, encoding="utf-8")
                print("✅")
            except Exception as e:
                print("❌\n   ", e)

    print("\n🏁 All done. Scripts are in:", out_root)

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Generate video scripts from trending-topic .txt files"
    )
    p.add_argument(
        "--fast", action="store_true",
        help="Produce shorter scripts (fewer tokens) for quick iteration"
    )
    args = p.parse_args()
    main(fast=args.fast)
