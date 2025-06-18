# tools/init_kategorien.py
# --------------------------------------------------
# Fügt Standard-Kategorien in die Datenbank ein.
# Wird nur ausgeführt, wenn eine Kategorie noch fehlt.
# --------------------------------------------------

import sqlite3
from src.db import DB_PATH

def init_kategorien():
    """
    Fügt eine Liste vordefinierter Kategorien in die Tabelle 'kategorie' ein,
    falls diese dort noch nicht existieren (INSERT OR IGNORE).
    """
    kategorien = [
        (1, "Hauptgerichte"),
        (2, "Getränke"),
        (3, "Desserts"),
        (4, "Vorspeisen"),
        (5, "Alkoholhaltige Getränke")
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for kategorieID, bezeichnung in kategorien:
        cursor.execute("""
            INSERT OR IGNORE INTO kategorie (kategorieID, bezeichnung)
            VALUES (?, ?)
        """, (kategorieID, bezeichnung))

    conn.commit()
    conn.close()
    print("✅ Kategorien wurden eingefügt (oder waren bereits vorhanden).")
