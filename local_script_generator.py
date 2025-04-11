from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def load_local_model(model_name="EleutherAI/gpt-j-6B"):
    """
    Loads a strong text-generation model.
    Default is GPT-J 6B which is more powerful than GPT-Neo 1.3B.
    """
    print(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    print("✅ Model loaded. (This may take a while on CPU.)")
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

def generate_script(prompt, generator, max_length=300, temperature=0.7):
    """
    Generate a YouTube script from the prompt using the given generator.
    """
    outputs = generator(
        prompt,
        max_length=max_length,
        do_sample=True,
        temperature=temperature,
        truncation=True,
        pad_token_id=50256  # GPT-J uses the same EOS token as GPT-Neo
    )
    return outputs[0]["generated_text"]

if __name__ == "__main__":
    # Example headline (tech-focused)
    headline = "Tech giants announce breakthrough in quantum computing innovation."

    prompt = f"""
You are a skilled YouTube scriptwriter specializing in tech content.

Write an engaging, complete YouTube script based on this trending headline:
"{headline}"

🧠 Guidelines:
- Begin with a bold hook to capture viewer attention.
- Provide a concise summary of the breakthrough.
- Explain the significance in terms that both tech enthusiasts and general viewers can grasp.
- End with a strong call-to-action (like, comment, subscribe).

Keep the script under 250 words.
Begin now:
"""

    # Load the GPT-J 6B model (this is a strong model that leverages your Codespace resources)
    generator = load_local_model("EleutherAI/gpt-j-6B")

    # Generate the script
    script = generate_script(prompt, generator)

    # Optional cleanup: Remove any leading unwanted prompt echoes
    if "Begin now:" in script:
        script = script.split("Begin now:")[-1].strip()

    print("\n📝 Final Script:\n")
    print(script)
