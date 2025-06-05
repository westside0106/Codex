from fastapi import FastAPI
from agent import ask_codex
from plugins import get_plugins

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Codex is running."}

@app.get("/ask")
def ask(prompt: str):
    answer = ask_codex(prompt)
    return {"answer": answer}

@app.get("/plugins")
def plugins():
    return {"available_plugins": get_plugins()}
