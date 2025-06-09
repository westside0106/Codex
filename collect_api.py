from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import re
import textwrap

from pathlib import Path
import csv, re

router = APIRouter()
templates = Jinja2Templates(directory="templates")

DATA_PATH = Path("data/DONE_HotWheels1_commas.csv")
COLLECTION_PATH = Path("data/HotWheelsGitCollection.csv")

class CollectRequest(BaseModel):
    toy_number: str
    quantity: int = 1

def load_database():
    with open(DATA_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_collection():
    if not COLLECTION_PATH.exists():
        return []
    with open(COLLECTION_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_collection(entries, fieldnames):
    with open(COLLECTION_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
def collect_model(data: CollectRequest) -> dict:
    db = load_database()
    collection = load_collection()

    matches = [entry for entry in db if entry["Toy #"] == data.toy_number]
    if not matches:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")

    new_entry = matches[0]
    new_entry["Quantity"] = str(data.quantity)

    already_in = False
    total_quantity = data.quantity

    for entry in collection:
        if (
            entry["Toy #"] == new_entry["Toy #"]
            and entry.get("Photo", "").strip() == new_entry.get("Photo", "").strip()
            and entry.get("Model Name", "").strip() == new_entry.get("Model Name", "").strip()
        ):
            existing_qty = int(entry.get("Quantity", "1"))
            total_quantity = existing_qty + data.quantity
            entry["Quantity"] = str(total_quantity)
            already_in = True
            break

    if not already_in:
        collection.append(new_entry)

    fieldnames = list(collection[0].keys())
    save_collection(collection, fieldnames)

    return {
        "new_quantity": total_quantity,
        "type": "updated" if already_in else "new"
    }
def normalize_series(name: str) -> str:
    """
    Bereinigt Seriennamen, indem Add-ons wie 'New for 2023', 'Kroger Exclusive', etc. entfernt werden.
    """
    name = name.strip()
    # Entferne bekannte Zusätze
    name = re.sub(r"\b(New for\s?\d{4}|New for|Target Exclusive|Kroger Exclusive|Exclusive|2nd Color|Walmart|GameStop Exclusive|Multipack Exclusive)\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[–\-]{1,2}", "", name)  # entferne Bindestriche/Trennstriche
    name = re.sub(r"\s{2,}", " ", name)     # doppelte Leerzeichen
    return name.strip()

@router.get("/form", response_class=HTMLResponse)
def serve_form_page():
    filepath = Path("templates/form_collect.html")
    if not filepath.exists():
        return HTMLResponse(content="❌ form_collect.html nicht gefunden", status_code=404)
    return HTMLResponse(content=filepath.read_text(encoding="utf-8"))

@router.post("/collect")
def collect_model_api(data: CollectRequest):
    db = load_database()
    collection = load_collection()

    matches = [entry for entry in db if entry["Toy #"] == data.toy_number]
    if not matches:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")

    new_entry = matches[0]
    new_entry["Quantity"] = str(data.quantity)
    total_quantity = data.quantity
    already_in = False

    for entry in collection:
        if (
            entry["Toy #"] == new_entry["Toy #"]
            and entry.get("Photo", "").strip() == new_entry.get("Photo", "").strip()
            and entry.get("Model Name", "").strip() == new_entry.get("Model Name", "").strip()
        ):
            old_qty = int(entry.get("Quantity", "1"))
            new_qty = old_qty + data.quantity
            entry["Quantity"] = str(new_qty)
            total_quantity = new_qty
            already_in = True
            break

    if not already_in:
        collection.append(new_entry)

    fieldnames = list(collection[0].keys())
    save_collection(collection, fieldnames)

    return {
        "success": True,
        "message": "✅ Modell gespeichert",
        "toy_number": data.toy_number,
        "quantity": data.quantity,
        "total_quantity": total_quantity,
        "type": "new" if not already_in else "updated"
    }

@router.post("/collect_form")
def collect_form(toy_number: str = Form(...), quantity: int = Form(1)):
    result = collect_model(CollectRequest(toy_number=toy_number, quantity=quantity))
    return JSONResponse(content={
        "success": True,
        "toy_number": toy_number,
        "total_quantity": result["new_quantity"]
    })

@router.get("/collection", response_class=HTMLResponse)
def view_collection():
    import re

    def normalize_series_for_view(series: str) -> str:
        series = re.sub(r"^\d{4}\s*", "", series)
        series = re.sub(r"(New for\s?\d{4}|New for|Kroger Exclusive|Exclusive|Walmart|2nd Color|Target Exclusive|GameStop Exclusive|Multipack Exclusive|!)", "", series, flags=re.IGNORECASE)
        return series.strip()

    collection = load_collection()
    if not collection:
        return "<h3>❌ Noch keine Modelle gespeichert.</h3>"

    headers = collection[0].keys()
    total_quantity = sum(int(entry.get("Quantity", "1")) for entry in collection)

    tooltips = {
        "Toy #": "Hot Wheels interne Modellnummer",
        "Model Name": "Name des Modells",
        "Year": "Erscheinungsjahr",
        "Series": "Serie oder Line, z. B. Mainline",
        "Quantity": "Wie oft du dieses Modell besitzt"
    }

    series_colors = {
        "mainline": "#e6f0ff",
        "premium": "#f0f0f0",
        "team transport": "#f5e6ff",
        "real riders": "#e9ffe6",
        "boulevard": "#fff6e6",
        "basic": "#fdfdfd"
    }

    all_series = sorted({normalize_series_for_view(entry.get("Series", "Unbekannt")) for entry in collection if entry.get("Series")})
    series_options = "".join(f'<option value="{s}">{s}</option>' for s in all_series)

    rows = ""
    for entry in collection:
        raw_series = entry.get("Series", "")
        norm_series = normalize_series_for_view(raw_series)
        series = norm_series.lower()
        color = series_colors.get(series, "#ffffff")
        row = f'<tr data-series="{series}" style="background-color:{color}">'
        for col in headers:
            val = entry.get(col, "")
            if col == "Series":
                val = norm_series
            if col == "Quantity" and val.isdigit():
                toy_id = entry.get("Toy #", "")
                val = textwrap.dedent(f"""\
                    <div style='display:flex;align-items:center;gap:4px'>
                        <button onclick="adjustQuantity('{toy_id}','-')">-</button>
                        <span>{val}x</span>
                       <button onclick="adjustQuantity('{toy_id}','+')">+</button>
                    </div>
                """)
            tooltip = tooltips.get(col, col)
            row += f'<td title="{tooltip}">{val}</td>'
        row += "</tr>"
        rows += row

    html = f"""
    <html>
    <head>
        <title>Meine Hot Wheels Sammlung</title>
        <style>
            body {{
                font-family: -apple-system, sans-serif;
                padding: 20px;
                background: #fafafa;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
                cursor: pointer;
            }}
            tbody tr:hover {{
                background-color: #f0f0f0;
            }}
            input[type="text"], select {{
                margin-bottom: 10px;
                padding: 5px;
                width: 100%;
                box-sizing: border-box;
            }}
            .summary {{
                margin-top: 20px;
                font-weight: bold;
            }}
            .legend {{
                margin-top: 40px;
                font-size: 0.95em;
            }}
            .legend span {{
                display:inline-block;
                width:16px;
                height:16px;
                border:1px solid #aaa;
                margin-right:6px;
            }}
            button {{
                cursor: pointer;
                font-size: 0.95em;
            }}
        </style>
        <script>
            function filterTable() {{
                let searchInput = document.getElementById("searchInput").value.toLowerCase();
                let selectedSeries = document.getElementById("seriesSelect").value.toLowerCase();
                let rows = document.querySelectorAll("tbody tr");

                rows.forEach(row => {{
                    let matchesSearch = [...row.cells].some(td =>
                        td.textContent.toLowerCase().includes(searchInput));
                    let matchesSeries = selectedSeries === "" || row.dataset.series === selectedSeries;
                    row.style.display = (matchesSearch && matchesSeries) ? "" : "none";
                }});
            }}

            function sortTable(colIndex) {{
                const table = document.querySelector("table");
                const rows = Array.from(table.querySelectorAll("tbody tr"));
                const asc = table.dataset.sortCol == colIndex && table.dataset.sortDir !== "asc";
                rows.sort((a, b) => {{
                    const valA = a.children[colIndex].textContent.trim();
                    const valB = b.children[colIndex].textContent.trim();
                    const isNum = !isNaN(valA) && !isNaN(valB);
                    return isNum
                        ? (asc ? valA - valB : valB - valA)
                        : (asc ? valA.localeCompare(valB) : valB.localeCompare(valA));
                }});
                table.dataset.sortCol = colIndex;
                table.dataset.sortDir = asc ? "asc" : "desc";
                const tbody = table.querySelector("tbody");
                rows.forEach(row => tbody.appendChild(row));
            }}

            function adjustQuantity(toy_number, model_name, photo, delta) {{
                const formData = new FormData();
                formData.append("toy_number", toy_number);
                formData.append("model_name", model_name);
                formData.append("photo", photo);
                formData.append("delta", delta);

                fetch("/adjust_quantity", {{
                    method: "POST",
                    body: formData
                }}).then(r => r.json()).then(data => {{
                    if (data.status === "ok") {{
                        location.reload();
                    }}
                }});
            }}
        </script>
    </head>
    <body>
        <h2>📦 Gesammelte Modelle</h2>

        <label for="searchInput">🔍 Suche:</label>
        <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Nach Modell, Jahr, Toy #...">

        <label for="seriesSelect">📂 Serie filtern:</label>
        <select id="seriesSelect" onchange="filterTable()">
            <option value="">Alle Serien anzeigen</option>
            {series_options}
        </select>

        <div class="summary">Gesamtzahl: {total_quantity} Modelle</div>

        <table data-sort-col="-1" data-sort-dir="asc">
            <thead>
                <tr>
                    {''.join(f'<th onclick="sortTable({i})" title="Sortieren">{h} ⬍</th>' for i, h in enumerate(headers))}
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>

        <br><a href="/form">⬅️ Zurück zum Formular</a>
        <br><a href="/download_csv" download>⬇️ CSV herunterladen</a>

        <div class="legend">
            <h3>🖍️ Farblegende:</h3>
            <ul style="list-style:none;padding:0;">
              <li><span style="background:#e6f0ff;"></span> Mainline</li>
              <li><span style="background:#f0f0f0;"></span> Premium</li>
              <li><span style="background:#f5e6ff;"></span> Team Transport</li>
              <li><span style="background:#e9ffe6;"></span> Real Riders</li>
              <li><span style="background:#fff6e6;"></span> Boulevard</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.get("/download_csv")
def download_csv():
    if not COLLECTION_PATH.exists():
        raise HTTPException(status_code=404, detail="Sammlung nicht gefunden")
    return FileResponse(COLLECTION_PATH, media_type='text/csv', filename="HotWheelsCollection.csv")

@router.get("/lost", response_class=HTMLResponse)
def show_missing():
    import re
    import csv
    from collections import defaultdict
    from pathlib import Path

    # Fallback-CSV für Toy # → Jahr
    fallback_years = {}
    fallback_path = Path("data/HotWheelsYear-Toy.csv")
    if fallback_path.exists():
        with open(fallback_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                toy = row.get("Toy #", "").strip()
                year = row.get("Year", "").strip()
                if toy and year.isdigit():
                    fallback_years[toy] = year

    # Serienbereinigung
    def normalize_series(series: str) -> str:
        if not series:
            return "Unbekannt"
        series = re.sub(
            r"(New for\s?\d{4}|New for|Kroger Exclusive|Exclusive|Walmart|2nd Color|"
            r"Target Exclusive|GameStop Exclusive|Multipack Exclusive|Best Buy|Super Treasure Hunt|"
            r"Treasure Hunt|Dollar General|Family Dollar|Family Day|Dollar Tree|Chinese New Year|"
            r"Day of the Dead|Halloween|Earth Day|Happy Birthday|Valentine'?s Day|"
            r"International Friendship Day|Ryu'?s Rides|New in Mainline|Mattel 80th Anniversary|"
            r"Leap Year|World Autism Awareness Day|World Braille Day|International Women'?s Day)",
            "",
            series,
            flags=re.IGNORECASE
        )
        series = re.sub(r"[^\w\s]", " ", series)  # Satzzeichen entfernen (! / etc.)
        series = re.sub(r"\s{2,}", " ", series)
        return series.strip()

    # Serienname + Jahr kombinieren
    def series_with_year(series: str, year: str) -> str:
        clean = normalize_series(series)
        return f"{clean} {year}".strip()

    db = load_database()
    collection = load_collection()
    collected_toys = {entry["Toy #"] for entry in collection}

    # Gruppieren nach bereinigter Serie + Jahr
    series_groups = defaultdict(list)
    for entry in db:
        toy_number = entry.get("Toy #", "").strip()
        raw_series = entry.get("Series", "").strip()
        raw_year = entry.get("Year", "").strip()
        model_name = entry.get("Model Name", "").strip()

        # Fallback für fehlendes Jahr
        year = raw_year if raw_year.isdigit() else fallback_years.get(toy_number, "Unbekannt")
        key = series_with_year(raw_series, year)

        series_groups[key].append({
            "Toy #": toy_number,
            "Model Name": model_name,
            "Collected": toy_number in collected_toys,
            "Year": year
        })

    # HTML-Aufbau
    html = """
    <html>
    <head>
        <title>Fehlende Modelle</title>
        <style>
            body { font-family: -apple-system, sans-serif; padding: 20px; background: #fdfdfd; }
            h2 { margin-top: 40px; }
            h3 { margin-top: 20px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 10px; }
            th, td { border: 1px solid #ccc; padding: 6px 10px; }
            th { background-color: #f2f2f2; }
            tr.missing { background-color: #ffecec; }
            tr.collected { background-color: #e7ffe7; }
            .progress-container {
                background: #ddd;
                border-radius: 4px;
                overflow: hidden;
                width: 100%;
                margin-bottom: 12px;
            }
            .progress-bar {
                background: #4caf50;
                padding: 4px 8px;
                color: white;
                font-weight: bold;
                font-size: 0.9em;
                text-align: left;
            }
            .stat-line {
                font-size: 0.9em;
                margin-bottom: 10px;
                color: #555;
            }
            .back-button {
                display: inline-block;
                padding: 6px 12px;
                background: #fff;
                border: 1px solid #ccc;
                border-radius: 6px;
                text-decoration: none;
                color: #333;
                font-size: 14px;
                margin: 10px 0 20px 0;
                box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
            }
        </style>
        <script>
            function toggleMissingOnly(checkbox) {
                const collectedRows = document.querySelectorAll("tr.collected");
                collectedRows.forEach(row => {
                    row.style.display = checkbox.checked ? "none" : "";
                });
            }
        </script>
    </head>
    <body>
        <h1>📉 Fehlende Modelle nach Serie + Jahr</h1>
        <a href="/form" class="back-button">⬅️ Zurück zum Formular</a><br>
        <label><input type="checkbox" onchange="toggleMissingOnly(this)"> Nur fehlende anzeigen</label><br><br>
    """

    # Sortieren: zuerst Serienname, dann Jahr numerisch
    def sort_key(series_key):
        parts = series_key.strip().rsplit(" ", 1)
        name = parts[0].lower()
        year = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 9999
        return (name, year)

    for series in sorted(series_groups.keys(), key=sort_key):
        items = series_groups[series]
        total = len(items)
        collected = sum(1 for x in items if x["Collected"])
        percent = int((collected / total) * 100) if total else 0
        missing = total - collected

        html += f"""
        <h3>🗂️ Serie: {series}</h3>
        <div class='progress-container'>
            <div class='progress-bar' style='width:{percent}%'>{percent}% gesammelt</div>
        </div>
        <div class='stat-line'>✅ {collected} gesammelt | ❌ {missing} fehlend (insgesamt: {total})</div>
        <table>
            <tr><th>Year</th><th>Toy #</th><th>Model Name</th><th>Status</th></tr>
        """

        for item in sorted(items, key=lambda x: x["Toy #"]):
            cls = "collected" if item["Collected"] else "missing"
            status = "✅ Gesammelt" if item["Collected"] else "❌ Fehlt"
            html += f"<tr class='{cls}'><td>{item['Year']}</td><td>{item['Toy #']}</td><td>{item['Model Name']}</td><td>{status}</td></tr>"

        html += "</table>"

    html += "</body></html>"
    return HTMLResponse(content=html)

# FastAPI Route: Vorschlagsliste für Toy #
@router.get("/toy_suggestions", response_class=HTMLResponse)
def toy_suggestions():
    db = load_database()
    toylist = sorted({entry["Toy #"] for entry in db if entry.get("Toy #")})
    html = "<datalist id='toylist'>" + "".join(f"<option value='{t}' />" for t in toylist) + "</datalist>"
    return HTMLResponse(content=html)

# FastAPI Route: Modellinfo (z. B. für Tooltip oder Smart-Vorschau)
@router.get("/toy_info")
def toy_info(toy_number: str):
    db = load_database()
    result = next((entry for entry in db if entry.get("Toy #") == toy_number), None)
    if result:
        return {
            "model_name": result.get("Model Name", "Unbekannt"),
            "year": result.get("Year", "Unbekannt"),
            "series": result.get("Series", "Unbekannt"),
            "photo": result.get("Photo", None)
        }
    raise HTTPException(status_code=404, detail="Modell nicht gefunden")

# FastAPI Route: Autocomplete für Modellnamen (optional)
@router.get("/autocomplete_model_names", response_class=HTMLResponse)
def autocomplete_model_names():
    db = load_database()
    names = sorted({entry["Model Name"] for entry in db if entry.get("Model Name")})
    html = "<datalist id='modellist'>" + "".join(f"<option value='{n}' />" for n in names) + "</datalist>"
    return HTMLResponse(content=html)

# Optional: Route zur Prüfung von Duplikaten (Debug oder UI-Hinweis)
@router.get("/check_duplicates")
def check_duplicates():
    collection = load_collection()
    counter = {}
    for entry in collection:
        key = (entry.get("Toy #"), entry.get("Photo"), entry.get("Model Name"))
        counter[key] = counter.get(key, 0) + int(entry.get("Quantity", "1"))
    duplicates = [k for k, v in counter.items() if v > 1]
    return {"duplicates": duplicates}

# NEUE ROUTE: Bulk-Formular-Eingabe wie "HYP47, 2x HNW39"
@router.post("/collect_bulk")
def collect_bulk_form(entries: str = Form(...)):
    results = []
    for raw in entries.split(","):
        part = raw.strip()
        if not part:
            continue
        if "x" in part:
            quantity, toy_number = part.lower().split("x")
            quantity = int(quantity.strip())
            toy_number = toy_number.strip().upper()
        elif part.lower().startswith("x"):
            # z. B. "x3 HNW39"
            split = part.lower().split(" ")
            quantity = int(split[0][1:])
            toy_number = split[1].strip().upper()
        else:
            toy_number = part.upper()
            quantity = 1

        try:
            result = collect_model(CollectRequest(toy_number=toy_number, quantity=quantity))
            results.append(f"✅ {toy_number} ({quantity}x): Gespeichert")
        except HTTPException as e:
            results.append(f"❌ {toy_number}: {e.detail}")

    html_result = "<br>".join(results)
    return HTMLResponse(f"""
        <html><head><title>Ergebnis</title></head>
        <body style='font-family: -apple-system, sans-serif;'>
            <h2>🔁 Bulk-Speicherung abgeschlossen</h2>
            <p>{html_result}</p>
            <a href='/form'>⬅️ Zurück</a>
        </body></html>
    """)

@router.post("/adjust_quantity")
def adjust_quantity(
    toy_number: str = Form(...),
    delta: int = Form(...),
    photo: str = Form(""),
    model_name: str = Form("")
):
    collection = load_collection()
    updated = False
    new_val = None

    for entry in collection:
        if (
            entry["Toy #"] == toy_number and
            entry.get("Photo", "").strip() == photo.strip() and
            entry.get("Model Name", "").strip() == model_name.strip()
        ):
            current = int(entry.get("Quantity", "1"))
            new_val = max(current + delta, 1)
            entry["Quantity"] = str(new_val)
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Eintrag nicht gefunden")

    fieldnames = list(collection[0].keys())
    save_collection(collection, fieldnames)
    return {"status": "ok", "new_quantity": new_val}

@router.post("/update_quantity")
async def update_quantity(request: Request):
    data = await request.json()
    toy_number = data.get("toy_number")
    action = data.get("action")

    collection = load_collection()
    updated = False
    new_quantity = None

    for entry in collection:
        if entry["Toy #"] == toy_number:
            qty = int(entry.get("Quantity", "1"))
            if action == "increment":
                qty += 1
            elif action == "decrement" and qty > 1:
                qty -= 1
            entry["Quantity"] = str(qty)
            new_quantity = qty
            updated = True
            break

    if updated:
        save_collection(collection)
        return {"success": True, "quantity": new_quantity}
    else:
        return {"success": False, "error": "Toy # not found"}
    
@router.get("/compare", response_class=HTMLResponse)
def compare_progress():
    from collections import defaultdict

    db = load_database()
    collection = load_collection()

    def normalize_series(series: str) -> str:
        if not series:
            return "Unbekannt"
        series = re.sub(r"(New for\s?\d{4}|New for|Kroger Exclusive|Exclusive|Walmart|2nd Color|"
                    r"Target Exclusive|GameStop Exclusive|Multipack Exclusive|Best Buy|Super Treasure Hunt|"
                    r"Treasure Hunt|Dollar General|Family Dollar|Family Day|Dollar Tree|Chinese New Year|"
                    r"Day of the Dead|Halloween|Earth Day|Happy Birthday|Valentine'?s Day|"
                    r"International Friendship Day|Ryu'?s Rides|New in Mainline|Mattel 80th Anniversary|"
                    r"Leap Year|World Autism Awareness Day|World Braille Day|International Women'?s Day)",
                    "", series, flags=re.IGNORECASE)
        series = re.sub(r"[^\w\s]", " ", series)  # Sonderzeichen entfernen
        series = re.sub(r"\s{2,}", " ", series)    # doppelte Leerzeichen
        return series.strip()

    # Serienzählungen nach "Normierte Serie + Jahr"
    total_per_series = defaultdict(int)
    collected_per_series = defaultdict(int)

    for row in db:
        year = row.get("Year", "").strip()
        raw_series = row.get("Series", "").strip()
        norm_series = normalize_series(raw_series)
        key = f"{norm_series} {year}"
        total_per_series[key] += 1

    for row in collection:
        year = row.get("Year", "").strip()
        raw_series = row.get("Series", "").strip()
        norm_series = normalize_series(raw_series)
        key = f"{norm_series} {year}"
        collected_per_series[key] += int(row.get('Quantity', 1))

    # HTML-Ausgabe
    html = """
    <html>
    <head>
        <title>Vergleich</title>
        <style>
            body { font-family: -apple-system, sans-serif; padding: 20px; background: #fafafa; }
            h2 { margin-bottom: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { padding: 6px 10px; border: 1px solid #ccc; text-align: left; }
            progress { width: 160px; height: 16px; }
        </style>
    </head>
    <body>
        <h2>📊 Sammlungs-Fortschritt pro Serie</h2>
        <table>
            <tr><th>Serie</th><th>Gesamt</th><th>Gesammelt</th><th>Fortschritt</th></tr>
    """

    for series in sorted(total_per_series.keys()):
        total = total_per_series[series]
        collected = collected_per_series.get(series, 0)
        percent = int((collected / total) * 100) if total else 0

        if percent >= 75:
            color = "#4caf50"  # grün
        elif percent >= 40:
            color = "#ffca28"  # gelb
        else:
            color = "#ef5350"  # rot

        html += f"""
        <tr>
            <td>{series}</td>
            <td>{total}</td>
            <td>{collected}</td>
            <td>
                <div title='{collected} von {total} gesammelt' style='display:flex;align-items:center;gap:6px;'>
                    <progress value='{percent}' max='100' style='accent-color:{color};'></progress>
                    <span>{percent}%</span>
                </div>
            </td>
        </tr>
        """

    html += "</table><br><a href='/form'>⬅️ Zurück zum Formular</a></body></html>"
    return HTMLResponse(content=html)

@router.post("/create_page")
def create_page(page_name: str = Form(...), page_content: str = Form(...)):
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "", page_name)
    filepath = Path("templates") / f"{safe_name}.html"
    filepath.write_text(page_content, encoding="utf-8")
    return HTMLResponse(content=f"✅ Seite '{safe_name}.html' wurde erstellt.", status_code=201)

@router.get("/{filename}", response_class=HTMLResponse)
def show_created_page(filename: str):
    filepath = Path("templates") / filename
    if not filepath.exists():
        return HTMLResponse(content="❌ Seite nicht gefunden.", status_code=404)
    return HTMLResponse(content=filepath.read_text(encoding="utf-8"))


@router.get("/available_pages")
def available_pages():
    pages = [f.name for f in Path("templates").glob("*.html") if f.name != "form_collect.html"]
    return {"pages": pages}

# router exportieren
__all__ = ["router"]
