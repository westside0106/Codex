import openai
import os
import json
from plugins import run_plugin
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("config/config.json") as f:
    config = json.load(f)

def ask_codex(prompt: str) -> str:
    if prompt.startswith("plugin:"):
        return run_plugin(prompt.split("plugin:")[1].strip())
    try:
        response = openai.ChatCompletion.create(
            model=config["openai"]["model"],
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI error: {e}"
