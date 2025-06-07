# db/__init__.py
# Gemeinsamer Pfad zur SQLite-Datenbank, für alle DB-Module
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "restaurant.db")