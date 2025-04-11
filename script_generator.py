import os
import requests
from dotenv import load_dotenv

load_dotenv()

use_local = os.getenv("USE_LOCAL_LLM", "False") == "True"
local_url = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1")

def generate_script_local(prompt):
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "local-model",  # LM Studio ignores this field
        "messages": [
            {"role": "system", "content": "You are a helpful script writer."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(f"{local_url}/chat/completions", json=payload, headers=headers)
    return response.json()["choices"][0]["message"]["content"].strip()

def generate_script(prompt):
    if use_local:
        return generate_script_local(prompt)

    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful script writer."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message["content"].strip()
