# src/tools/init_kategorien.py

import sqlite3
from src.db import DB_PATH

def init_kategorien():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    kategorien = [
        (1, "Hauptgerichte"),
        (2, "Getränke"),
        (3, "Desserts")
    ]

    for kategorieID, bezeichnung in kategorien:
        cursor.execute("""
            INSERT OR IGNORE INTO kategorie (kategorieID, bezeichnung)
            VALUES (?, ?)
        """, (kategorieID, bezeichnung))

    conn.commit()
    conn.close()
    print("✅ Kategorien wurden eingefügt (oder waren bereits vorhanden).")

if __name__ == "__main__":
    init_kategorien()
