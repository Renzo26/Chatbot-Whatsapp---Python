import os
import requests

def process_ai_response(message_text: str) -> str:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/completions"
    headers = {"Authorization": f"Bearer {openai_api_key}"}
    data = {
        "model": "gpt-4",
        "prompt": message_text,
        "max_tokens": 100
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json().get("choices", [{}])[0].get("text", "")
