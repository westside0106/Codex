# 🧠 Codex – Modular AI Assistant

Codex is a flexible AI framework powered by FastAPI and OpenAI, designed for plugins, configuration via JSON, and structured data processing.

---

## 🚀 Quickstart

### ▶️ Local
```bash
pip install -r requirements.txt
./start.sh
```

Open your browser at: [http://localhost:8000](http://localhost:8000)

---

### 🐳 Docker
```bash
docker build -t codex .
docker run -p 8000:8000 codex
```

---

## 🔌 Plugins

Create a new plugin in `plugins/` with a `run()` function.

Example:
```python
# plugins/greet.py
def run(name="stranger"):
    return f"Hello, {name}!"
```

Call via:
```
/ask?prompt=plugin:greet?name=Philipp
```

---

## ⚙️ Config

All main settings are in `config/config.json`:
- OpenAI model
- Temperature
- Plugin options
- CSV path

---

## 🗂 Structure

```
codex_project/
├── main.py
├── start.sh
├── Dockerfile
├── README.md
├── requirements.txt
├── config/
│   └── config.json
├── agent/
│   └── agent.py
├── plugins/
│   ├── __init__.py
│   └── example.py
├── data/
│   └── hotwheels_data.csv
```

---

## 🔐 .env

Create a `.env` file:

```
OPENAI_API_KEY=sk-...
```

---

MIT License – 2025 by Philipp Lahn
