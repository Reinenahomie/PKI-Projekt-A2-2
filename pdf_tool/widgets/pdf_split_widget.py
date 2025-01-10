#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - PDF Split Widget

Implementiert die Funktionalität zum Aufteilen von PDF-Dokumenten in einzelne
Seiten. Das Widget ermöglicht das Aufteilen einer PDF-Datei in separate
PDF-Dateien, wobei jede Seite als eigenständige Datei gespeichert wird.

Funktionen:
- Automatisches Aufteilen in Einzelseiten
- Vorschau der PDF-Seiten
- Auswahl des Zielverzeichnisses
- Fortschrittsanzeige während der Verarbeitung
- Beibehaltung der Seitenqualität
- Automatische Benennung der Ausgabedateien

Layout:
- Vertikales Hauptlayout
- Vorschaubereich für die aktuelle PDF-Seite
- Statusbereich für Fortschritt und Meldungen
- Informationsbereich für Ausgabepfad

Technische Details:
- Basiert auf QWidget und PyMuPDF
- Threadsichere Verarbeitung
- Optimierte Speicherverwaltung
- Fehlerbehandlung und Benutzer-Feedback

Verwendung:
    split_widget = PDFSplitWidget()
    split_widget.show()
    
    # PDF aufteilen
    split_widget.split_pdf()
    
    # Status prüfen
    if split_widget.is_splitting:
        print("Aufteilung läuft...")

Autor: Team A2-2
"""

import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QProgressBar,
    QMessageBox
)
from PyQt5.QtCore import Qt

from pdf_tool.utils import split_pdf_into_pages, show_directory_dialog

class PDFSplitWidget(QWidget):
    """
    Widget zum Trennen von PDF-Dokumenten in Einzelseiten.
    
    Bietet eine Benutzeroberfläche zum Aufteilen einer PDF-Datei in separate
    Dateien für jede einzelne Seite. Der Benutzer kann das Zielverzeichnis
    auswählen und der Prozess zeigt den Fortschritt an.
    
    Attribute:
        is_processing (bool): Gibt an, ob gerade eine Verarbeitung läuft
        status_label (QLabel): Label für Statusmeldungen
        progress_bar (QProgressBar): Fortschrittsanzeige
        output_label (QLabel): Zeigt den Ausgabepfad an
    
    Verwendung:
        widget = PDFSplitWidget()
        widget.show()
        
        # PDF trennen
        widget.split_pdf()
    """
    def __init__(self, stacked_widget, parent=None):
        """
        Initialisiert das PDF-Split-Widget mit allen notwendigen Steuerelementen.
        Erstellt das Layout und initialisiert die Komponenten für die Benutzeroberfläche
        zur Aufteilung von PDF-Dokumenten in Einzelseiten.
        """
        super().__init__(parent)
        self.stacked_widget = stacked_widget          # Übergeordnetes StackedWidget
        self.is_processing = False                    # Flag für laufende Verarbeitung
        
        # Layout erstellen
        layout = QVBoxLayout()                        # Vertikales Hauptlayout
        layout.setContentsMargins(20, 0, 20, 20)      # Seitliche Ränder: 20px
        layout.setSpacing(10)                         # Abstand zwischen Elementen

        # Container für die Vorschau
        preview_container = QWidget()                 # Container für den Vorschaubereich
        preview_container.setMinimumSize(400, 600)    # Mindestgröße für Hochformat
        preview_container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)                                          # Grauer Hintergrund
        preview_layout = QVBoxLayout(preview_container)  # Layout für Container
        preview_layout.setContentsMargins(20, 20, 20, 20)  # Innere Ränder
        
        # Status-Label
        self.status_label = QLabel("Bereit zum Trennen der PDF")  # Status-Anzeige
        self.status_label.setAlignment(Qt.AlignCenter)  # Zentrierte Ausrichtung
        preview_layout.addWidget(self.status_label)   # Zum Layout hinzufügen
        
        # Fortschrittsbalken
        self.progress_bar = QProgressBar()            # Fortschrittsanzeige
        self.progress_bar.setVisible(False)           # Initial ausgeblendet
        preview_layout.addWidget(self.progress_bar)   # Zum Layout hinzufügen
        
        # Ausgabepfad-Label
        self.output_label = QLabel()                  # Label für Ausgabepfad
        self.output_label.setAlignment(Qt.AlignCenter)  # Zentrierte Ausrichtung
        self.output_label.setWordWrap(True)          # Zeilenumbruch aktivieren
        preview_layout.addWidget(self.output_label)   # Zum Layout hinzufügen
        
        layout.addWidget(preview_container, 1)        # Container mit Stretch-Faktor 1
        self.setLayout(layout)                        # Layout dem Widget zuweisen
        
    def split_pdf(self):
        """
        Teilt die aktuelle PDF in einzelne Seiten auf.
        Zeigt einen Dialog zur Auswahl des Zielverzeichnisses, führt die Aufteilung
        durch und speichert die einzelnen Seiten als separate PDF-Dateien.
        Aktualisiert die Benutzeroberfläche während des Prozesses.
        """
        if self.is_processing:                        # Wenn bereits Verarbeitung läuft
            return
            
        # Hole die aktuelle PDF vom Hauptfenster
        main_window = self.window()                   # Hole Hauptfenster-Referenz
        pdf_path = main_window.get_current_pdf()      # Hole aktuellen PDF-Pfad
        
        if not pdf_path:                             # Wenn keine PDF geöffnet
            QMessageBox.warning(
                self,
                "Keine PDF geöffnet",
                "Bitte öffnen Sie zuerst eine PDF-Datei."
            )                                         # Zeige Warnung
            return
            
        # Zeige Dialog zur Verzeichnisauswahl
        output_dir = show_directory_dialog(
            self,
            "Zielverzeichnis auswählen",
            use_export_dir=True
        )                                            # Öffne Verzeichnisauswahl
        
        if not output_dir:                           # Wenn kein Verzeichnis gewählt
            return
            
        try:
            self.is_processing = True                 # Setze Verarbeitungs-Flag
            self.status_label.setText("Trenne PDF in Einzelseiten...")  # Update Status
            self.progress_bar.setVisible(True)        # Zeige Fortschrittsbalken
            self.progress_bar.setRange(0, 0)          # Unbestimmter Fortschritt
            
            # Trenne die PDF
            page_files = split_pdf_into_pages(pdf_path, output_dir)  # Führe Trennung durch
            
            # Zeige Erfolgsmeldung
            timestamp = os.path.basename(os.path.dirname(page_files[0]))  # Hole Zeitstempel
            output_path = os.path.join(output_dir, timestamp)  # Erstelle Ausgabepfad
            
            self.status_label.setText("PDF erfolgreich getrennt!")  # Update Status
            self.output_label.setText(f"Die einzelnen Seiten wurden gespeichert unter:\n{output_path}")  # Zeige Pfad
            
            QMessageBox.information(
                self,
                "PDF getrennt",
                f"Die PDF wurde erfolgreich in {len(page_files)} Einzelseiten aufgeteilt.\n\n"
                f"Die Dateien wurden gespeichert unter:\n{output_path}"
            )                                         # Zeige Erfolgsmeldung
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Trennen der PDF:\n{str(e)}"
            )                                         # Zeige Fehlermeldung
            self.status_label.setText("Fehler beim Trennen der PDF")  # Update Status
            
        finally:
            self.is_processing = False                # Setze Verarbeitungs-Flag zurück
            self.progress_bar.setVisible(False)       # Verstecke Fortschrittsbalken 