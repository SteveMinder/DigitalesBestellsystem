from abc import ABC, abstractmethod
from datetime import datetime
import sqlite3
from src.db import DB_PATH

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

    def istVerfuegbar(self):
        return self.verfuegbar

    @abstractmethod
    def anzeigen(self):
        pass

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
