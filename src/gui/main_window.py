# src/gui/main_window.py
# ------------------------------------------------------------
# GUI mit Grid-Layout für Produktanzeige und Tisch-Auswahl
# ------------------------------------------------------------
from src.gui import styles
import tkinter as tk
from src.models.restaurant_klassen import Warenkorb, Produkt
import sqlite3
from src.db import DB_PATH
from datetime import datetime

warenkorb = Warenkorb()
sprache_var = None
tisch_var_str = None
tisch_mapping = {}
aktuelle_kategorieID = 1
scrollable_frame = None
canvas = None
window_id = None

TEXTS = {
    "de": {
        "Hauptgerichte": "Hauptgerichte",
        "Getränke": "Getränke",
        "Desserts": "Desserts",
        "Vorspeisen": "Vorspeisen",
        "Produkte": "Produkte",
        "Warenkorb": "Warenkorb",
        "Hinweis": "Hinweis",
        "Vegetarisch": "Vegetarisch",
        "Vegan": "Vegan",
        "Herkunft": "Herkunft",
        "Hinzufügen": "+ Hinzufügen",
        "Entfernen": "Entfernen",
        "Gesamt": "Gesamt",
        "Tisch": "Tisch"
    },
    "fr": {
        "Hauptgerichte": "Plats principaux",
        "Getränke": "Boissons",
        "Desserts": "Desserts",
        "Vorspeisen": "Entrées",
        "Produkte": "Produits",
        "Warenkorb": "Panier",
        "Hinweis": "Remarque",
        "Vegetarisch": "Végétarien",
        "Vegan": "Vegan",
        "Herkunft": "Origine",
        "Hinzufügen": "+ Ajouter",
        "Entfernen": "Supprimer",
        "Gesamt": "Total",
        "Tisch": "Table"
    },
    "en": {
        "Hauptgerichte": "Main Courses",
        "Getränke": "Drinks",
        "Desserts": "Desserts",
        "Vorspeisen": "Starters",
        "Produkte": "Products",
        "Warenkorb": "Cart",
        "Hinweis": "Note",
        "Vegetarisch": "Vegetarian",
        "Vegan": "Vegan",
        "Herkunft": "Origin",
        "Hinzufügen": "+ Add",
        "Entfernen": "Remove",
        "Gesamt": "Total",
        "Tisch": "Table"
    }
}

# Kategorie-IDs
KATEGORIEN = {
    1: "Hauptgerichte",
    2: "Getränke",
    3: "Desserts",
    4: "Vorspeisen"
}

# Tisch-Auswahl (Anzeige + Mapping)
def lade_tisch_anzeigen():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT tischID, sitzplaetze FROM tisch ORDER BY tischID")
    daten = cursor.fetchall()
    conn.close()
    anzeigen = [f"Tisch {tid} ({plaetze} Plätze)" for tid, plaetze in daten]
    id_map = {f"Tisch {tid} ({plaetze} Plätze)": tid for tid, plaetze in daten}
    return anzeigen, id_map

