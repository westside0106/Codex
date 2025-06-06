from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import csv

app = FastAPI()

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

@app.post("/collect")
def collect_model(data: CollectRequest):
    db = load_database()
    collection = load_collection()

    matches = [entry for entry in db if entry["Toy #"] == data.toy_number]
    if not matches:
        raise HTTPException(status_code=404, detail="Modell nicht gefunden")

    new_entry = matches[0]
    new_entry["Quantity"] = str(data.quantity)

    # Prüfen ob genau diese Farbvariante schon existiert
    already_in = False
    for entry in collection:
        if entry["Toy #"] == new_entry["Toy #"] and entry.get("Photo") == new_entry.get("Photo"):
            entry["Quantity"] = str(int(entry.get("Quantity", "1")) + data.quantity)
            already_in = True
            break

    if not already_in:
        collection.append(new_entry)

    fieldnames = list(collection[0].keys())
    save_collection(collection, fieldnames)
    return {"message": "✅ Modell gespeichert", "toy_number": data.toy_number, "quantity": data.quantity}
