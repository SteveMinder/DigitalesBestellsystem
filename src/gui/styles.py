# src/gui/styles.py
# --------------------------------------------------
# Zentrales Stylesheet für das GUI der Restaurant-App
# Definiert Farben, Fonts und Standard-Widget-Styles
# --------------------------------------------------

# Farben
FARBE_HINTERGRUND = "#fdfdfd"
FARBE_TEXT = "#222831"
FARBE_KATEGORIE = "#eeeeee"
FARBE_KARTE = "#ffffff"
FARBE_HIGHLIGHT = "#dceefb"
FARBE_PRIMÄR = "#3a86ff"
FARBE_RAND = "#dddddd"

# Bestellstatusfarben
FARBE_STATUS = {
    "offen": "#FFB347",
    "in Bearbeitung": "#FFD700",
    "serviert": "#90EE90",
    "bezahlt": "#87CEFA"
}

# Schriftarten
FONT_TITEL = ("Segoe UI", 18, "bold")
FONT_KATEGORIE = ("Segoe UI", 14, "bold")
FONT_PRODUKTNAME = ("Segoe UI", 12, "bold")
FONT_TEXT = ("Segoe UI", 11)
FONT_PREIS = ("Segoe UI", 10, "italic")
FONT_KLEIN = ("Segoe UI", 9)
FONT_KLEIN_BOLD = ("Segoe UI", 10, "bold")
FONT_KLEIN_ITALIC = ("Segoe UI", 10, "italic")

# Stil: Buttons
STYLE_BUTTON = {
    "bg": FARBE_PRIMÄR,
    "fg": "white",
    "activebackground": "#005fcb",
    "activeforeground": "white",
    "font": FONT_TEXT,
    "relief": "flat",
    "bd": 0,
    "padx": 12,
    "pady": 8
}

STYLE_BUTTON_STATUS = {
    "bg": "#FFA500",
    "fg": "white",
    "font": FONT_KLEIN,
    "padx": 8,
    "pady": 3
}

STYLE_BUTTON_RECHNUNG = {
    "bg": FARBE_PRIMÄR,
    "fg": "white",
    "font": FONT_KLEIN,
    "padx": 8,
    "pady": 3
}

# Stil: Label
STYLE_LABEL = {
    "bg": FARBE_HINTERGRUND,
    "fg": FARBE_TEXT,
    "font": FONT_TEXT,
}

STYLE_TITEL = {
    "bg": FARBE_HINTERGRUND,
    "fg": FARBE_PRIMÄR,
    "font": FONT_TITEL,
    "pady": 20
}

STYLE_KATEGORIE = {
    "bg": FARBE_HINTERGRUND,
    "fg": FARBE_TEXT,
    "font": FONT_KATEGORIE,
    "pady": 10
}

STYLE_PRODUKTNAME = {
    "bg": FARBE_KARTE,
    "fg": FARBE_TEXT,
    "font": FONT_PRODUKTNAME
}

STYLE_BESCHREIBUNG = {
    "bg": FARBE_KARTE,
    "fg": "#666666",
    "font": FONT_TEXT
}

STYLE_PREIS = {
    "bg": FARBE_KARTE,
    "fg": "#555555",
    "font": FONT_PREIS
}

STYLE_BESTELLUNG_HEADER = {
    "font": FONT_KLEIN_BOLD,
    "anchor": "w"
}

STYLE_BESTELLUNG_SUMME = {
    "font": FONT_KLEIN_ITALIC,
    "anchor": "e"
}

STYLE_CANVAS = {
    "bg": FARBE_HINTERGRUND
}

STYLE_FRAME = {
    "bg": FARBE_KARTE,
    "bd": 1,
    "relief": "solid",
    "padx": 10,
    "pady": 6
}

STYLE_WARENKORB_POSITION = {
    "bg": FARBE_KARTE,
    "fg": FARBE_TEXT,
    "font": FONT_TEXT,
    "anchor": "w",
    "padx": 10,
    "pady": 4
}