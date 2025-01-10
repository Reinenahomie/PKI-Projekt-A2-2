#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - PDF Bildextraktor Widget

Implementiert die Funktionalität zum Extrahieren von Bildern aus PDF-Dokumenten.
Das Widget bietet eine Vorschau der gefundenen Bilder und ermöglicht deren
Export in verschiedenen Formaten.

Funktionen:
- Automatische Erkennung aller Bildtypen (JPEG, PNG, etc.)
- Vorschau der gefundenen Bilder mit Metadaten
- Einzelexport oder Massenexport aller Bilder
- Beibehaltung der Bildqualität und Metadaten
- Unterstützung verschiedener Bildformate

Layout:
- Vertikales Hauptlayout
- Bildvorschaubereich mit Scrollfunktion
- Kontrollbereich für Export-Optionen
- Statusbereich für Fortschritt und Meldungen

Technische Details:
- Basiert auf QWidget und PyMuPDF
- Threadsichere Bildextraktion
- Optimierte Speicherverwaltung
- Fehlerbehandlung und Benutzer-Feedback

Verwendung:
    extractor = PDFImageExtractorWidget()
    extractor.show()
    
    # Bilder extrahieren
    extractor.extract_images()
    
    # Status prüfen
    if extractor.is_extracting:
        print("Extraktion läuft...")

Autor: Team A2-2
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, 
    QScrollArea, QGridLayout, QFrame, QHBoxLayout, QSizePolicy, QComboBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize
from ..utils.pdf_functions import extract_images_from_pdf
import os

