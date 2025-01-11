#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - Startskript

Dieses Skript startet die PDF Tool Anwendung. Es initialisiert die
Qt-Anwendung und das Hauptfenster.

Verwendung:
    python run.py

Technische Details:
- Verwendet PyQt5 für die GUI
- Importiert die Hauptanwendung aus dem pdf_tool Paket
- Fehlerbehandlung beim Start

Autor: Team A2-2
"""

import sys
from PyQt5.QtWidgets import QApplication
from pdf_tool.gui_components.gui import MainWindow

def main():
    """
    Hauptfunktion zum Starten der Anwendung.
    
    Erstellt die Qt-Anwendung und das Hauptfenster.
    Startet die Ereignisschleife.
    
    Returns:
        int: Exit-Code der Anwendung
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())

