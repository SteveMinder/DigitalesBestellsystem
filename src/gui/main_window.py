# src/gui/main_window.py
# ------------------------------------------------------------
# GUI-Startfenster: Anzeige der Speise- und Getränkekarte
# mit Gruppierung nach Kategorie (z.B. Hauptgerichte, Getränke)
# ------------------------------------------------------------

import tkinter as tk
import sqlite3

# ✅ DB_PATH importieren
from src.db import DB_PATH


def lade_produkte():
    """Lade alle Produkte aus der Datenbank, inklusive Status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.name, p.beschreibung, p.preis, k.bezeichnung, p.verfuegbar
        FROM produkt p
        JOIN kategorie k ON p.kategorieID = k.kategorieID
        ORDER BY k.kategorieID, p.name
    """)
    daten = cursor.fetchall()
    conn.close()
    return daten


def start_app():
    print("🔵 GUI wurde gestartet.")
    root = tk.Tk()
    root.title("Digitale Speisekarte")
    root.geometry("600x600")

    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    produkte = lade_produkte()
    print(f"🔍 {len(produkte)} Produkte aus DB geladen.")
    aktuelle_kategorie = None

    for name, beschreibung, preis, kategorie, verfuegbar in produkte:
        if kategorie != aktuelle_kategorie:
            lbl_kat = tk.Label(scroll_frame, text=kategorie, font=("Arial", 16, "bold"), pady=10)
            lbl_kat.pack(anchor="w")
            aktuelle_kategorie = kategorie

        frame = tk.Frame(scroll_frame, bd=1, relief="solid", padx=10, pady=5)
        frame.pack(fill="x", padx=10, pady=5)

        lbl_name = tk.Label(frame, text=name, font=("Arial", 12, "bold"))
        lbl_name.pack(anchor="w")

        lbl_beschr = tk.Label(frame, text=beschreibung, font=("Arial", 10), fg="gray")
        lbl_beschr.pack(anchor="w")

        lbl_preis = tk.Label(frame, text=f"Preis: {preis:.2f} €", font=("Arial", 10, "italic"))
        lbl_preis.pack(anchor="w")

        status = "✅ Verfügbar" if verfuegbar else "⛔ Nicht verfügbar"
        lbl_status = tk.Label(frame, text=status, font=("Arial", 9, "italic"), fg="green" if verfuegbar else "red")
        lbl_status.pack(anchor="w")

    root.mainloop()


# Optionaler Direktstart
if __name__ == "__main__":
    start_app()
