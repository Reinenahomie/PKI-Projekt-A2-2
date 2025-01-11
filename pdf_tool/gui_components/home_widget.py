#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - Home Widget

Implementiert die Startseite des PDF Tools mit einer übersichtlichen
Darstellung aller verfügbaren Funktionen. Das Widget dient als zentrale
Navigationsoberfläche und Einstiegspunkt für die Benutzer.

Funktionen:
- Übersichtliche Darstellung aller PDF-Werkzeuge
- Intuitive Navigation durch große, beschriftete Buttons
- Informative Beschreibungen der Funktionen
- Direkter Zugriff auf alle Hauptfunktionen
- Responsive Benutzeroberfläche

Layout:
- Vertikales Hauptlayout
- Rasteranordnung der Funktionsbuttons
- Informationsbereich für Beschreibungen
- Statusbereich für Systemmeldungen

Technische Details:
- Basiert auf QWidget
- Dynamische Layout-Anpassung
- Einheitliches Styling der Buttons
- Fehlerbehandlung und Benutzer-Feedback

Verwendung:
    home = HomeWidget()
    home.show()
    
    # Navigation zu einer Funktion
    home.navigate_to('pdf_split')
    
    # Button-Status aktualisieren
    home.update_button_states()

Autor: Team A2-2
"""

import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from pdf_tool.config import HOME_IMAGE_PATH

class HomeWidget(QWidget):
    """Widget für die Anzeige der Startseite des PDF Tools."""
    def __init__(self, parent=None):
        """Initialisiert das Startseiten-Widget."""
        super().__init__(parent)
        
        # Erstelle Layout
        layout = QVBoxLayout()                                # Vertikales Layout für die Seite
        layout.setContentsMargins(20, 0, 20, 20)             # Setze Randabstände, oben kein Rand
        layout.setSpacing(20)                                # Setze Abstand zwischen Elementen
        
        # Erstelle Container mit grauem Hintergrund
        container = QWidget()                                # Container für den Hauptinhalt
        container.setMinimumSize(400, 600)                   # Setze Mindestgröße wie andere Widgets
        container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)                                                 # Setze Hintergrundfarbe
        container_layout = QVBoxLayout(container)            # Layout für den Container
        container_layout.setContentsMargins(20, 20, 20, 20)  # Setze innere Abstände
        container_layout.setSpacing(10)                      # Setze Abstand zwischen Elementen
        
        # Erstelle Label für das Startbild
        label = QLabel()                                     # Label für Bild oder Fehlermeldung
        label.setAlignment(Qt.AlignCenter)                   # Zentriere den Inhalt
        label.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)                                                 # Mache Hintergrund transparent

        # Lade und zeige das Startbild
        if os.path.exists(HOME_IMAGE_PATH):
            pixmap = QPixmap(HOME_IMAGE_PATH)                # Lade das Startbild
            label.setPixmap(pixmap)                          # Zeige das Bild im Label
        else:
            label.setText("Startbild nicht gefunden.")       # Zeige Fehlermeldung

        # Füge Komponenten zum Layout hinzu
        container_layout.addWidget(label)                    # Füge Label zum Container
        layout.addWidget(container, 1)                       # Füge Container zum Hauptlayout
        
        self.setLayout(layout)                              # Setze das Hauptlayout 