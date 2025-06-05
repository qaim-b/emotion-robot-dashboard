import os
import google.generativeai as genai

# Load API key from environment variable
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use correct model name (even for free tier)
model = genai.GenerativeModel(model_name="models/gemini-pro")

# Prompt
prompt = "The user is feeling sad. Say something comforting."
response = model.generate_content(prompt)

# Print the result
print("Gemini says:", response.text)

