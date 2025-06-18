from abc import ABC, abstractmethod
from datetime import datetime
import sqlite3
from src.db import DB_PATH
from tkinter import messagebox
from tkinter import Frame, Label
from src.lang.translations import TEXTS

# -------------------------
# 1. Abstrakte Klasse Produkt
# -------------------------
class Produkt(ABC):
    def __init__(self, produktID, name, beschreibung, preis, kategorieID, verfuegbar):
        self.produktID = produktID
        self.name = name
        self.beschreibung = beschreibung
        self.preis = preis
        self.kategorieID = kategorieID
        self.verfuegbar = verfuegbar

    @staticmethod
    def lade_alle_aus_db(kategorieID, sprache="de"):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT produktID, name, name_fr, name_en,
                   beschreibung, beschreibung_fr, beschreibung_en,
                   preis, typ, groesse, vegetarisch, vegan, herkunft, verfuegbar, kategorieID
            FROM produkt
            WHERE verfuegbar = 1 AND kategorieID = ?
        """, (kategorieID,))

        daten = cursor.fetchall()
        conn.close()

        produkte = []
        for row in daten:
            produktID, name_de, name_fr, name_en, \
                beschr_de, beschr_fr, beschr_en, preis, typ, groesse, \
                vegetarisch, vegan, herkunft, verfuegbar, kID = row

            if sprache == "fr":
                name = name_fr or name_de
                beschreibung = beschr_fr or beschr_de
            elif sprache == "en":
                name = name_en or name_de
                beschreibung = beschr_en or beschr_de
            else:
                name = name_de
                beschreibung = beschr_de

            if typ == "Getränk":
                produkt = Getraenk(produktID, name, beschreibung, preis, kID, verfuegbar, groesse)
            else:
                produkt = Speise(produktID, name, beschreibung, preis, kID, verfuegbar,
                                 bool(vegetarisch), bool(vegan), False, herkunft)
            produkte.append(produkt)
        return produkte

    def __eq__(self, other):
        result = isinstance(other, Produkt) and self.produktID == other.produktID
        if not result:
            print(f"🔍 Vergleich fehlgeschlagen: {self.produktID} vs {getattr(other, 'produktID', 'N/A')}")
        return result

    def __hash__(self):
        return hash(self.produktID)

    @staticmethod
    def zeige_kategorie(kategorieID, scrollable_frame, titel_label, TEXTS, sprache, warenkorb):
        from tkinter import Frame, Label, Button
        from src.gui import styles
        from src.models.restaurant_klassen import Produkt

        texts = TEXTS.get(sprache, TEXTS["de"])

        scrollable_frame.configure(bg="#f8f8f8")

        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        kategorien = {
            1: "Hauptgerichte",
            2: "Getränke",
            3: "Desserts",
            4: "Vorspeisen",
            5: "Alkoholhaltige Getränke"
        }

        titel_label.config(text=texts.get(kategorien[kategorieID], texts["Produkte"]))

        produkte = Produkt.lade_alle_aus_db(kategorieID, sprache)
        scrollable_frame.update_idletasks()
        scrollable_width = scrollable_frame.winfo_width() or scrollable_frame.winfo_reqwidth()
        kachel_breite = 300
        spalten = max(2, scrollable_width // kachel_breite)

        for index, produkt in enumerate(produkte):
            row = index // spalten
            col = index % spalten

            frame = Frame(
                scrollable_frame,
                width=280,
                height=150,
                bg="#ffffff",
                bd=0,
                relief="flat",
                highlightbackground="#cccccc",
                highlightthickness=1
            )
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            frame.grid_propagate(False)

            scrollable_frame.grid_columnconfigure(col, weight=1)

            # Innerer Container für Inhalte
            inner = Frame(frame, bg="#ffffff")
            inner.pack(fill="both", expand=True)

            Label(inner, text=produkt.name, wraplength=260, justify="left", **styles.STYLE_PRODUKTNAME).pack(anchor="w",
                                                                                                             pady=(
                                                                                                             0, 2))
            Label(inner, text=produkt.beschreibung, wraplength=260, justify="left", **styles.STYLE_BESCHREIBUNG).pack(
                anchor="w")
            Label(inner, text=f"{produkt.preis:.2f} CHF", **styles.STYLE_PREIS).pack(anchor="se", padx=12)

            Button(
                inner,
                text=texts["Hinzufügen"],
                command=lambda p=produkt: warenkorb.hinzufuegen(p, 1),
                bg=styles.FARBE_PRIMÄR,
                fg="white"
            ).pack(anchor="se", side="bottom", pady=6, padx=12)

# -------------------------
# 2. Subklasse Speise
# -------------------------
class Speise(Produkt):
    def __init__(self, produktID, name, beschreibung, preis, kategorieID, verfuegbar,
                 vegetarisch, vegan, glutenfrei, herkunft):
        super().__init__(produktID, name, beschreibung, preis, kategorieID, verfuegbar)
        self.vegetarisch = vegetarisch
        self.vegan = vegan
        self.glutenfrei = glutenfrei
        self.herkunft = herkunft

    def anzeigen(self):
        return f"{self.name} ({self.preis:.2f} CHF) - {self.beschreibung}"

# -------------------------
# 3. Subklasse Getränk
# -------------------------
class Getraenk(Produkt):
    def __init__(self, produktID, name, beschreibung, preis, kategorieID, verfuegbar, groesse):
        super().__init__(produktID, name, beschreibung, preis, kategorieID, verfuegbar)
        self.groesse = groesse

    def anzeigen(self):
        return f"{self.name} ({self.groesse}) - {self.preis:.2f} CHF"

# -------------------------
# 4. Klasse Kategorie
# -------------------------
class Kategorie:
    def __init__(self, kategorieID, bezeichnung):
        self.kategorieID = kategorieID
        self.bezeichnung = bezeichnung

    def alleProdukte(self, datenquelle):
        return [p for p in datenquelle if p.kategorieID == self.kategorieID]

# -------------------------
# 5. Klasse Tisch
# -------------------------
class Tisch:
    def __init__(self, tischID, sitzplaetze, clusterID=None):
        self.tischID = tischID
        self.sitzplaetze = sitzplaetze
        self.clusterID = clusterID
        self.status_wert = "offen"

    def status(self):
        return self.status_wert

    def clusterZuweisen(self, clusterID):
        self.clusterID = clusterID

    @staticmethod
    def lade_anzeigen(sprache="de"):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT tischID, sitzplaetze FROM tisch ORDER BY tischID")
        daten = cursor.fetchall()
        conn.close()
        texts = TEXTS.get(sprache, TEXTS["de"])
        anzeigen = [f"{texts['Tisch']} {tid} ({plaetze} {texts['Plätze']})" for tid, plaetze in daten]
        id_map = {f"{texts['Tisch']} {tid} ({plaetze} {texts['Plätze']})": tid for tid, plaetze in daten}

        return anzeigen, id_map

# -------------------------
# 6. Klasse Bestellung
# -------------------------
class Bestellung:
    def __init__(self, bestellungID, tischID, zeitstempel=None, status="offen"):
        self.bestellungID = bestellungID
        self.tischID = tischID
        self.zeitstempel = zeitstempel or datetime.now()
        self.status = status
        self.positionen = []

    def gesamtpreis(self):
        return sum(p.teilpreis() for p in self.positionen)

    def hinzufuegen(self, produkt, menge):
        self.positionen.append(Bestellposition(None, self.bestellungID, produkt, menge))

    def anzeigen(self):
        for pos in self.positionen:
            print(pos.beschreibung())

    def loeschen(self, produkt):
        self.positionen = [p for p in self.positionen if p.produkt != produkt]

    def speichern(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bestellung (tischID, zeitstempel, status) VALUES (?, ?, ?)",
            (self.tischID, self.zeitstempel.isoformat(), self.status)
        )
        self.bestellungID = cursor.lastrowid
        for pos in self.positionen:
            cursor.execute(
                "INSERT INTO bestellposition (bestellungID, produktID, menge) VALUES (?, ?, ?)",
                (self.bestellungID, pos.produkt.produktID, pos.menge)
            )
        conn.commit()
        conn.close()
        return self.bestellungID

    @staticmethod
    def loesche_alle_bestellungen():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bestellposition")
        cursor.execute("DELETE FROM bestellung")
        # Setzt Autoincrement-Zähler für 'bestellung' zurück
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='bestellung'")
        conn.commit()
        conn.close()
        print("🗑️ Alle Bestellungen, Positionen und Zähler wurden gelöscht.")

    @staticmethod
    def alle_bestellungen_loeschen():
        antwort = messagebox.askyesno("Alle Bestellungen löschen",
                                      "Möchten Sie wirklich alle Bestellungen dauerhaft löschen?")
        if antwort:
            Bestellung.loesche_alle_bestellungen()
            messagebox.showinfo("Erledigt", "Alle Bestellungen und der Zähler wurden gelöscht.")

    @staticmethod
    def zeige_bestellungen(scrollable_frame, titel_label, TEXTS, tisch_id, sprache):
        if not tisch_id:
            print("❗ Kein Tisch ausgewählt für Bestellungsanzeige.")
            return

        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        texts = TEXTS.get(sprache, TEXTS["de"])
        bestellungen = Bestellung.lade_bestellungen_fuer_tisch(tisch_id)

        titel_label.config(text=f"{texts['Bestellungen']} Tisch {tisch_id}")

        for i, b in enumerate(bestellungen):
            frame = Frame(scrollable_frame, bg="#f0f0f0", bd=1, relief="solid")
            frame.grid(row=i, column=0, padx=10, pady=5, sticky="w")

            header = f"🧾 Bestellung {b['id']} ({b['zeit']}, Status: {b['status']})"
            Label(frame, text=header, font=("Segoe UI", 10, "bold"), anchor="w").pack(anchor="w")

            bestellwert = 0.0
            for name, menge, preis in b['positionen']:
                teilpreis = menge * preis
                bestellwert += teilpreis
                text = f"  - {menge}× {name} = {teilpreis:.2f} CHF"
                Label(frame, text=text, anchor="w").pack(anchor="w")

            # Einzelne Summe pro Bestellung anzeigen
            Label(frame, text=f"💵 Summe: {bestellwert:.2f} CHF",
                  font=("Segoe UI", 10, "italic"), anchor="e").pack(anchor="e", pady=(0, 5))

    @staticmethod
    def bestellung_speichern(warenkorb, tisch_id):
        if not tisch_id:
            print("❗ Kein Tisch ausgewählt.")
            return

        bestellung = warenkorb.als_bestellung(None, tisch_id)
        bestellung_id = bestellung.speichern()
        print(f"✅ Bestellung {bestellung_id} gespeichert für Tisch {tisch_id}.")
        warenkorb.leeren()

    @staticmethod
    def lade_bestellungen_fuer_tisch(tisch_id, sprache="de"):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT bestellungID, zeitstempel, status
            FROM bestellung
            WHERE tischID = ?
            ORDER BY zeitstempel DESC
        """, (tisch_id,))
        bestellungen = cursor.fetchall()
        result = []
        for bestellung_id, zeit, status in bestellungen:
            # Sprachabhängige Spaltennamen
            name_spalte = {
                "de": "name",
                "fr": "name_fr",
                "en": "name_en"
            }.get(sprache, "name")

            cursor.execute(f"""
                SELECT p.{name_spalte}, bp.menge, p.preis
                FROM bestellposition bp
                JOIN produkt p ON bp.produktID = p.produktID
                WHERE bp.bestellungID = ?
            """, (bestellung_id,))
            positionen = cursor.fetchall()
            result.append({
                "id": bestellung_id,
                "zeit": zeit,
                "status": status,
                "positionen": positionen
            })
        conn.close()
        return result

    @staticmethod
    def wechsle_status(bestellung_id):
        """Wechselt den Status einer Bestellung in der Reihenfolge: offen → in Bearbeitung → serviert → bezahlt."""
        status_folge = ["offen", "in Bearbeitung", "serviert", "bezahlt"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT status FROM bestellung WHERE bestellungID = ?", (bestellung_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return

        aktueller_status = row[0]
        try:
            neuer_status = status_folge[status_folge.index(aktueller_status) + 1]
        except IndexError:
            neuer_status = aktueller_status  # bleibt bei "bezahlt"

        cursor.execute("UPDATE bestellung SET status = ? WHERE bestellungID = ?", (neuer_status, bestellung_id))
        conn.commit()
        conn.close()
# -------------------------
# 7. Klasse Bestellposition
# -------------------------
class Bestellposition:
    def __init__(self, positionID, bestellungID, produkt, menge):
        self.positionID = positionID
        self.bestellungID = bestellungID
        self.produkt = produkt
        self.menge = menge

    def teilpreis(self):
        return self.produkt.preis * self.menge

    def beschreibung(self):
        return f"{self.menge}× {self.produkt.name} = {self.teilpreis():.2f} CHF"

# -------------------------
# 8. Klasse Sprache
# -------------------------
class Sprache:
    def __init__(self, sprachID, bezeichnung):
        self.sprachID = sprachID
        self.bezeichnung = bezeichnung

    def alsCode(self):
        return self.bezeichnung[:2].upper()

# -------------------------
# 9. Klasse ProduktText
# -------------------------
class ProduktText:
    def __init__(self, produktID, sprachID, name, beschreibung):
        self.produktID = produktID
        self.sprachID = sprachID
        self.name = name
        self.beschreibung = beschreibung

    def textInSprache(self, sprachID):
        return (self.name, self.beschreibung) if self.sprachID == sprachID else None

# -------------------------
# X. Klasse Warenkorb
# -------------------------
class Warenkorb:
    def __init__(self):
        self.positionen = []

    def hinzufuegen(self, produkt, menge=1):
        for pos in self.positionen:
            if pos.produkt.produktID == produkt.produktID:
                pos.menge += menge
                return
        self.positionen.append(Bestellposition(None, None, produkt, menge))

    def loeschen(self, produkt):
        self.positionen = [p for p in self.positionen if p.produkt.produktID != produkt.produktID]

    def gesamtpreis(self):
        return sum(p.teilpreis() for p in self.positionen)

    def leeren(self):
        self.positionen.clear()

    def als_bestellung(self, bestellungID, tischID):
        bestellung = Bestellung(bestellungID, tischID)
        for pos in self.positionen:
            bestellung.hinzufuegen(pos.produkt, pos.menge)
        return bestellung

    def zeige_warenkorb(self, scrollable_frame, titel_label, TEXTS, sprache, tisch_id):
        from tkinter import Frame, Label, Button

        texts = TEXTS.get(sprache, TEXTS["de"])

        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        titel_label.config(text=texts["Warenkorb"])

        spalten = 2
        for s in range(spalten):
            scrollable_frame.grid_columnconfigure(s, weight=1)

        for i, pos in enumerate(self.positionen):
            row = i // spalten
            col = i % spalten

            frame = Frame(scrollable_frame, width=260, height=110, bg="#ffffff", bd=1, relief="solid",
                          highlightbackground="#dddddd", highlightthickness=1)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            frame.grid_propagate(False)

            Label(frame, text=f"{pos.menge}× {pos.produkt.name}", font=("Segoe UI", 10, "bold"), anchor="w").pack(
                anchor="w", pady=(0, 2), padx=6)
            Label(frame, text=f"{pos.teilpreis():.2f} CHF", font=("Segoe UI", 10, "italic"), anchor="w").pack(
                anchor="w", pady=(0, 4), padx=6)

            Button(
                frame,
                text="🗑️ Entfernen",
                command=lambda p=pos.produkt: (self.loeschen(p), self.zeige_warenkorb_mit_speichern(scrollable_frame, titel_label, TEXTS,sprache, tisch_id)),
                bg="#d62828",
                fg="white",
                font=("Segoe UI", 9),
                padx=6,
                pady=2
            ).pack(anchor="se", pady=6, padx=12)

        total_row = (len(self.positionen) - 1) // spalten + 1
        Label(scrollable_frame, text=f"{texts['Gesamt']}: {self.gesamtpreis():.2f} CHF",
              font=("Segoe UI", 10, "bold")).grid(
            row=total_row, column=0, columnspan=spalten, sticky="e", padx=10, pady=10
        )

    def zeige_warenkorb_mit_speichern(self, scrollable_frame, titel_label, TEXTS, sprache, tisch_id):
        from tkinter import Button, messagebox, Label

        self.zeige_warenkorb(scrollable_frame, titel_label, TEXTS, sprache, tisch_id)

        if self.positionen:
            def bestaetige_speichern():
                antwort = messagebox.askyesno(
                    TEXTS[sprache]["Bestellung speichern"],
                    TEXTS[sprache]["Bestellung bestätigen"]
                )
                if antwort:
                    from .restaurant_klassen import Bestellung
                    Bestellung.bestellung_speichern(self, tisch_id)
                    self.leeren()
                    self.zeige_warenkorb(scrollable_frame, titel_label, TEXTS, sprache, tisch_id)

            speichern_button = Button(
                scrollable_frame,
                text="💾 " + TEXTS[sprache]["Bestellung speichern"],
                command=bestaetige_speichern,
                bg="#4CAF50",
                fg="white",
                font=("Segoe UI", 10),
                padx=10,
                pady=5
            )
            speichern_button.grid(row=999, column=0, columnspan=3, sticky="e", padx=10, pady=10)

