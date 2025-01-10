#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - Hauptprogramm

Haupteinstiegspunkt für die PDF Tool Anwendung. Diese Datei initialisiert die
Anwendung und startet die grafische Benutzeroberfläche.

Funktionsweise:
1. Erstellt die Qt-Anwendungsinstanz
2. Initialisiert das Hauptfenster
3. Startet die Ereignisschleife
4. Beendet die Anwendung sauber

Verwendung:
    python -m pdf_tool.main
    
    # Oder über die Funktion
    from pdf_tool.main import main
    main()

Technische Details:
- Verwendet PyQt5 für die GUI
- Einheitliche Fehlerbehandlung
- Sauberes Aufräumen beim Beenden

Autor: Team A2-2
"""

import sys
from PyQt5.QtWidgets import QApplication
from .gui import MainWindow

def main():
    """
    Hauptfunktion zum Starten der Anwendung.
    
    Erstellt die Qt-Anwendung, initialisiert das Hauptfenster
    und startet die Ereignisschleife.
    
    Returns:
        int: Exit-Code der Anwendung (0 bei normalem Beenden)
    """
    # Erstelle die Qt-Anwendung
    app = QApplication(sys.argv)
    
    # Erstelle und zeige das Hauptfenster
    window = MainWindow()
    window.show()
    
    # Starte die Ereignisschleife
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())
