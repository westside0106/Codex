# 🧰 Codex: Hot Wheels Sammlungsmanager

**Codex** ist ein persönlicher Sammlungsagent für Hot Wheels-Modelle, der auf FastAPI basiert. Er ermöglicht das Erfassen, Verwalten und Exportieren deiner Sammlung mit einer benutzerfreundlichen Weboberfläche und API-Endpunkten.

---

## 🚗 Funktionen

- **Modell hinzufügen**: Trage neue Modelle mit ihrer Toy-Nummer und Anzahl über ein Webformular ein.
- **Sammlung anzeigen**: Durchsuche deine Sammlung in einer visuellen HTML-Tabelle mit Bildern.
- **JSON-Export**: Exportiere deine Sammlung als JSON für die Weiterverarbeitung.
- **API-Dokumentation**: Interaktive Swagger-Oberfläche zur Erkundung der API-Endpunkte.

---

## 🛠️ Installation

1. **Repository klonen**:

   ```bash
   git clone https://github.com/westside0106/Codex.git
   cd Codex
   ```

2. **Abhängigkeiten installieren**:

   Stelle sicher, dass Python 3.7 oder höher installiert ist.

   ```bash
   pip install -r requirements.txt
   ```

3. **Server starten**:

   ```bash
   uvicorn collect_api:app --reload
   ```

4. **Zugriff auf die Anwendung**:

   Öffne deinen Browser und navigiere zu `http://127.0.0.1:8000/`.

---

## 🌐 Weboberfläche

- **Modell hinzufügen**: [http://127.0.0.1:8000/form](http://127.0.0.1:8000/form)
- **Sammlung anzeigen**: [http://127.0.0.1:8000/collection](http://127.0.0.1:8000/collection)
- **JSON-Export**: [http://127.0.0.1:8000/export/json](http://127.0.0.1:8000/export/json)
- **API-Dokumentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📁 Projektstruktur

```
Codex/
├── collect_api.py           # Haupt-FastAPI-Anwendung
├── export_json_plugin.py    # Plugin für JSON-Export
├── static/
│   ├── index.html           # Startseite mit Navigation
│   └── collection_view.html # Visuelle Sammlungsvorschau
├── templates/
│   └── form_collect.html    # HTML-Formular zum Hinzufügen von Modellen
├── data/
│   ├── DONE_HotWheels1_commas.csv  # Ursprüngliche Datenbank
│   └── HotWheelsGitCollection.csv  # Benutzerdefinierte Sammlung
└── requirements.txt         # Python-Abhängigkeiten
```

---

## 📦 Abhängigkeiten

- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [Pandas](https://pandas.pydata.org/)
- [Jinja2](https://palletsprojects.com/p/jinja/)

Installiere alle Abhängigkeiten mit:

```bash
pip install -r requirements.txt
```

---

## 🤝 Mitwirken

Beiträge sind willkommen! Wenn du neue Funktionen hinzufügen oder Fehler beheben möchtest:

1. Forke das Repository.
2. Erstelle einen neuen Branch: `git checkout -b feature/DeineFunktion`.
3. Nimm deine Änderungen vor und committe sie: `git commit -m 'Füge neue Funktion hinzu'`.
4. Push den Branch: `git push origin feature/DeineFunktion`.
5. Erstelle einen Pull Request.

---

## 📄 Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).

---

## 📬 Kontakt

Bei Fragen oder Anregungen kannst du mich über GitHub kontaktieren: [@westside0106](https://github.com/westside0106)