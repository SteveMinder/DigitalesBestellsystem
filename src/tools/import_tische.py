# src/tools/import_tische.py
# ----------------------------------------------------
# Importiert Tische aus CSV und synchronisiert die Datenbank:
# - Fügt neue Tische ein
# - Überspringt bereits vorhandene
# ----------------------------------------------------

import os
import sys
import csv
import sqlite3

# 🔧 Projektpfad verfügbar machen
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, project_root)

from src.db import DB_PATH  # ❗️Pfad belassen wie im Original

def importiere_tische(dateipfad):
    """
    Importiert Tischdaten aus einer CSV-Datei in die Datenbank:
    - Neue Tische werden eingefügt
    - Bereits existierende Einträge übersprungen
    """
    if not os.path.exists(dateipfad):
        print(f"❌ Fehler: Datei nicht gefunden: {dateipfad}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(dateipfad, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        hinzugefuegt = 0
        uebersprungen = 0

        for row in reader:
            tisch_id = int(row["tischID"])
            sitzplaetze = int(row["sitzplaetze"])

            cursor.execute("SELECT COUNT(*) FROM tisch WHERE tischID = ?", (tisch_id,))
            exists = cursor.fetchone()[0] > 0

            if exists:
                print(f"↪️ Tisch {tisch_id} existiert bereits – übersprungen.")
                uebersprungen += 1
                continue

            cursor.execute(
                "INSERT INTO tisch (tischID, sitzplaetze) VALUES (?, ?)",
                (tisch_id, sitzplaetze)
            )
            hinzugefuegt += 1
            print(f"✅ Tisch {tisch_id} mit {sitzplaetze} Sitzplätzen importiert.")

    conn.commit()
    conn.close()

    print(f"\n📊 Tisch-Import Zusammenfassung:")
    print(f"   ✅ Neu hinzugefügt:   {hinzugefuegt}")
    print(f"   ↪️  Übersprungen:       {uebersprungen}")

if __name__ == "__main__":
    csv_pfad = os.path.join(current_dir, "tische.csv")
    importiere_tische(csv_pfad)
