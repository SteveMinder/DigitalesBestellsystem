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
    if not os.path.exists(dateipfad):
        print(f"❌ Fehler: Datei nicht gefunden: {dateipfad}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(dateipfad, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        csv_keys = set()
        neu_importiert = 0
        wieder_aktiviert = 0

        for row in reader:
            name = row["name"]
            groesse = row["groesse"] or ""
            preis = float(row["preis"])
            name_key = f"{name}_{groesse}_{preis:.2f}"
            csv_keys.add(name_key)

            cursor.execute(
                "SELECT COUNT(*) FROM produkt WHERE name = ? AND groesse = ? AND preis = ?",
                (name, groesse, preis)
            )
            exists = cursor.fetchone()[0] > 0

            if exists:
                cursor.execute(
                    "UPDATE produkt SET verfuegbar = 1 WHERE name = ? AND groesse = ? AND preis = ?",
                    (name, groesse, preis)
                )
                wieder_aktiviert += 1
                print(f"♻️ Produkt reaktiviert: {name} {groesse} ({preis:.2f} CHF)")
                continue

            cursor.execute("""
                INSERT INTO produkt (
                    name, name_fr, name_en,
                    beschreibung, beschreibung_fr, beschreibung_en,
                    preis, typ, groesse, vegetarisch, vegan,
                    herkunft, verfuegbar, kategorieID
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                row.get("name_fr") or None,
                row.get("name_en") or None,
                row["beschreibung"],
                row.get("beschreibung_fr") or None,
                row.get("beschreibung_en") or None,
                preis,
                row["typ"],
                groesse,
                bool(int(row["vegetarisch"])),
                bool(int(row["vegan"])),
                row["herkunft"] or None,
                True,
                int(row["kategorieID"])
            ))
            neu_importiert += 1
            print(f"✅ Produkt importiert: {name} {groesse} ({preis:.2f} CHF)")

    # 🧹 Deaktivieren nicht mehr vorhandener Produkte
    cursor.execute("SELECT name, groesse, preis FROM produkt")
    alle_db_keys = {
        f"{row[0]}_{row[1] or ''}_{row[2]:.2f}" for row in cursor.fetchall()
    }
    zu_deaktivieren = alle_db_keys - csv_keys
    deaktiviert = 0

    for key in zu_deaktivieren:
        name, groesse, preis = key.rsplit("_", 2)
        cursor.execute(
            "UPDATE produkt SET verfuegbar = 0 WHERE name = ? AND groesse = ? AND preis = ?",
            (name, groesse, float(preis))
        )
        deaktiviert += 1
        print(f"⛔ Produkt deaktiviert: {name} {groesse}")

    conn.commit()
    conn.close()

    print(f"\n📊 Import-Zusammenfassung:")
    print(f"   ✅ Neu importiert:      {neu_importiert}")
    print(f"   ♻️  Wieder aktiviert:    {wieder_aktiviert}")
    print(f"   ⛔ Deaktiviert:         {deaktiviert}")
    print(f"   📦 Aktive Produkte:     {len(csv_keys)}")

if __name__ == "__main__":
    csv_pfad = os.path.join(os.path.dirname(__file__), "produkte.csv")
    importiere_csv(csv_pfad)
