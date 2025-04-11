from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def load_local_model(model_name="EleutherAI/gpt-neo-1.3B"):
    """
    Loads the specified Hugging Face transformer model and tokenizer.
    Defaults to GPT-Neo 1.3B.
    """
    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
    print("✅ Model is ready to generate.")
    return generator

def generate_script(prompt, generator, max_length=300, temperature=0.7):
    """
    Uses the generator pipeline to create a script from a prompt.
    """
    outputs = generator(
        prompt,
        max_length=max_length,
        do_sample=True,
        temperature=temperature,
        truncation=True,
        pad_token_id=50256  # Standard for GPT-Neo
    )
    return outputs[0]["generated_text"]

if __name__ == "__main__":
    headline = "House adopts budget blueprint for Trump's agenda after GOP leaders sway holdouts - NBC News"

    prompt = f"""
You are a skilled YouTube scriptwriter known for making viral, engaging videos.

Write a complete, compelling YouTube script based on this trending headline:
"{headline}"

🧠 Guidelines:
- Start with a bold hook that grabs attention.
- Provide a short but powerful summary of the headline.
- Use simple, dramatic language that speaks to the average viewer.
- Include emotional and factual angles.
- End with a call to action (like, comment, subscribe).

🎯 Keep the entire script under 250 words.
Begin now:
"""

    # Load model and run generation
    generator = load_local_model("EleutherAI/gpt-neo-1.3B")
    script = generate_script(prompt, generator)

    # Optional cleanup: extract text after "Begin now:"
    if "Begin now:" in script:
        script = script.split("Begin now:")[-1].strip()

    print("\n📝 Final Script:\n")
    print(script)
