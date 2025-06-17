from src.gui import styles
import tkinter as tk
from tkinter import messagebox
from src.models.restaurant_klassen import Warenkorb, Produkt, Tisch, Bestellung

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
        "Tisch": "Tisch",
        "Bestellungen": "Bestellungen"
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
        "Tisch": "Table",
        "Bestellungen": "Commandes"
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
        "Tisch": "Table",
        "Bestellungen": "Orders"
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

def zeige_bestellungen_mit_status():
    tisch_id = tisch_mapping.get(tisch_var_str.get())
    titel_label.config(text=tisch_var_str.get())  # Zeigt den aktuellen Tischnamen als Überschrift
    if not tisch_id:
        return
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    texts = TEXTS.get(sprache_var.get(), TEXTS["de"])
    bestellungen = Bestellung.lade_bestellungen_fuer_tisch(tisch_id)

    farben = {
        "offen": "#FFB347",
        "in Bearbeitung": "#FFD700",
        "serviert": "#90EE90",
        "bezahlt": "#87CEFA"
    }

    for i, b in enumerate(bestellungen):
        frame = tk.Frame(scrollable_frame, bg=farben.get(b['status'], "#f0f0f0"), bd=1, relief="solid")
        frame.grid_propagate(True)
        frame.pack_propagate(True)
        frame.grid(row=i, column=0, padx=10, pady=5, sticky="w")

        inner = tk.Frame(frame, bg=farben.get(b['status'], "#f0f0f0"))
        inner.pack(fill="both", expand=True)

        header = f"📋 Bestellung {b['id']} ({b['zeit']}, Status: {b['status']})"
        tk.Label(inner, text=header, font=("Segoe UI", 10, "bold"), anchor="w", bg=farben.get(b['status'], "#f0f0f0")).pack(anchor="w")

        bestellwert = 0.0
        for name, menge, preis in b['positionen']:
            teilpreis = menge * preis
            bestellwert += teilpreis
            text = f"  - {menge}× {name} = {teilpreis:.2f} CHF"
            tk.Label(inner, text=text, anchor="w", bg=farben.get(b['status'], "#f0f0f0")).pack(anchor="w")

        summe_label = f"💵 {texts['Gesamt']}: {bestellwert:.2f} CHF"
        tk.Label(inner, text=summe_label, font=("Segoe UI", 10, "italic"), anchor="e", bg=farben.get(b['status'], "#f0f0f0")).pack(anchor="e", pady=(0, 5))

        def status_wechsel(b_id=b['id']):
            Bestellung.wechsle_status(b_id)
            zeige_bestellungen_mit_status()

        tk.Button(
            inner, text="🔁 Status ändern", command=status_wechsel,
            bg="#FFA500", fg="white", font=("Segoe UI", 9)
        ).pack(anchor="e", padx=5, pady=(0, 5))


def start_app():
    global sprache_var, tisch_var_str, tisch_mapping, aktuelle_kategorieID
    root = tk.Tk()
    root.title("Zum hungrigen Bären")
    root.geometry("1024x768")
    root.configure(bg=styles.FARBE_HINTERGRUND)

    sprache_var = tk.StringVar(value="de")
    anzeigen, tisch_mapping = Tisch.lade_anzeigen()
    tisch_var_str = tk.StringVar(value=anzeigen[0] if anzeigen else "")

    nav_frame = tk.Frame(root, width=200, bg=styles.FARBE_KATEGORIE)
    nav_frame.pack(side="left", fill="y")

    content_frame = tk.Frame(root, bg=styles.FARBE_HINTERGRUND)
    content_frame.pack(side="right", expand=True, fill="both")

    top_frame = tk.Frame(content_frame, bg=styles.FARBE_HINTERGRUND)
    top_frame.pack(fill="x", padx=10, pady=10)

    global titel_label
    titel_label = tk.Label(top_frame, text="", **styles.STYLE_TITEL)
    titel_label.pack(side="left")

    sprache_dropdown = tk.OptionMenu(
        top_frame, sprache_var, "de", "fr", "en",
        command=lambda _: Produkt.zeige_kategorie(aktuelle_kategorieID, scrollable_frame, titel_label, TEXTS, sprache_var.get(), warenkorb)
    )
    sprache_dropdown.config(bg="white")
    sprache_dropdown.pack(side="right")

    tisch_dropdown = tk.OptionMenu(top_frame, tisch_var_str, *anzeigen)
    tisch_dropdown.config(bg="white")
    tisch_dropdown.pack(side="right", padx=10)

    erstelle_scroll_frame(content_frame)

    def lade_kategorie(kategorieID):
        global aktuelle_kategorieID
        aktuelle_kategorieID = kategorieID
        Produkt.zeige_kategorie(kategorieID, scrollable_frame, titel_label, TEXTS, sprache_var.get(), warenkorb)

    for label, kat_id in [("Vorspeisen", 4), ("Hauptgerichte", 1), ("Desserts", 3), ("Getränke", 2)]:
        tk.Button(nav_frame, text=label, command=lambda k=kat_id: lade_kategorie(k), **styles.STYLE_BUTTON).pack(fill="x")


    tk.Button(nav_frame, text="🗑️ Alle Bestellungen löschen", command=Bestellung.alle_bestellungen_loeschen, **styles.STYLE_BUTTON).pack(fill="x", side="bottom")


    tk.Button(nav_frame, text="🛒 Warenkorb", command=lambda: warenkorb.zeige_warenkorb_mit_speichern(
        scrollable_frame, titel_label, TEXTS, sprache_var.get(), tisch_mapping.get(tisch_var_str.get())
    ), **styles.STYLE_BUTTON).pack(fill="x", side="bottom")

    tk.Button(nav_frame, text="📋 Bestellungen anzeigen", command=zeige_bestellungen_mit_status, **styles.STYLE_BUTTON).pack(fill="x", side="bottom")

    Produkt.zeige_kategorie(aktuelle_kategorieID, scrollable_frame, titel_label, TEXTS, sprache_var.get(), warenkorb)
    root.mainloop()