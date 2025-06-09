from fastapi import FastAPI
from collect_api import router as collect_router
from agent.agent import ask_codex
from plugins import get_plugins
import json

with open("config/config.json") as f:
    config = json.load(f)

app = FastAPI(title=config.get("project_name", "Codex"))
app.include_router(collect_router)

@app.get("/")
def root():
    return {"message": config.get("description", "Codex is running.")}

@app.get("/ask")
def ask(prompt: str):
    return {"answer": ask_codex(prompt)}

@app.get("/plugins")
def plugins():
    return {"plugins": get_plugins()}