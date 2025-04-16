from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def load_local_model(size="fast"):
    """
    Loads GPT-Neo 125M (fast) or 1.3B (smart) based on 'size'.
    """
    if size == "smart":
        model_name = "EleutherAI/gpt-neo-1.3B"
    else:
        model_name = "EleutherAI/gpt-neo-125M"

    print(f"📦 Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

def generate_script(prompt, generator, max_length=300, temperature=0.7):
    """
    Generates script from prompt using the generator pipeline.
    """
    outputs = generator(
        prompt,
        max_length=max_length,
        do_sample=True,
        temperature=temperature,
        truncation=True,
        pad_token_id=50256
    )
    return outputs[0]["generated_text"]
