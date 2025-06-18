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
    Hauptfunktion des Programms:
    1. Erstellt (falls nötig) die SQLite-Datenbank mit allen Tabellen.
    2. Fügt Standard-Kategorien ein (falls noch nicht vorhanden).
    3. Importiert Produkte aus CSV-Datei.
    4. Startet die grafische Benutzeroberfläche.
    """
    print("📦 Initialisiere Datenbank...")
    schema.create_tables()

    print("📁 Initialisiere Kategorien...")
    init_kategorien()

    print("📁 Initialisiere Tische...")
    importiere_tische("src/tools/tische.csv")

    print("🛒 Importiere Produkte aus CSV...")
    importiere_csv("tools/produkte.csv")

    print("🖥️ Starte GUI...")
    start_app()

if __name__ == "__main__":
    main()