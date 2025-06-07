# src/gui/main_window.py
# ------------------------------------------------------------
# Überarbeitetes GUI gemäß Mockup: Navigation + Produktanzeige
# ------------------------------------------------------------
from src.gui import styles
import tkinter as tk
import sqlite3
from src.db import DB_PATH


# -----------------------------
# Kategorie-Navigation und Anzeige
# -----------------------------
def lade_produkte_nach_kategorie(kategorieID):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, beschreibung, preis FROM produkt
        WHERE verfuegbar = 1 AND kategorieID = ?
        ORDER BY name
    """, (kategorieID,))
    daten = cursor.fetchall()
    conn.close()
    return daten


def zeige_kategorie(kategorieID, inhalt_frame, titel_label):
    # Inhalt löschen
    for widget in inhalt_frame.winfo_children():
        widget.destroy()

    # Titel setzen
    kategorie_namen = {
        1: "Hauptgerichte",
        2: "Getränke",
        3: "Desserts",
        4: "Vorspeisen"
    }
    titel_label.config(text=kategorie_namen.get(kategorieID, "Produkte"))

    # Produkte laden und anzeigen
    produkte = lade_produkte_nach_kategorie(kategorieID)
    for name, beschr, preis in produkte:
        frame = tk.Frame(inhalt_frame, **styles.STYLE_FRAME)
        frame.pack(fill="x", padx=10, pady=5, expand=True)

        tk.Label(frame, text=name, **styles.STYLE_PRODUKTNAME).pack(anchor="w")
        tk.Label(frame, text=beschr, **styles.STYLE_BESCHREIBUNG).pack(anchor="w")
        tk.Label(frame, text=f"{preis:.2f} €", **styles.STYLE_PREIS).pack(anchor="e")


# -----------------------------
# Start der App
# -----------------------------
def start_app():
    root = tk.Tk()
    root.title("Zum hungrigen Bären")
    root.geometry("800x600")
    root.configure(bg=styles.FARBE_HINTERGRUND)

    # Layout: Links Navigation, rechts Inhalt
    nav_frame = tk.Frame(root, width=200, bg=styles.FARBE_KATEGORIE)
    nav_frame.pack(side="left", fill="y")

    content_frame = tk.Frame(root, bg=styles.FARBE_HINTERGRUND)
    content_frame.pack(side="right", expand=True, fill="both")

    titel_label = tk.Label(content_frame, text="", **styles.STYLE_TITEL)
    titel_label.pack(anchor="w", padx=10)

    # Scrollbarer Inhaltsbereich
    canvas = tk.Canvas(content_frame, **styles.STYLE_CANVAS)
    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scrollable_frame = tk.Frame(canvas, bg=styles.FARBE_HINTERGRUND)
    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def on_resize(event):
        canvas.itemconfig(window_id, width=event.width)

    scrollable_frame.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_resize)

    # Navigations-Buttons
    buttons = [
        ("Vorspeisen", 4),
        ("Hauptgerichte", 1),
        ("Desserts", 3),
        ("Getränke", 2),
    ]

    for label, kat_id in buttons:
        btn = tk.Button(nav_frame, text=label, command=lambda k=kat_id: zeige_kategorie(k, scrollable_frame, titel_label), **styles.STYLE_BUTTON)
        btn.pack(fill="x")

    # Warenkorb-Platzhalter
    tk.Button(nav_frame, text="🛒 Warenkorb", **styles.STYLE_BUTTON).pack(fill="x", side="bottom")

    # Standardanzeige (z.B. Hauptgerichte)
    zeige_kategorie(1, scrollable_frame, titel_label)

    root.mainloop()
