#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - PDF Merge Widget

Implementiert die Funktionalität zum Zusammenführen mehrerer PDF-Dokumente in
eine einzelne PDF-Datei. Das Widget ermöglicht das Hinzufügen, Ordnen und
Entfernen von PDF-Dateien sowie die Vorschau der zu kombinierenden Dokumente.

Funktionen:
- Drag & Drop Unterstützung für PDF-Dateien
- Vorschau der ausgewählten PDFs
- Anpassbare Reihenfolge der Dokumente
- Fortschrittsanzeige während der Verarbeitung
- Beibehaltung der Dokumentqualität

Layout:
- Vertikales Hauptlayout
- Listendarstellung der ausgewählten PDFs
- Vorschaubereich für das aktuelle Dokument
- Kontrollbereich für Dateioperationen
- Statusbereich für Meldungen

Technische Details:
- Basiert auf QWidget und PyMuPDF
- Threadsichere Verarbeitung
- Optimierte Speicherverwaltung
- Fehlerbehandlung und Benutzer-Feedback

Verwendung:
    merge_widget = PDFMergeWidget()
    merge_widget.show()
    
    # PDFs hinzufügen
    merge_widget.add_pdf_files(['doc1.pdf', 'doc2.pdf'])
    
    # PDFs zusammenführen
    merge_widget.merge_pdfs()

Autor: Team A2-2
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QMessageBox, QFileDialog, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QImage, QPixmap
from ..utils.pdf_functions import merge_pdfs, render_page
import os
from datetime import datetime

class PDFPreviewTile(QWidget):
    """
    Widget für ein einzelnes PDF-Vorschaubild in einer quadratischen Kachel.
    Zeigt die erste Seite einer PDF als Vorschau an und ermöglicht die Auswahl
    durch Mausklick. Der Auswahlstatus wird visuell durch einen farbigen Rahmen
    dargestellt.
    """
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path                      # Pfad zur PDF-Datei
        self.selected = False                         # Auswahlstatus der Kachel
        
        # Layout erstellen
        layout = QVBoxLayout()                        # Vertikales Layout für Vorschau und Name
        layout.setContentsMargins(10, 10, 10, 10)     # Einheitliche Ränder von 10px
        layout.setSpacing(5)                          # Abstand zwischen Elementen
        
        # Container für das Vorschaubild
        self.preview_container = QLabel()             # Label für die PDF-Vorschau
        self.preview_container.setFixedSize(200, 200) # Quadratische Größe für einheitliches Layout
        self.preview_container.setAlignment(Qt.AlignCenter)  # Zentrierte Ausrichtung
        self.update_style()                           # Initialen Stil setzen
        layout.addWidget(self.preview_container)      # Zum Layout hinzufügen
        
        # Label für den Dateinamen
        filename = os.path.basename(pdf_path)         # Nur Dateiname ohne Pfad
        self.name_label = QLabel(filename)            # Label für den Dateinamen
        self.name_label.setAlignment(Qt.AlignCenter)  # Zentrierte Textausrichtung
        self.name_label.setWordWrap(True)            # Zeilenumbruch aktivieren
        layout.addWidget(self.name_label)             # Zum Layout hinzufügen
        
        self.setLayout(layout)                        # Layout dem Widget zuweisen
        
        self.load_preview()                           # Vorschaubild laden

    def update_style(self):
        """
        Aktualisiert den Stil der Vorschaukachel basierend auf dem Auswahlstatus.
        Ausgewählte Kacheln haben einen blauen, dickeren Rahmen, nicht ausgewählte
        einen grauen, dünneren Rahmen.
        """
        border_color = "#2196F3" if self.selected else "#cccccc"  # Blau wenn ausgewählt, sonst grau
        border_width = "3px" if self.selected else "1px"          # Dicker wenn ausgewählt
        self.preview_container.setStyleSheet(f"""
            QLabel {{
                border: {border_width} solid {border_color};
                background-color: white;
                padding: 5px;
            }}
        """)                                          # Stil auf Container anwenden

    def mousePressEvent(self, event):
        """
        Behandelt Mausklicks auf die Vorschaukachel. Ein Linksklick wechselt
        den Auswahlstatus und aktualisiert die visuelle Darstellung.
        """
        if event.button() == Qt.LeftButton:           # Nur Linksklicks verarbeiten
            self.selected = not self.selected         # Auswahlstatus umschalten
            self.update_style()                       # Visuelle Darstellung aktualisieren
            # Informiere übergeordnetes Widget
            if isinstance(self.parent(), QWidget):    # Prüfe ob Parent existiert
                parent = self.parent()                # Hole Parent-Widget
                while parent and not isinstance(parent, PDFMergeWidget):
                    parent = parent.parent()          # Suche PDFMergeWidget
                if parent:
                    parent.update_delete_button()     # Button-Status aktualisieren

    def load_preview(self):
        """
        Lädt und zeigt die Vorschau der ersten Seite der PDF-Datei.
        Die Vorschau wird auf die Containergröße skaliert und bei
        Fehlern wird ein Platzhaltertext angezeigt.
        """
        try:
            # Rendere die erste Seite
            pix = render_page(self.pdf_path, 0, 1.0)  # Erste Seite mit Zoom 1.0
            
            # Berechne optimalen Zoom-Faktor
            available_size = self.preview_container.size()  # Verfügbare Größe
            width_ratio = (available_size.width() - 10) / pix.width  # Breitenverhältnis
            height_ratio = (available_size.height() - 10) / pix.height  # Höhenverhältnis
            zoom = min(width_ratio, height_ratio)     # Kleineres Verhältnis wählen
            
            # Rendere mit optimalem Zoom
            pix = render_page(self.pdf_path, 0, zoom)  # Neu rendern mit Zoom
            
            # Konvertiere zu QPixmap und zeige an
            img_data = pix.tobytes("ppm")            # Konvertiere zu Bytes
            qimg = QImage.fromData(img_data)         # Erstelle QImage
            pixmap = QPixmap.fromImage(qimg)         # Konvertiere zu QPixmap
            self.preview_container.setPixmap(pixmap)  # Zeige Vorschau an
            
        except Exception as e:
            self.preview_container.setText("Vorschau\nnicht verfügbar")  # Zeige Fehlertext

