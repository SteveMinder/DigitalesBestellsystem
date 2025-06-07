# main.py
# -------------------------
# Einstiegspunkt für das Restaurant-Bestellsystem
# Dieser Code bereitet die Datenbank vor (Tabellen + Testdaten)
# und startet anschließend die grafische Benutzeroberfläche (GUI)
# -------------------------

# Importiere die Funktionen zum Erstellen der DB und Dummy-Daten
from db import schema

# Importiere die GUI-Startfunktion
# from gui.main_window import start_app

def main():
    """
    Hauptfunktion des Programms.
    Führt folgende Schritte aus:
    1. Erstellt (falls nötig) die SQLite-Datenbank mit allen Tabellen.
    2. Fügt ein paar Beispiel-Datensätze (Kategorien, Produkte) ein.
    3. Startet das GUI-Fenster für die Benutzeroberfläche.
    """
    print("Initialisiere Datenbank ...")
    schema.create_tables()       # Tabellen erstellen (falls noch nicht da)

    print("Starte GUI ...")
 #   start_app()  # Starte grafische Oberfläche

# Diese Zeile stellt sicher, dass das Programm nur startet,
# wenn die Datei direkt ausgeführt wird (nicht bei Import)
if __name__ == "__main__":
    main()

