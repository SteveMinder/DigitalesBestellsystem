# src/gui/main_window.py
# ------------------------------------------------------------
# GUI mit Grid-Layout für Produktanzeige
# ------------------------------------------------------------
from src.gui import styles
import tkinter as tk
from src.models.restaurant_klassen import Warenkorb, Produkt

warenkorb = Warenkorb()
sprache_var = None
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
        "Gesamt": "Gesamt"
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
        "Gesamt": "Total"
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
        "Gesamt": "Total"
    }
}

KATEGORIEN = {
    1: "Hauptgerichte",
    2: "Getränke",
    3: "Desserts",
    4: "Vorspeisen"
}

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
        if getattr(produkt, "vegetarisch", False):
            hinweise.append(texts["Vegetarisch"])
        if getattr(produkt, "vegan", False):
            hinweise.append(texts["Vegan"])
        if getattr(produkt, "herkunft", ""):
            hinweise.append(f"{texts['Herkunft']}: {produkt.herkunft}")

        if hinweise:
            hinweis_text = f"{texts['Hinweis']}: " + ", ".join(hinweise)
            tk.Label(frame, text=hinweis_text, **styles.STYLE_BESCHREIBUNG).pack(anchor="w")

        tk.Label(frame, text=f"{produkt.preis:.2f} €", **styles.STYLE_PREIS).pack(anchor="e")

        tk.Button(
            frame,
            text=texts["Hinzufügen"],
            command=lambda p=produkt: warenkorb.hinzufuegen(p, 1),
            bg=styles.FARBE_PRIMÄR,
            fg="white"
        ).pack(anchor="e", pady=3)

# (Rest bleibt gleich – z. B. zeige_warenkorb(), start_app() usw.)

def zeige_warenkorb(titel_label):
    sprache = sprache_var.get()
    texts = TEXTS.get(sprache, TEXTS["de"])

    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    titel_label.config(text=texts["Warenkorb"])

    for i, pos in enumerate(warenkorb.positionen):
        frame = tk.Frame(scrollable_frame, **styles.STYLE_FRAME)
        frame.grid(row=i, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        header = tk.Frame(frame, bg=styles.FARBE_KARTE)
        header.pack(fill="x")

        tk.Label(header, text=f"{pos.menge}× {pos.produkt.name}", **styles.STYLE_PRODUKTNAME).pack(anchor="w", side="left")
        tk.Label(header, text=f"{pos.teilpreis():.2f} €", **styles.STYLE_PREIS).pack(anchor="e", side="right")

        tk.Button(frame, text=texts["Entfernen"],
                  command=lambda p=pos.produkt: (warenkorb.loeschen(p), zeige_warenkorb(titel_label)),
                  bg="red", fg="white", font=("Segoe UI", 9)).pack(anchor="e", pady=2)

    gesamt = warenkorb.gesamtpreis()
    tk.Label(scrollable_frame, text=f"{texts['Gesamt']}: {gesamt:.2f} €", **styles.STYLE_PREIS).grid(row=i+1, column=0, columnspan=3, sticky="e", padx=10, pady=10)

def start_app():
    global sprache_var

    root = tk.Tk()
    root.title("Zum hungrigen Bären")
    root.geometry("1000x700")
    root.configure(bg=styles.FARBE_HINTERGRUND)

    sprache_var = tk.StringVar(value="de")

    nav_frame = tk.Frame(root, width=200, bg=styles.FARBE_KATEGORIE)
    nav_frame.pack(side="left", fill="y")

    content_frame = tk.Frame(root, bg=styles.FARBE_HINTERGRUND)
    content_frame.pack(side="right", expand=True, fill="both")

    top_frame = tk.Frame(content_frame, bg=styles.FARBE_HINTERGRUND)
    top_frame.pack(fill="x", padx=10, pady=10)

    titel_label = tk.Label(top_frame, text="", **styles.STYLE_TITEL)
    titel_label.pack(side="left")

    sprache_dropdown = tk.OptionMenu(
        top_frame, sprache_var, "de", "fr", "en",
        command=lambda _: zeige_kategorie(aktuelle_kategorieID, titel_label, sprache_var.get())
    )
    sprache_dropdown.config(bg="white")
    sprache_dropdown.pack(side="right")

    erstelle_scroll_frame(content_frame)

    def lade_kategorie(kategorieID):
        zeige_kategorie(kategorieID, titel_label, sprache_var.get())

    for label, kat_id in [
        ("Vorspeisen", 4),
        ("Hauptgerichte", 1),
        ("Desserts", 3),
        ("Getränke", 2),
    ]:
        tk.Button(nav_frame, text=label, command=lambda k=kat_id: lade_kategorie(k),
                  **styles.STYLE_BUTTON).pack(fill="x")

    tk.Button(nav_frame, text="🛒 Warenkorb",
              command=lambda: zeige_warenkorb(titel_label),
              **styles.STYLE_BUTTON).pack(fill="x", side="bottom")

    zeige_kategorie(aktuelle_kategorieID, titel_label, sprache_var.get())
    root.mainloop()