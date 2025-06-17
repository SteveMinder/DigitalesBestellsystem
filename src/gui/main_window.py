""
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

def start_app():
    global sprache_var, tisch_var_str, tisch_mapping, aktuelle_kategorieID

    root = tk.Tk()
    root.title("Zum hungrigen Bären")
    root.geometry("1000x700")
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

    for label, kat_id in [
        ("Vorspeisen", 4),
        ("Hauptgerichte", 1),
        ("Desserts", 3),
        ("Getränke", 2),
    ]:
        tk.Button(nav_frame, text=label, command=lambda k=kat_id: lade_kategorie(k),
                  **styles.STYLE_BUTTON).pack(fill="x")

    def zeige_warenkorb_mit_speichern():
        warenkorb.zeige_warenkorb(scrollable_frame, titel_label, TEXTS, sprache_var.get())
        if warenkorb.positionen:
            def bestaetige_speichern():
                antwort = messagebox.askyesno("Bestellung bestätigen", "Möchten Sie die Bestellung wirklich abschicken? Eine nachträgliche Änderung ist nicht möglich.")
                if antwort:
                    Bestellung.bestellung_speichern(warenkorb, tisch_mapping.get(tisch_var_str.get()))

            speichern_button = tk.Button(scrollable_frame, text="💾 Bestellung speichern",
                      command=bestaetige_speichern,
                      **styles.STYLE_BUTTON)
            speichern_button.grid(row=999, column=0, columnspan=3, sticky="e", padx=10, pady=10)

    def alle_bestellungen_loeschen():
        antwort = messagebox.askyesno("Alle Bestellungen löschen", "Möchten Sie wirklich alle Bestellungen dauerhaft löschen?")
        if antwort:
            Bestellung.loesche_alle_bestellungen()
            messagebox.showinfo("Erledigt", "Alle Bestellungen wurden gelöscht.")

    tk.Button(nav_frame, text="🗑️ Alle Bestellungen löschen",
              command=alle_bestellungen_loeschen,
              **styles.STYLE_BUTTON).pack(fill="x", side="bottom")

    tk.Button(nav_frame, text="🛒 Warenkorb",
              command=zeige_warenkorb_mit_speichern,
              **styles.STYLE_BUTTON).pack(fill="x", side="bottom")

    tk.Button(nav_frame, text="📋 Bestellungen anzeigen",
              command=lambda: Bestellung.zeige_bestellungen(scrollable_frame, titel_label, TEXTS, tisch_mapping.get(tisch_var_str.get()), sprache_var.get()),
              **styles.STYLE_BUTTON).pack(fill="x", side="bottom")

    Produkt.zeige_kategorie(aktuelle_kategorieID, scrollable_frame, titel_label, TEXTS, sprache_var.get(), warenkorb)
    root.mainloop()
