import os
import requests

api_key = os.getenv("GEMINI_API_KEY")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

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
