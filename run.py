#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - Hauptprogramm

Startet die PDF Tool Anwendung. Dieses Skript ist der Einstiegspunkt für das Programm
und initialisiert die grafische Benutzeroberfläche.

Funktionsweise:
- Erstellt die Qt-Anwendung
- Initialisiert das Hauptfenster
- Startet die Ereignisschleife

Autor: Team A2-2
"""

# System-Imports
import sys

# Qt-Anwendungsklasse für die GUI
from PyQt5.QtWidgets import QApplication

# Import des Hauptfensters aus unserem PDF Tool
from pdf_tool.gui import MainWindow

# Nur ausführen, wenn direkt gestartet (nicht bei Import)
if __name__ == '__main__':
    # Erstelle die Qt-Anwendung
    app = QApplication(sys.argv)
    
    # Erstelle und zeige das Hauptfenster
    window = MainWindow()
    window.show()
    
    # Starte die Ereignisschleife und beende das Programm nach dem Schließen
    sys.exit(app.exec_())