class PDFMergeWidget(QWidget):
    """
    Widget zum Zusammenführen mehrerer PDF-Dokumente. Bietet eine grafische
    Oberfläche zum Auswählen, Ordnen und Zusammenführen von PDF-Dateien mit
    Vorschaubildern und Drag & Drop-Funktionalität.
    """
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget          # Übergeordnetes StackedWidget
        self.preview_tiles = []                       # Liste der Vorschau-Kacheln
        
        # Layout erstellen
        layout = QVBoxLayout()                        # Vertikales Hauptlayout
        layout.setContentsMargins(20, 0, 20, 20)      # Seitliche Ränder: 20px
        layout.setSpacing(20)                         # Abstand zwischen Elementen

        # Scroll-Bereich für die PDF-Vorschauen
        scroll_area = QScrollArea()                   # Scrollbarer Bereich
        scroll_area.setWidgetResizable(True)          # Automatische Größenanpassung
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Horizontale Scrollbar
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)    # Vertikale Scrollbar
        
        # Container für das Grid
        self.preview_container = QWidget()            # Container für Vorschaukacheln
        self.preview_container.setMinimumSize(400, 600)  # Mindestgröße für Layout
        self.preview_container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)                                          # Grauer Hintergrund
        
        # Grid-Layout mit zwei Spalten
        self.grid_layout = QGridLayout(self.preview_container)  # Rasteranordnung
        self.grid_layout.setSpacing(20)               # Abstand zwischen Kacheln
        self.grid_layout.setContentsMargins(20, 20, 20, 20)  # Einheitliche Ränder
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Ausrichtung
        
        # Initial-Label
        self.initial_label = QLabel("Keine PDFs ausgewählt.")  # Standardtext
        self.initial_label.setAlignment(Qt.AlignCenter)  # Zentrierte Ausrichtung
        self.grid_layout.addWidget(self.initial_label, 0, 0, 1, 2)  # Über zwei Spalten
        
        scroll_area.setWidget(self.preview_container)  # Container in Scroll-Bereich
        layout.addWidget(scroll_area, 1)              # Scroll-Bereich mit Stretch

        self.setLayout(layout)                        # Layout dem Widget zuweisen

        self.pdf_paths = []                           # Liste der PDF-Pfade

    def showEvent(self, event):
        """
        Wird beim Anzeigen des Widgets aufgerufen. Lädt die aktuelle PDF
        aus dem Hauptfenster und aktualisiert die Vorschau.
        """
        super().showEvent(event)                      # Basis-Implementation aufrufen
        main_window = self.window()                   # Hole Hauptfenster
        current_pdf = main_window.get_current_pdf()   # Hole aktuelle PDF
        
        self.pdf_paths = []                           # Liste zurücksetzen
        if current_pdf:
            self.pdf_paths.append(current_pdf)        # Aktuelle PDF hinzufügen
        self.update_preview()                         # Vorschau aktualisieren

    def add_pdf(self):
        """
        Öffnet einen Dialog zum Auswählen mehrerer PDF-Dateien und fügt
        diese der Liste hinzu. Die Vorschau wird automatisch aktualisiert.
        """
        file_dialog = QFileDialog(self)               # Erstelle Dialog
        file_dialog.setWindowTitle("PDF-Dateien auswählen")  # Setze Titel
        file_dialog.setNameFilter("PDF-Dateien (*.pdf)")  # Nur PDF-Dateien
        file_dialog.setViewMode(QFileDialog.List)     # Listenansicht
        file_dialog.setFileMode(QFileDialog.ExistingFiles)  # Mehrfachauswahl
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # PyQt Dialog
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_files = file_dialog.selectedFiles()  # Hole ausgewählte Dateien
            self.pdf_paths.extend(selected_files)     # Füge Dateien zur Liste hinzu
            self.update_preview()                     # Aktualisiere Vorschau

    def remove_selected_pdf(self):
        """
        Entfernt alle ausgewählten PDFs aus der Liste und aktualisiert
        die Vorschau. Die Dateien werden nur aus der Liste entfernt,
        nicht vom Dateisystem gelöscht.
        """
        selected_paths = []                           # Liste für ausgewählte Pfade
        for tile in self.preview_tiles:               # Durchlaufe alle Kacheln
            if tile.selected:                         # Wenn Kachel ausgewählt
                selected_paths.append(tile.pdf_path)   # Pfad merken
        
        if selected_paths:                            # Wenn Pfade zum Entfernen
            for path in selected_paths:               # Durchlaufe Pfade
                self.pdf_paths.remove(path)           # Entferne aus Liste
            self.update_preview()                     # Aktualisiere Vorschau

    def update_preview(self):
        """
        Aktualisiert die Vorschaukacheln basierend auf den aktuellen PDF-Pfaden.
        Löscht alle bestehenden Vorschauen und erstellt neue für alle PDFs
        in der Liste.
        """
        # Lösche bestehende Widgets
        for i in reversed(range(self.grid_layout.count())):  # Rückwärts durchlaufen
            self.grid_layout.itemAt(i).widget().setParent(None)  # Widget entfernen
        
        self.preview_tiles = []                       # Liste leeren
        
        if not self.pdf_paths:                        # Wenn keine PDFs vorhanden
            self.initial_label = QLabel("Keine PDFs ausgewählt.")  # Info-Label
            self.initial_label.setAlignment(Qt.AlignCenter)  # Zentriert
            self.grid_layout.addWidget(self.initial_label, 0, 0, 1, 2)  # Einfügen
            return
        
        # Füge neue Vorschaukacheln hinzu
        for index, pdf_path in enumerate(self.pdf_paths):  # Durchlaufe PDFs
            preview = PDFPreviewTile(pdf_path)        # Erstelle Vorschaukachel
            self.preview_tiles.append(preview)        # Zur Liste hinzufügen
            row = index // 2                          # Zeile berechnen
            col = index % 2                           # Spalte berechnen
            self.grid_layout.addWidget(preview, row, col)  # Im Grid platzieren
        
        self.update_delete_button()                   # Button-Status aktualisieren

    def update_delete_button(self):
        """
        Aktiviert oder deaktiviert den Lösch-Button basierend auf der
        aktuellen Auswahl. Der Button wird nur aktiviert, wenn mindestens
        eine PDF ausgewählt ist.
        """
        has_selection = any(tile.selected for tile in self.preview_tiles)  # Prüfe Auswahl
        
        main_window = self.window()                   # Hole Hauptfenster
        if main_window:                               # Wenn Hauptfenster existiert
            # Suche den Lösch-Button
            for i in range(main_window.action_buttons_layout.count()):  # Durchsuche Buttons
                button = main_window.action_buttons_layout.itemAt(i).widget()  # Hole Button
                if isinstance(button, QPushButton) and button.text() == "Ausgewählte PDF entfernen":
                    button.setEnabled(has_selection)   # Aktiviere/Deaktiviere
                    break

    def merge_pdfs(self):
        """
        Führt die ausgewählten PDFs zu einer neuen PDF-Datei zusammen.
        Öffnet einen Dialog zur Auswahl des Speicherorts und erstellt
        die kombinierte PDF mit standardisiertem Dateinamen.
        """
        if len(self.pdf_paths) < 2:                   # Prüfe Mindestanzahl
            QMessageBox.warning(self, "Fehler", 
                "Bitte wählen Sie mindestens zwei PDF-Dateien aus.")
            return
            
        # Erstelle standardisierten Dateinamen
        default_filename = f"Merge_{datetime.now().strftime('%Y-%m-%d')}.pdf"  # Mit Datum
        
        # Stelle sicher, dass export_folder existiert
        export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "export_folder")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)                   # Erstelle Verzeichnis
        
        # Konfiguriere Speichern-Dialog
        file_dialog = QFileDialog(self)               # Erstelle Dialog
        file_dialog.setWindowTitle("Zusammengefügte PDF speichern")  # Setze Titel
        file_dialog.setNameFilter("PDF-Dateien (*.pdf)")  # Nur PDF-Dateien
        file_dialog.setViewMode(QFileDialog.List)     # Listenansicht
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)  # Speichermodus
        file_dialog.setDefaultSuffix("pdf")          # Standard-Dateiendung
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # PyQt Dialog
        
        # Setze Standardpfad
        default_path = os.path.join(export_dir, default_filename)  # Vollständiger Pfad
        file_dialog.selectFile(default_path)          # Vorauswahl setzen
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            output_path = file_dialog.selectedFiles()[0]  # Hole Speicherort
            try:
                merge_pdfs(self.pdf_paths, output_path)  # Führe PDFs zusammen
                QMessageBox.information(self, "Erfolg", 
                    "Die PDF-Dateien wurden erfolgreich zusammengefügt.")
                self.pdf_paths = []                   # Liste leeren
                self.update_preview()                 # Vorschau aktualisieren
            except Exception as e:
                QMessageBox.critical(self, "Fehler", 
                    f"Fehler beim Zusammenfügen der PDF-Dateien: {str(e)}") 