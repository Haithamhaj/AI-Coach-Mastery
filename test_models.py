import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

models_to_test = [
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-flash-latest",
    "gemini-pro",
    "gemini-1.5-pro-latest"
]

print("Testing models...")
for model_name in models_to_test:
    print(f"Testing {model_name}...", end=" ")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"SUCCESS! Response: {response.text.strip()}")
        # If success, we found a winner, but let's test others to be sure what's best
    except Exception as e:
        print(f"FAILED. Error: {e}")
