# src/gui/main_window.py
# ------------------------------------------------------------
# Überarbeitetes GUI gemäß Mockup: Navigation + Produktanzeige + Warenkorb
# ------------------------------------------------------------
from src.gui import styles
import tkinter as tk
import sqlite3
from src.db import DB_PATH
from src.models.restaurant_klassen import Bestellung, Bestellposition, Speise, Getraenk

# -----------------------------
# Globale Warenkorb-Instanz
# -----------------------------
aktuelle_bestellung = Bestellung(bestellungID=1, tischID=1)


# -----------------------------
# Kategorie-Navigation und Anzeige
# -----------------------------
def lade_produkte_nach_kategorie(kategorieID):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT produktID, name, beschreibung, preis, typ, groesse, vegetarisch, vegan, herkunft
        FROM produkt
        WHERE verfuegbar = 1 AND kategorieID = ?
        ORDER BY name
    """, (kategorieID,))
    daten = cursor.fetchall()
    conn.close()
    return daten


def zeige_kategorie(kategorieID, inhalt_frame, titel_label):
    for widget in inhalt_frame.winfo_children():
        widget.destroy()

    kategorie_namen = {
        1: "Hauptgerichte",
        2: "Getränke",
        3: "Desserts",
        4: "Vorspeisen"
    }
    titel_label.config(text=kategorie_namen.get(kategorieID, "Produkte"))

    produkte = lade_produkte_nach_kategorie(kategorieID)
    for produktID, name, beschr, preis, typ, groesse, vegetarisch, vegan, herkunft in produkte:
        frame = tk.Frame(inhalt_frame, **styles.STYLE_FRAME)
        frame.pack(fill="x", padx=10, pady=5, expand=True)

        tk.Label(frame, text=name, **styles.STYLE_PRODUKTNAME).pack(anchor="w")
        tk.Label(frame, text=beschr, **styles.STYLE_BESCHREIBUNG).pack(anchor="w")
        tk.Label(frame, text=f"{preis:.2f} €", **styles.STYLE_PREIS).pack(anchor="e")

        def hinzufuegen(produktID=produktID, name=name, beschr=beschr, preis=preis,
                        kategorieID=kategorieID, typ=typ, groesse=groesse,
                        vegetarisch=vegetarisch, vegan=vegan, herkunft=herkunft):
            if typ == "Getränk":
                produkt = Getraenk(produktID, name, beschr, preis, kategorieID, True, groesse)
            else:
                produkt = Speise(produktID, name, beschr, preis, kategorieID, True,
                                 bool(vegetarisch), bool(vegan), False, herkunft)

            aktuelle_bestellung.hinzufuegen(produkt, 1)
            print(f"➕ '{name}' zum Warenkorb hinzugefügt.")

        tk.Button(frame, text="+ Hinzufügen", command=hinzufuegen, bg=styles.FARBE_PRIMÄR, fg="white").pack(anchor="e", pady=3)


# -----------------------------
# Warenkorb anzeigen
# -----------------------------
def zeige_warenkorb(inhalt_frame):
    for widget in inhalt_frame.winfo_children():
        widget.destroy()

    tk.Label(inhalt_frame, text="Warenkorb", **styles.STYLE_TITEL).pack(anchor="w", padx=10, pady=10)

    for pos in aktuelle_bestellung.positionen:
        frame = tk.Frame(inhalt_frame, **styles.STYLE_FRAME)
        frame.pack(fill="x", padx=10, pady=5)

        header = tk.Frame(frame, bg=styles.FARBE_KARTE)
        header.pack(fill="x")

        tk.Label(header, text=f"{pos.menge}× {pos.produkt.name}", **styles.STYLE_PRODUKTNAME).pack(anchor="w", side="left")
        tk.Label(header, text=f"{pos.teilpreis():.2f} €", **styles.STYLE_PREIS).pack(anchor="e", side="right")

        def loesche_pos(p=pos):
            aktuelle_bestellung.loeschen(p.produkt)
            zeige_warenkorb(inhalt_frame)

        tk.Button(frame, text="Entfernen", command=loesche_pos, bg="red", fg="white", font=("Segoe UI", 9)).pack(anchor="e", pady=2)

    gesamt = aktuelle_bestellung.gesamtpreis()
    tk.Label(inhalt_frame, text=f"Gesamt: {gesamt:.2f} €", **styles.STYLE_PREIS).pack(anchor="e", padx=10, pady=10)


# -----------------------------
# Start der App
# -----------------------------
def start_app():
    root = tk.Tk()
    root.title("Zum hungrigen Bären")
    root.geometry("800x600")
    root.configure(bg=styles.FARBE_HINTERGRUND)

    nav_frame = tk.Frame(root, width=200, bg=styles.FARBE_KATEGORIE)
    nav_frame.pack(side="left", fill="y")

    content_frame = tk.Frame(root, bg=styles.FARBE_HINTERGRUND)
    content_frame.pack(side="right", expand=True, fill="both")

    titel_label = tk.Label(content_frame, text="", **styles.STYLE_TITEL)
    titel_label.pack(anchor="w", padx=10)

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

    buttons = [
        ("Vorspeisen", 4),
        ("Hauptgerichte", 1),
        ("Desserts", 3),
        ("Getränke", 2),
    ]

    for label, kat_id in buttons:
        btn = tk.Button(nav_frame, text=label, command=lambda k=kat_id: zeige_kategorie(k, scrollable_frame, titel_label), **styles.STYLE_BUTTON)
        btn.pack(fill="x")

    tk.Button(nav_frame, text="🛒 Warenkorb", command=lambda: zeige_warenkorb(scrollable_frame), **styles.STYLE_BUTTON).pack(fill="x", side="bottom")

    zeige_kategorie(1, scrollable_frame, titel_label)
    root.mainloop()
