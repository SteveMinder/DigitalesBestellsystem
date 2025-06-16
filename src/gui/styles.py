# src/gui/styles.py
# --------------------------------------------------
# Zentrales Stylesheet für das GUI der Restaurant-App
# Definiert Farben, Fonts und Standard-Widget-Styles
# --------------------------------------------------

# Farbpalette (modern & kontrastreich)
FARBE_HINTERGRUND = "#fdfdfd"
FARBE_TEXT = "#222831"
FARBE_KATEGORIE = "#eeeeee"
FARBE_KARTE = "#ffffff"
FARBE_HIGHLIGHT = "#dceefb"
FARBE_PRIMÄR = "#3a86ff"
FARBE_RAND = "#dddddd"

# Schriftarten
FONT_TITEL = ("Segoe UI", 18, "bold")
FONT_KATEGORIE = ("Segoe UI", 14, "bold")
FONT_PRODUKTNAME = ("Segoe UI", 12, "bold")
FONT_TEXT = ("Segoe UI", 11)
FONT_PREIS = ("Segoe UI", 10, "italic")

# Button-Stil (Navigation)
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

# Label-Stil (z. B. Kategorienamen)
STYLE_LABEL = {
    "bg": FARBE_HINTERGRUND,
    "fg": FARBE_TEXT,
    "font": FONT_TEXT,
}

# Frame-Stil (Produktkarte)
STYLE_FRAME = {
    "bg": FARBE_KARTE,
    "bd": 1,
    "relief": "solid",
    "padx": 10,
    "pady": 6
}

# Canvas-Farbe
STYLE_CANVAS = {
    "bg": FARBE_HINTERGRUND
}

# Kategorie-Label
STYLE_KATEGORIE = {
    "bg": FARBE_HINTERGRUND,
    "fg": FARBE_TEXT,
    "font": FONT_KATEGORIE,
    "pady": 10
}

# Titelkopf
STYLE_TITEL = {
    "bg": FARBE_HINTERGRUND,
    "fg": FARBE_PRIMÄR,
    "font": FONT_TITEL,
    "pady": 20
}

# Preis-Label
STYLE_PREIS = {
    "bg": FARBE_KARTE,
    "fg": "#555555",
    "font": FONT_PREIS
}

# Produktname
STYLE_PRODUKTNAME = {
    "bg": FARBE_KARTE,
    "fg": FARBE_TEXT,
    "font": FONT_PRODUKTNAME
}

# Beschreibung
STYLE_BESCHREIBUNG = {
    "bg": FARBE_KARTE,
    "fg": "#666666",
    "font": FONT_TEXT
}

# Warenkorbzeile (für Bestellpositionen)
STYLE_WARENKORB_POSITION = {
    "bg": FARBE_KARTE,
    "fg": FARBE_TEXT,
    "font": FONT_TEXT,
    "anchor": "w",
    "padx": 10,
    "pady": 4
}

