import os
from pathlib import Path
import google.generativeai as genai


def load_api_key() -> str:
    """Load API key from ``api_key.txt`` or ``GEMINI_API_KEY`` env var."""
    key_file = Path(__file__).with_name("api_key.txt")
    if key_file.exists():
        return key_file.read_text().strip()
    return os.getenv("GEMINI_API_KEY", "")


api_key = load_api_key()
if not api_key:
    raise RuntimeError("API key not found. Provide api_key.txt or GEMINI_API_KEY env var.")

genai.configure(api_key=api_key)

# Use correct model name (even for free tier)
model = genai.GenerativeModel(model_name="models/gemini-pro")

# Prompt
prompt = "The user is feeling sad. Say something comforting."
response = model.generate_content(prompt)

# Print the result
print("Gemini says:", response.text)

