#!/usr/bin/env python3
"""
Haupt-Eintrittspunkt für die Dynamische Stromtarif-Analyse
Reine Streamlit-Lösung - keine CLI mehr
"""

import sys
import os

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("❌ FEHLER: Diese Datei kann nicht direkt ausgeführt werden!")
print()
print("🚀 Bitte starten Sie die Weboberfläche mit:")
print("   streamlit run web_app.py")
print()
print("💡 Warum? Streamlit kann nicht als Modul importiert werden")
print("   und muss immer als Hauptskript gestartet werden.")

sys.exit(1)