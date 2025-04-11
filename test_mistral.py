import requests

prompt = "Write a short, funny poem about AI learning to cook."
payload = {
    "model": "mistral",          # Tell Ollama explicitly to use the "mistral" model
    "prompt": prompt,
    "temperature": 0.7,
    "max_tokens": 200,
}

# Note: Ollama's API endpoint is typically /api/generate
response = requests.post("http://localhost:11434/api/generate", json=payload)

print(response.json())
