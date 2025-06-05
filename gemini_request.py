import os
from pathlib import Path
import requests


def load_api_key() -> str:
    """Load API key from ``api_key.txt`` if available or fallback to environment."""
    key_file = Path(__file__).with_name("api_key.txt")
    if key_file.exists():
        return key_file.read_text().strip()
    return os.getenv("GEMINI_API_KEY", "")


api_key = load_api_key()
url = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-2.0-flash:generateContent?key={api_key}"
)

headers = {
    "Content-Type": "application/json"
}

data = {
    "contents": [{
        "parts": [{"text": "Write 3 reasons why I should move to Malaysia."}]
    }]
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
