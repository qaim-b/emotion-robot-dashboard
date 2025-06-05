import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Convert the generator to a list
models = list(genai.list_models())
print("Available models:", models)

