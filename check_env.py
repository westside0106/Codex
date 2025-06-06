import os
from dotenv import load_dotenv

def check_env():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key and api_key.startswith("sk-"):
        print("✅ OPENAI_API_KEY is set.")
    elif api_key:
        print("⚠️ OPENAI_API_KEY is set, but format looks wrong.")
    else:
        print("❌ OPENAI_API_KEY is missing. Please check your .env file.")

if __name__ == "__main__":
    check_env()
