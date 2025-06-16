# src/gui/main_window.py
# ------------------------------------------------------------
# Überarbeitetes GUI gemäß Mockup: Navigation + Produktanzeige + Warenkorb
# ------------------------------------------------------------
from src.gui import styles
import tkinter as tk
from src.models.restaurant_klassen import Warenkorb, Produkt

# -----------------------------
# Globale Warenkorb-Instanz
# -----------------------------
warenkorb = Warenkorb()


# -----------------------------
# Kategorie-Navigation und Anzeige
# -----------------------------
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

    produkte = Produkt.lade_alle_aus_db(kategorieID)
    for produkt in produkte:
        frame = tk.Frame(inhalt_frame, **styles.STYLE_FRAME)
        frame.pack(fill="x", padx=10, pady=5, expand=True)

        tk.Label(frame, text=produkt.name, **styles.STYLE_PRODUKTNAME).pack(anchor="w")
        tk.Label(frame, text=produkt.beschreibung, **styles.STYLE_BESCHREIBUNG).pack(anchor="w")
        tk.Label(frame, text=f"{produkt.preis:.2f} €", **styles.STYLE_PREIS).pack(anchor="e")

        def hinzufuegen(p=produkt):
            warenkorb.hinzufuegen(p, 1)
            print(f"➕ '{p.name}' zum Warenkorb hinzugefügt.")

        tk.Button(frame, text="+ Hinzufügen", command=hinzufuegen, bg=styles.FARBE_PRIMÄR, fg="white").pack(anchor="e", pady=3)


# -----------------------------
# Warenkorb anzeigen
# -----------------------------
def zeige_warenkorb(inhalt_frame):
    for widget in inhalt_frame.winfo_children():
        widget.destroy()

    tk.Label(inhalt_frame, text="Warenkorb", **styles.STYLE_TITEL).pack(anchor="w", padx=10, pady=10)

    for pos in warenkorb.positionen:
        frame = tk.Frame(inhalt_frame, **styles.STYLE_FRAME)
        frame.pack(fill="x", padx=10, pady=5)

        header = tk.Frame(frame, bg=styles.FARBE_KARTE)
        header.pack(fill="x")

        tk.Label(header, text=f"{pos.menge}× {pos.produkt.name}", **styles.STYLE_PRODUKTNAME).pack(anchor="w", side="left")
        tk.Label(header, text=f"{pos.teilpreis():.2f} €", **styles.STYLE_PREIS).pack(anchor="e", side="right")

        def loesche_pos(p=pos):
            warenkorb.loeschen(p.produkt)
            zeige_warenkorb(inhalt_frame)

        tk.Button(frame, text="Entfernen", command=loesche_pos, bg="red", fg="white", font=("Segoe UI", 9)).pack(anchor="e", pady=2)

    gesamt = warenkorb.gesamtpreis()
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