# Bestellungen aus DB laden
def lade_bestellungen_fuer_tisch(tisch_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT bestellungID, zeitstempel, status
        FROM bestellung
        WHERE tischID = ?
        ORDER BY zeitstempel DESC
    """, (tisch_id,))
    bestellungen = cursor.fetchall()

    ergebnis = []
    for bestellung_id, zeit, status in bestellungen:
        cursor.execute("""
            SELECT p.name, bp.menge, p.preis
            FROM bestellposition bp
            JOIN produkt p ON bp.produktID = p.produktID
            WHERE bp.bestellungID = ?
        """, (bestellung_id,))
        positionen = cursor.fetchall()
        ergebnis.append({
            "id": bestellung_id,
            "zeit": zeit,
            "status": status,
            "positionen": positionen
        })

    conn.close()
    return ergebnis

# Bestellung speichern
def bestellung_speichern():
    if not warenkorb.positionen:
        print("❗ Kein Produkt im Warenkorb.")
        return

    tisch_id = tisch_mapping.get(tisch_var_str.get())
    if not tisch_id:
        print("❗ Kein Tisch ausgewählt.")
        return

    zeit = datetime.now().isoformat()
    status = "offen"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO bestellung (tischID, zeitstempel, status) VALUES (?, ?, ?)",
        (tisch_id, zeit, status)
    )
    bestellung_id = cursor.lastrowid

    for pos in warenkorb.positionen:
        cursor.execute(
            "INSERT INTO bestellposition (bestellungID, produktID, menge) VALUES (?, ?, ?)",
            (bestellung_id, pos.produkt.produktID, pos.menge)
        )

    conn.commit()
    conn.close()
    print(f"✅ Bestellung {bestellung_id} gespeichert für Tisch {tisch_id}.")
    warenkorb.leeren()

    # Bestellungen anzeigen
    bestellungen = lade_bestellungen_fuer_tisch(tisch_id)
    for b in bestellungen:
        print(f"🧾 Bestellung {b['id']} ({b['zeit']}, Status: {b['status']})")
        for name, menge, preis in b['positionen']:
            print(f"  - {menge}× {name} = {menge * preis:.2f} CHF")

# GUI-Funktionen: scrollbare Fläche
def erstelle_scroll_frame(content_frame):
    global canvas, scrollable_frame, window_id
    canvas = tk.Canvas(content_frame, **styles.STYLE_CANVAS)
    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    scrollable_frame = tk.Frame(canvas, bg=styles.FARBE_HINTERGRUND)
    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))

# Kategorieanzeige
def zeige_kategorie(kategorieID, titel_label, sprache):
    global aktuelle_kategorieID
    aktuelle_kategorieID = kategorieID
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    texts = TEXTS.get(sprache, TEXTS["de"])
    titel_label.config(text=texts.get(KATEGORIEN[kategorieID], texts["Produkte"]))
    produkte = Produkt.lade_alle_aus_db(kategorieID, sprache)
    spalten = 3
    for index, produkt in enumerate(produkte):
        row = index // spalten
        col = index % spalten
        frame = tk.Frame(scrollable_frame, **styles.STYLE_FRAME)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        tk.Label(frame, text=produkt.name, **styles.STYLE_PRODUKTNAME).pack(anchor="w")
        tk.Label(frame, text=produkt.beschreibung, **styles.STYLE_BESCHREIBUNG).pack(anchor="w")

        hinweise = []
        if getattr(produkt, "vegetarisch", False): hinweise.append(texts["Vegetarisch"])
        if getattr(produkt, "vegan", False): hinweise.append(texts["Vegan"])
        if getattr(produkt, "herkunft", ""): hinweise.append(f"{texts['Herkunft']}: {produkt.herkunft}")
        if hinweise:
            tk.Label(frame, text=f"{texts['Hinweis']}: " + ", ".join(hinweise), **styles.STYLE_BESCHREIBUNG).pack(anchor="w")

        tk.Label(frame, text=f"{produkt.preis:.2f} CHF", **styles.STYLE_PREIS).pack(anchor="e")
        tk.Button(frame, text=texts["Hinzufügen"], command=lambda p=produkt: warenkorb.hinzufuegen(p, 1),
                  bg=styles.FARBE_PRIMÄR, fg="white").pack(anchor="e", pady=3)

# Warenkorb anzeigen
def zeige_warenkorb(titel_label):
    sprache = sprache_var.get()
    texts = TEXTS.get(sprache, TEXTS["de"])
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    titel_label.config(text=texts["Warenkorb"])
    for i, pos in enumerate(warenkorb.positionen):
        row = i // 3
        col = i % 3
        frame = tk.Frame(scrollable_frame, width=246, height=132, **styles.STYLE_FRAME)
        frame.grid(row=row, column=col, padx=10, pady=10)
        frame.grid_propagate(False)
        header = tk.Frame(frame, bg=styles.FARBE_KARTE)
        header.pack(fill="x")
        tk.Label(header, text=f"{pos.menge}× {pos.produkt.name}", **styles.STYLE_PRODUKTNAME).pack(anchor="w", side="left")
        tk.Label(header, text=f"{pos.teilpreis():.2f} CHF", **styles.STYLE_PREIS).pack(anchor="e", side="right")
        tk.Button(frame, text=texts["Entfernen"], command=lambda p=pos.produkt: (warenkorb.loeschen(p), zeige_warenkorb(titel_label)),
                  bg="red", fg="white", font=("Segoe UI", 9)).pack(anchor="e", pady=2)
    total_row = (len(warenkorb.positionen) - 1) // 3 + 1
    tk.Label(scrollable_frame, text=f"{texts['Gesamt']}: {warenkorb.gesamtpreis():.2f} CHF",
             **styles.STYLE_PREIS).grid(row=total_row, column=0, columnspan=3, sticky="e", padx=10, pady=10)

def zeige_bestellungen():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    sprache = sprache_var.get()
    texts = TEXTS.get(sprache, TEXTS["de"])
    tisch_id = tisch_mapping.get(tisch_var_str.get())

    bestellungen = lade_bestellungen_fuer_tisch(tisch_id)

    row = 0
    for bestellung in bestellungen:
        header = f"Bestellung {bestellung['id']} ({bestellung['zeit']}) - Status: {bestellung['status']}"
        tk.Label(scrollable_frame, text=header, **styles.STYLE_TITEL).grid(row=row, column=0, sticky="w", padx=10, pady=5)
        row += 1

        for name, menge, preis in bestellung['positionen']:
            text = f"{menge}× {name} = {menge * preis:.2f} CHF"
            tk.Label(scrollable_frame, text=text, **styles.STYLE_BESCHREIBUNG).grid(row=row, column=0, sticky="w", padx=20)
            row += 1

        row += 1  # Abstand zur nächsten Bestellung

# App starten
def start_app():
    global sprache_var, tisch_var_str, tisch_mapping, scrollable_frame
    root = tk.Tk()
    root.title("Zum hungrigen Bären")
    root.geometry("1000x700")
    root.configure(bg=styles.FARBE_HINTERGRUND)

    sprache_var = tk.StringVar(value="de")
    anzeigen, tisch_mapping = lade_tisch_anzeigen()
    tisch_var_str = tk.StringVar(value=anzeigen[0] if anzeigen else "")

    nav_frame = tk.Frame(root, width=200, bg=styles.FARBE_KATEGORIE)
    nav_frame.pack(side="left", fill="y")
    content_frame = tk.Frame(root, bg=styles.FARBE_HINTERGRUND)
    content_frame.pack(side="right", expand=True, fill="both")
    top_frame = tk.Frame(content_frame, bg=styles.FARBE_HINTERGRUND)
    top_frame.pack(fill="x", padx=10, pady=10)

    titel_label = tk.Label(top_frame, text="", **styles.STYLE_TITEL)
    titel_label.pack(side="left")

    tk.Button(nav_frame, text="💾 Bestellung speichern", command=bestellung_speichern,
              **styles.STYLE_BUTTON).pack(fill="x", side="bottom")
    tk.Button(nav_frame, text="🛒 Warenkorb",
              command=lambda: zeige_warenkorb(titel_label),
              **styles.STYLE_BUTTON).pack(fill="x", side="bottom")
    tk.Button(nav_frame, text="📋 Bestellungen anzeigen",
              command=zeige_bestellungen,
              **styles.STYLE_BUTTON).pack(fill="x", side="bottom")

    sprache_dropdown = tk.OptionMenu(
        top_frame, sprache_var, "de", "fr", "en",
        command=lambda _: zeige_kategorie(aktuelle_kategorieID, titel_label, sprache_var.get())
    )
    sprache_dropdown.config(bg="white")
    sprache_dropdown.pack(side="right")

    tisch_dropdown = tk.OptionMenu(top_frame, tisch_var_str, *anzeigen)
    tisch_dropdown.config(bg="white")
    tisch_dropdown.pack(side="right", padx=10)

    erstelle_scroll_frame(content_frame)

    def lade_kategorie(kategorieID):
        zeige_kategorie(kategorieID, titel_label, sprache_var.get())

    for label, kat_id in [("Vorspeisen", 4), ("Hauptgerichte", 1), ("Desserts", 3), ("Getränke", 2)]:
        tk.Button(nav_frame, text=label, command=lambda k=kat_id: lade_kategorie(k),
                  **styles.STYLE_BUTTON).pack(fill="x")

    zeige_kategorie(aktuelle_kategorieID, titel_label, sprache_var.get())
    root.mainloop()