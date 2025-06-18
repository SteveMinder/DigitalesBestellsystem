# src/main.py
# --------------------------------------------------
# Einstiegspunkt für das Restaurant-Bestellsystem.
# Initialisiert die Datenbank und startet die GUI.
# --------------------------------------------------

from db import schema
from tools.init_kategorien import init_kategorien
from tools.import_products import importiere_csv
from gui.main_window import start_app
from src.tools.import_tische import importiere_tische

def main():
    """
    Führt die Initialisierung des Systems aus:
    1. Erstellt die SQLite-Datenbank mit allen Tabellen (falls nicht vorhanden).
    2. Fügt Standard-Kategorien in die Datenbank ein.
    3. Importiert Tische und Produkte aus CSV-Dateien.
    4. Startet die grafische Benutzeroberfläche (GUI).
    """
    print("📦 Initialisiere Datenbank...")
    schema.create_tables()

    print("📁 Initialisiere Kategorien...")
    init_kategorien()

    print("📁 Initialisiere Tische...")
    importiere_tische("src/tools/tische.csv")

    print("🛒 Importiere Produkte aus CSV...")
    importiere_csv("src/tools/produkte.csv")

    print("🖥️ Starte GUI...")
    start_app()

if __name__ == "__main__":
    main()