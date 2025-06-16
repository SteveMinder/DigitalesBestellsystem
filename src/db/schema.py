# src/db/schema.py
# Erstellt alle Tabellen in der SQLite-Datenbank

import sqlite3
from . import DB_PATH  # <- Zugriff auf DB_PATH aus __init__.py

def create_tables():
    """
    Erstellt die benötigten Tabellen für das Restaurant-Bestellsystem,
    falls sie noch nicht existieren.
    """
    # Verbindung zur SQLite-Datenbank herstellen
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # SQL-Skript zur Erstellung aller Tabellen
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS kategorie (
        kategorieID INTEGER PRIMARY KEY AUTOINCREMENT,
        bezeichnung TEXT
    );

    CREATE TABLE IF NOT EXISTS produkt (
    produktID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    beschreibung TEXT,
    name_fr TEXT,
    beschreibung_fr TEXT,
    name_en TEXT,
    beschreibung_en TEXT,
    preis REAL,
    typ TEXT,
    groesse TEXT,
    vegetarisch BOOLEAN,
    vegan BOOLEAN,
    herkunft TEXT,
    verfuegbar BOOLEAN,
    kategorieID INTEGER,
    FOREIGN KEY (kategorieID) REFERENCES kategorie(kategorieID)
);

    CREATE TABLE IF NOT EXISTS tisch (
        tischID INTEGER PRIMARY KEY AUTOINCREMENT,
        sitzplaetze INTEGER
    );

    CREATE TABLE IF NOT EXISTS bestellung (
        bestellungID INTEGER PRIMARY KEY AUTOINCREMENT,
        tischID INTEGER,
        zeitstempel TEXT,
        status TEXT,
        FOREIGN KEY (tischID) REFERENCES tisch(tischID)
    );

    CREATE TABLE IF NOT EXISTS bestellposition (
        positionID INTEGER PRIMARY KEY AUTOINCREMENT,
        bestellungID INTEGER,
        produktID INTEGER,
        menge INTEGER,
        FOREIGN KEY (bestellungID) REFERENCES bestellung(bestellungID),
        FOREIGN KEY (produktID) REFERENCES produkt(produktID)
    );
    """)

    # Änderungen speichern und Verbindung schließen
    conn.commit()
    conn.close()

    print("Tabellen wurden erfolgreich erstellt.")