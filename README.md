# Codex 🧠🔍 – Das Sammler-Tool für Hot Wheels Modelle

Codex ist ein intelligentes System zur Verwaltung, Analyse und Erweiterung deiner Hot Wheels Sammlung. Es unterstützt das Erkennen von Duplikaten, zeigt dir fehlende Modelle je Serie und Jahr an und ermöglicht smarte Dateneingabe via Formular – ideal für Sammler, die Überblick und Tiefe wollen.

## 🔧 Funktionen

- ✅ Sammlung verwalten und analysieren
- 📄 CSV- und JSON-Export deiner Sammlung
- 🔍 Serie + Jahr-basierte Fortschrittsanzeige
- 🧠 Intelligente Duplikaterkennung (auch mit Mengenangabe)
- ⚙️ Live-Modellvorschau beim Hinzufügen (Toy #)
- 🌐 Webbasierte Oberfläche via FastAPI

## 📁 Ordnerstruktur

```
Codex/
├── data/
│   ├── DONE_HotWheels1_commas.csv         ← Vollständige Modell-Datenbank
│   ├── HotWheelsGitCollection.csv         ← Deine persönliche Sammlung
│   └── HotWheelsYear-Toy.csv              ← Zuordnung Toy # → Jahr
├── templates/
│   ├── form_collect.html                  ← Eingabeformular
├── static/
│   └── success.html                       ← Bestätigungsseite
├── collect_api.py                         ← FastAPI-Backend mit allen Routen
├── main.py                                ← App-Starter
└── README.md                              ← Diese Datei
```

## ▶️ Startanleitung

1. **Projekt klonen**  
   ```bash
   git clone https://github.com/westside0106/Codex.git
   cd Codex
   ```

2. **Virtual Environment aktivieren (optional aber empfohlen)**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Abhängigkeiten installieren**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Server starten**  
   ```bash
   uvicorn collect_api:app --reload
   ```

5. Öffne im Browser: [http://127.0.0.1:8000/form](http://127.0.0.1:8000/form)

## ✨ Hinweise

- Sammel-Datenbank (`DONE_HotWheels1_commas.csv`) wird nicht automatisch aktualisiert.
- Neue Modelle kannst du per Toy # eingeben oder direkt via CSV ergänzen.
- Die Duplikaterkennung berücksichtigt Farbvarianten als eigenständig.

---

Erstellt von **Philipp Lahn** 🏎️✨  
Feedback oder Ideen? → GitHub-Issue oder PN.
