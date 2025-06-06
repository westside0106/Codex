# html_generator.py
from pathlib import Path

html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Modell hinzufügen</title>
</head>
<body>
    <h1>🛠️ Hot Wheels Modell eintragen</h1>
    <form action="/collect_form" method="post">
        <label for="toy_number">Toy #:</label>
        <input type="text" id="toy_number" name="toy_number" required><br><br>

        <label for="quantity">Anzahl:</label>
        <input type="number" id="quantity" name="quantity" value="1" min="1"><br><br>

        <button type="submit">✅ Speichern</button>
    </form>
</body>
</html>
"""

Path("form_collect.html").write_text(html_content, encoding="utf-8")
print("✔️ HTML-Datei erstellt: form_collect.html")
