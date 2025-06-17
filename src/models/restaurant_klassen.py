from abc import ABC, abstractmethod
from datetime import datetime
import sqlite3
from src.db import DB_PATH
from tkinter import Frame, Label

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

        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        kategorien = {
            1: "Hauptgerichte",
            2: "Getränke",
            3: "Desserts",
            4: "Vorspeisen"
        }

        titel_label.config(text=texts.get(kategorien[kategorieID], texts["Produkte"]))

        produkte = Produkt.lade_alle_aus_db(kategorieID, sprache)
        spalten = 3

        for index, produkt in enumerate(produkte):
            row = index // spalten
            col = index % spalten

            frame = Frame(scrollable_frame, **styles.STYLE_FRAME)
            frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            Label(frame, text=produkt.name, **styles.STYLE_PRODUKTNAME).pack(anchor="w")
            Label(frame, text=produkt.beschreibung, **styles.STYLE_BESCHREIBUNG).pack(anchor="w")
            Label(frame, text=f"{produkt.preis:.2f} CHF", **styles.STYLE_PREIS).pack(anchor="e")
            Button(
                frame,
                text=texts["Hinzufügen"],
                command=lambda p=produkt: warenkorb.hinzufuegen(p, 1),
                bg=styles.FARBE_PRIMÄR,
                fg="white"
            ).pack(anchor="e", pady=3)

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
    def lade_anzeigen():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT tischID, sitzplaetze FROM tisch ORDER BY tischID")
        daten = cursor.fetchall()
        conn.close()
        anzeigen = [f"Tisch {tid} ({plaetze} Plätze)" for tid, plaetze in daten]
        id_map = {f"Tisch {tid} ({plaetze} Plätze)": tid for tid, plaetze in daten}
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
        result = []
        for bestellung_id, zeit, status in bestellungen:
            cursor.execute("""
                SELECT p.name, bp.menge, p.preis
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

    def zeige_warenkorb(self, scrollable_frame, titel_label, TEXTS, sprache):
        from tkinter import Frame, Label, Button

        texts = TEXTS.get(sprache, TEXTS["de"])

        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        titel_label.config(text=texts["Warenkorb"])

        for i, pos in enumerate(self.positionen):
            row = i // 3
            col = i % 3

            frame = Frame(scrollable_frame, width=246, height=132, bg="#f0f0f0", bd=1, relief="solid")
            frame.grid(row=row, column=col, padx=10, pady=10)
            frame.grid_propagate(False)

            header = Frame(frame, bg="#e0e0e0")
            header.pack(fill="x")

            Label(header, text=f"{pos.menge}× {pos.produkt.name}", font=("Segoe UI", 10, "bold"), anchor="w").pack(anchor="w", side="left")
            Label(header, text=f"{pos.teilpreis():.2f} CHF", font=("Segoe UI", 10), anchor="e").pack(anchor="e", side="right")

            Button(frame, text=texts["Entfernen"],
                   command=lambda p=pos.produkt: (self.loeschen(p), self.zeige_warenkorb(scrollable_frame, titel_label, TEXTS, sprache)),
                   bg="red", fg="white", font=("Segoe UI", 9)).pack(anchor="e", pady=2)

        total_row = (len(self.positionen) - 1) // 3 + 1
        Label(scrollable_frame, text=f"{texts['Gesamt']}: {self.gesamtpreis():.2f} CHF", font=("Segoe UI", 10)).grid(
            row=total_row, column=0, columnspan=3, sticky="e", padx=10, pady=10
        )

    def zeige_warenkorb_mit_speichern(self, scrollable_frame, titel_label, TEXTS, sprache, tisch_id):
        from tkinter import Button, messagebox, Label

        self.zeige_warenkorb(scrollable_frame, titel_label, TEXTS, sprache)

        if self.positionen:
            def bestaetige_speichern():
                antwort = messagebox.askyesno(
                    "Bestellung bestätigen",
                    "Möchten Sie die Bestellung wirklich abschicken? Eine nachträgliche Änderung ist nicht möglich."
                )
                if antwort:
                    from .restaurant_klassen import Bestellung
                    Bestellung.bestellung_speichern(self, tisch_id)
                    self.leeren()
                    self.zeige_warenkorb(scrollable_frame, titel_label, TEXTS, sprache)

            speichern_button = Button(
                scrollable_frame,
                text="💾 Bestellung speichern",
                command=bestaetige_speichern,
                bg="#4CAF50",
                fg="white",
                font=("Segoe UI", 10),
                padx=10,
                pady=5
            )
            speichern_button.grid(row=999, column=0, columnspan=3, sticky="e", padx=10, pady=10)