class ImageContainer(QWidget):
    """Container für ein einzelnes Bild mit fester Größe."""
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)  # Größere Kacheln für bessere Platznutzung
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Label für das Bild
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #cccccc;
                background-color: white;
                padding: 10px;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Lade das Bild
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Skaliere das Bild auf 180x180 (200 - 2*10 padding)
            scaled_pixmap = pixmap.scaled(
                180, 180,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Vorschau\nnicht verfügbar")

class PDFImageExtractorWidget(QWidget):
    """
    Widget zur Extraktion von Bildern aus PDF-Dateien.
    
    Bietet eine Benutzeroberfläche zum Extrahieren und Vorschauen von Bildern
    aus PDF-Dokumenten. Die Bilder können einzeln oder als ZIP-Datei gespeichert
    werden. Das Widget zeigt eine Vorschau aller gefundenen Bilder in einem
    Raster-Layout an.
    
    Attribute:
        stacked_widget: Übergeordnetes StackedWidget für Navigation
        preview_container (QWidget): Container für die Bildvorschauen
        grid_layout (QGridLayout): Layout für die Bildanordnung
        initial_label (QLabel): Label für Statusanzeige
    
    Verwendung:
        widget = PDFImageExtractorWidget(stacked_widget)
        widget.show()
        
        # Bilder extrahieren
        widget.extract_images()
        
        # Als ZIP speichern
        widget.extract_images_to_zip()
    """

    def __init__(self, stacked_widget, parent=None):
        """
        Initialisiert das Bildextraktions-Widget.
        
        Args:
            stacked_widget: Übergeordnetes StackedWidget für Navigation
            parent (QWidget, optional): Übergeordnetes Widget
        """
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        
        # Layout erstellen
        layout = QVBoxLayout()                          # Hauptlayout für vertikale Anordnung
        layout.setContentsMargins(20, 0, 20, 20)       # Seitliche Ränder: 20px, oben: 0px
        layout.setSpacing(20)                          # Abstand zwischen Elementen: 20px

        # Scroll-Bereich für die Bildvorschauen
        scroll_area = QScrollArea()                    # Scrollbarer Bereich für große Bildmengen
        scroll_area.setWidgetResizable(True)           # Automatische Größenanpassung
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Horizontale Scrollbar bei Bedarf
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)    # Vertikale Scrollbar bei Bedarf
        
        # Container für das Grid
        self.preview_container = QWidget()             # Container für das Vorschauraster
        self.preview_container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)                                          # Grauer Hintergrund für besseren Kontrast
        
        # Grid-Layout für Bildvorschauen
        self.grid_layout = QGridLayout(self.preview_container)  # Rasteranordnung der Bilder
        self.grid_layout.setSpacing(15)               # Abstand zwischen den Bildern: 15px
        self.grid_layout.setContentsMargins(15, 15, 15, 15)  # Einheitliche Ränder: 15px
        self.grid_layout.setAlignment(Qt.AlignTop)    # Ausrichtung am oberen Rand
        
        # Initial-Label für Statusanzeige
        self.initial_label = QLabel("Keine Bilder gefunden.")  # Standardtext bei leerer Ansicht
        self.initial_label.setAlignment(Qt.AlignCenter)        # Zentrierte Textausrichtung
        self.grid_layout.addWidget(self.initial_label, 0, 0, 1, 3)  # Über drei Spalten zentriert
        
        # Layout zusammenbauen
        scroll_area.setWidget(self.preview_container)  # Container in Scroll-Bereich einsetzen
        layout.addWidget(scroll_area, 1)              # Scroll-Bereich mit Stretch-Faktor 1
        self.setLayout(layout)                        # Layout dem Widget zuweisen

    def show_preview(self):
        """
        Zeigt eine Vorschau der Bilder aus der aktuellen PDF.
        
        Extrahiert alle Bilder aus der aktuell geöffneten PDF und zeigt sie
        in einem Raster an. Die Bilder werden temporär gespeichert und beim
        Beenden der Anwendung automatisch gelöscht.
        
        Raises:
            Exception: Wenn die Bilder nicht geladen werden können
        """
        main_window = self.window()                   # Referenz auf Hauptfenster
        pdf_path = main_window.get_current_pdf()      # Pfad der aktuellen PDF
        
        if not pdf_path:
            self.initial_label.setText("Keine PDF-Datei geöffnet.")  # Info wenn keine PDF geladen
            return

        try:
            # Bestehende Vorschaubilder entfernen
            while self.grid_layout.count():           # Iteriere über alle Widgets
                item = self.grid_layout.takeAt(0)     # Entferne Widget aus Layout
                if item.widget():
                    item.widget().deleteLater()       # Widget aus Speicher entfernen

            # Extrahiere Bilder für die Vorschau
            images = extract_images_from_pdf(pdf_path, preview_only=True)  # Temporäre Extraktion
            
            if images:
                # Bilder in einem Grid mit 3 Spalten anordnen
                for index, image_path in enumerate(images):
                    container = ImageContainer(image_path)  # Container pro Bild
                    row = index // 3                       # Zeilenindex berechnen
                    col = index % 3                        # Spaltenindex (0-2)
                    self.grid_layout.addWidget(container, row, col, Qt.AlignTop)  # Im Grid platzieren
            else:
                # Wenn keine Bilder gefunden wurden
                label = QLabel("Keine Bilder in der PDF gefunden.")  # Info-Label erstellen
                label.setAlignment(Qt.AlignCenter)                   # Text zentrieren
                self.grid_layout.addWidget(label, 0, 0, 1, 3)       # Über drei Spalten anzeigen

        except Exception as e:
            # Fehlerbehandlung
            error_msg = f"Die Bilder konnten nicht geladen werden:\n{str(e)}"  # Fehlermeldung erstellen
            QMessageBox.critical(self, "Fehler beim Laden", error_msg)         # Fehlerdialog anzeigen

    def extract_images(self):
        """
        Extrahiert Bilder aus der PDF und speichert sie im gewählten Verzeichnis.
        
        Öffnet einen Dialog zur Verzeichnisauswahl und extrahiert alle Bilder
        aus der aktuellen PDF in das gewählte Verzeichnis. Die Bilder werden
        mit aussagekräftigen Namen versehen.
        
        Raises:
            Exception: Wenn die Bildextraktion fehlschlägt
        """
        main_window = self.window()                   # Referenz auf Hauptfenster
        pdf_path = main_window.get_current_pdf()      # Pfad der aktuellen PDF
        
        if not pdf_path:
            QMessageBox.warning(self, "Fehler", "Bitte öffnen Sie zuerst eine PDF-Datei.")
            return
            
        # Stelle sicher, dass das export_folder existiert
        export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "export_folder")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)                   # Erstelle Verzeichnis falls nötig
            
        # Zeige Verzeichnisauswahl-Dialog
        file_dialog = QFileDialog(self)               # Erstelle Dateidialog
        file_dialog.setWindowTitle("Speicherverzeichnis auswählen")  # Setze Fenstertitel
        file_dialog.setFileMode(QFileDialog.Directory)  # Nur Verzeichnisauswahl
        file_dialog.setViewMode(QFileDialog.List)       # Listenansicht
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)  # Nur Verzeichnisse anzeigen
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # PyQt Dialog verwenden
        file_dialog.setOption(QFileDialog.DontUseCustomDirectoryIcons, True)  # Standardicons
        
        # Setze Standardverzeichnis auf export_folder
        file_dialog.setDirectory(export_dir)          # Startverzeichnis setzen
        
        # Entferne "Files of type" Dropdown und Label
        for child in file_dialog.findChildren(QLabel):
            if child.text() == "Files of type:":
                child.hide()                          # Verstecke Label
        for child in file_dialog.findChildren(QComboBox):
            if child.parentWidget().findChild(QLabel).text() == "Files of type:":
                child.hide()                          # Verstecke Dropdown
        
        # Label für die Pfadanzeige erstellen
        path_label = QLabel("Ausgewähltes Verzeichnis:")  # Beschriftung
        path_label.setStyleSheet("QLabel { padding: 5px; font-weight: bold; }")  # Formatierung
        file_dialog.layout().addWidget(path_label)        # Zum Dialog hinzufügen
        
        path_value = QLabel()                            # Label für Pfadanzeige
        path_value.setStyleSheet("QLabel { padding: 5px; }")  # Formatierung
        file_dialog.layout().addWidget(path_value)       # Zum Dialog hinzufügen
        
        # Aktualisiere Pfadanzeige bei Verzeichniswechsel
        def update_path_label():
            current_path = file_dialog.directory().absolutePath()  # Aktueller Pfad
            path_value.setText(current_path)                       # Pfad anzeigen
        
        file_dialog.directoryEntered.connect(update_path_label)  # Signal verbinden
        update_path_label()                                      # Initial anzeigen
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            save_dir = file_dialog.selectedFiles()[0]  # Gewähltes Verzeichnis
            try:
                # Extrahiere und speichere Bilder
                extracted_images = extract_images_from_pdf(pdf_path, output_dir=save_dir)  # Extraktion
                
                # Zeige Erfolgsmeldung
                if extracted_images:
                    QMessageBox.information(self, "Erfolg", f"{len(extracted_images)} Bilder wurden erfolgreich extrahiert.")
                else:
                    QMessageBox.information(self, "Keine Bilder", "Es wurden keine Bilder in der PDF gefunden.")
                    
            except Exception as e:
                # Zeige Fehlermeldung
                QMessageBox.critical(self, "Fehler", f"Fehler beim Extrahieren der Bilder: {str(e)}")

    def extract_images_to_zip(self):
        """
        Extrahiert die Bilder aus der PDF und speichert sie in einer ZIP-Datei.
        
        Öffnet einen Dialog zur Auswahl des Speicherorts für die ZIP-Datei.
        Die Bilder werden temporär extrahiert und dann in einem ZIP-Archiv
        zusammengefasst. Der vorgeschlagene Dateiname enthält das aktuelle Datum.
        
        Raises:
            Exception: Wenn die ZIP-Erstellung fehlschlägt
        """
        main_window = self.window()                   # Referenz auf Hauptfenster
        pdf_path = main_window.get_current_pdf()      # Pfad der aktuellen PDF
        
        if not pdf_path:
            QMessageBox.warning(self, "Fehler", "Bitte öffnen Sie zuerst eine PDF-Datei.")
            return
            
        # Stelle sicher, dass das export_folder existiert
        export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "export_folder")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)                   # Erstelle Verzeichnis falls nötig
            
        # Erstelle standardisierten Dateinamen mit aktuellem Datum
        from datetime import datetime
        default_filename = f"Bilder_{datetime.now().strftime('%Y-%m-%d')}.zip"  # Dateiname mit Datum
        default_path = os.path.join(export_dir, default_filename)               # Vollständiger Pfad
            
        # Konfiguriere Dateiauswahl-Dialog
        file_dialog = QFileDialog(self)               # Erstelle Dialog
        file_dialog.setWindowTitle("ZIP-Datei speichern")  # Setze Titel
        file_dialog.setNameFilter("ZIP-Dateien (*.zip)")   # Nur ZIP-Dateien
        file_dialog.setViewMode(QFileDialog.List)          # Listenansicht
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)  # Speichermodus
        file_dialog.setDefaultSuffix("zip")               # Standard-Dateiendung
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # PyQt Dialog
        
        # Setze den vorgeschlagenen Dateinamen
        file_dialog.selectFile(default_path)          # Vorschlag setzen
        
        # Entferne "Files of type" Dropdown und Label
        for child in file_dialog.findChildren(QLabel):
            if child.text() == "Files of type:":
                child.hide()                          # Verstecke Label
        for child in file_dialog.findChildren(QComboBox):
            if child.parentWidget().findChild(QLabel).text() == "Files of type:":
                child.hide()                          # Verstecke Dropdown
        
        # Label für die Pfadanzeige erstellen
        path_label = QLabel("Ausgewähltes Verzeichnis:")  # Beschriftung
        path_label.setStyleSheet("QLabel { padding: 5px; font-weight: bold; }")  # Formatierung
        file_dialog.layout().addWidget(path_label)        # Zum Dialog hinzufügen
        
        path_value = QLabel()                            # Label für Pfadanzeige
        path_value.setStyleSheet("QLabel { padding: 5px; }")  # Formatierung
        file_dialog.layout().addWidget(path_value)       # Zum Dialog hinzufügen
        
        # Aktualisiere Pfadanzeige bei Verzeichniswechsel
        def update_path_label():
            current_path = file_dialog.directory().absolutePath()  # Aktueller Pfad
            path_value.setText(current_path)                       # Pfad anzeigen
        
        file_dialog.directoryEntered.connect(update_path_label)  # Signal verbinden
        update_path_label()                                      # Initial anzeigen
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            zip_path = file_dialog.selectedFiles()[0]  # Gewählter Speicherort
            try:
                # Temporäres Verzeichnis für die Bilder
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Bilder extrahieren
                    extracted_images = extract_images_from_pdf(pdf_path, output_dir=temp_dir)  # Extraktion
                    if extracted_images:
                        # ZIP erstellen
                        from ..utils.pdf_functions import create_zip_from_files
                        create_zip_from_files(extracted_images, zip_path)  # ZIP packen
                        QMessageBox.information(self, "Erfolg", f"{len(extracted_images)} Bilder wurden erfolgreich als ZIP-Datei gespeichert.")
                    else:
                        QMessageBox.information(self, "Keine Bilder", "Es wurden keine Bilder in der PDF gefunden.")
            except Exception as e:
                # Zeige Fehlermeldung
                QMessageBox.critical(self, "Fehler", f"Fehler beim Erstellen der ZIP-Datei: {str(e)}")
