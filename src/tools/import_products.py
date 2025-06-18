# tools/import_products.py
# ----------------------------------------------------
# Importiert Produkte aus CSV und synchronisiert die Datenbank:
# - Fügt neue Produkte ein
# - Reaktiviert deaktivierte Produkte
# - Deaktiviert veraltete Produkte
# ----------------------------------------------------

import os
import sys
import csv
import sqlite3

# 🔧 Projektpfad verfügbar machen
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

# ✅ DB_PATH importieren
from src.db import DB_PATH

def importiere_csv(dateipfad):
    """
    Liest Produkte aus einer CSV-Datei und gleicht sie mit der Datenbank ab:
    - Neue Produkte werden eingefügt
    - Bereits existierende reaktiviert
    - Nicht mehr enthaltene Produkte deaktiviert
    """
    if not os.path.exists(dateipfad):
        print(f"❌ Fehler: Datei nicht gefunden: {dateipfad}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(dateipfad, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        csv_namen = set()
        neu_importiert = 0
        wieder_aktiviert = 0

        for row in reader:
            name = row["name"]
            csv_namen.add(name)

            cursor.execute("SELECT COUNT(*) FROM produkt WHERE name = ?", (name,))
            exists = cursor.fetchone()[0] > 0

            if exists:
                cursor.execute("UPDATE produkt SET verfuegbar = 1 WHERE name = ?", (name,))
                wieder_aktiviert += 1
                print(f"♻️ Produkt reaktiviert: {name}")
                continue

            cursor.execute("""
                INSERT INTO produkt (
                    name, name_fr, name_en,
                    beschreibung, beschreibung_fr, beschreibung_en,
                    preis, typ, groesse, vegetarisch, vegan,
                    herkunft, verfuegbar, kategorieID
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["name"],
                row.get("name_fr") or None,
                row.get("name_en") or None,
                row["beschreibung"],
                row.get("beschreibung_fr") or None,
                row.get("beschreibung_en") or None,
                float(row["preis"]),
                row["typ"],
                row["groesse"] or None,
                bool(int(row["vegetarisch"])),
                bool(int(row["vegan"])),
                row["herkunft"] or None,
                True,
                int(row["kategorieID"])
            ))
            neu_importiert += 1
            print(f"✅ Produkt importiert: {name}")

    # 🧹 Deaktivieren nicht mehr vorhandener Produkte
    cursor.execute("SELECT name FROM produkt")
    alle_db_namen = {row[0] for row in cursor.fetchall()}
    zu_deaktivieren = alle_db_namen - csv_namen

    deaktiviert = 0
    for name in zu_deaktivieren:
        cursor.execute("UPDATE produkt SET verfuegbar = 0 WHERE name = ?", (name,))
        deaktiviert += 1
        print(f"⛔ Produkt deaktiviert: {name}")

    conn.commit()
    conn.close()

    print(f"\n📊 Import-Zusammenfassung:")
    print(f"   ✅ Neu importiert:      {neu_importiert}")
    print(f"   ♻️  Wieder aktiviert:    {wieder_aktiviert}")
    print(f"   ⛔ Deaktiviert:         {deaktiviert}")
    print(f"   📦 Aktive Produkte:     {len(csv_namen)}")

if __name__ == "__main__":
    csv_pfad = os.path.join(os.path.dirname(__file__), "produkte.csv")
    importiere_csv(csv_pfad)