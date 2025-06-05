# Codex – Modular AI Agent Framework

Dieses Projekt kombiniert:
- 🧠 Einfache LLM-Integration
- ⚡ FastAPI für Webzugriff
- 📦 Modulares Projekt mit Plugin-System

## Start

```bash
uvicorn main:app --reload
```

## Beispielaufruf

```http
GET /ask?prompt=Hello
GET /ask?prompt=plugin:example
GET /plugins
```
