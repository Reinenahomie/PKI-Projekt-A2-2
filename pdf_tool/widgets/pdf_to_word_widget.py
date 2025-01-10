#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - PDF zu Word Widget

Implementiert die Funktionalität zur Konvertierung von PDF-Dokumenten in das
Word-Format (DOCX). Das Widget bietet eine Vorschau der PDF und führt die
Konvertierung mit bestmöglicher Beibehaltung von Layout und Formatierung durch.

Funktionen:
- Vorschau der zu konvertierenden PDF
- Automatische Konvertierung nach Word
- Fortschrittsanzeige während der Verarbeitung
- Beibehaltung von Text, Tabellen und Bildern
- Intelligente Layout-Erkennung

Layout:
- Vertikales Hauptlayout
- Vorschaubereich für die aktuelle PDF-Seite
- Statusbereich für Fortschritt und Meldungen
- Informationsbereich für Ausgabepfad

Technische Details:
- Basiert auf QWidget und python-docx
- Threadsichere Konvertierung
- Optimierte Text- und Layout-Extraktion
- Fehlerbehandlung und Benutzer-Feedback

Verwendung:
    word_widget = PDFToWordWidget()
    word_widget.show()
    
    # PDF konvertieren
    word_widget.convert_to_word()
    
    # Status prüfen
    if word_widget.is_converting:
        print("Konvertierung läuft...")

Autor: Team A2-2
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QMessageBox, QScrollArea, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
from ..utils.pdf_functions import pdf_to_word, render_page, show_save_dialog
from pdf2docx import Converter
import os

class ConversionThread(QThread):
    """Thread für die separate Ausführung der PDF zu DOCX Konvertierung."""
    finished = pyqtSignal(bool, str)  # Signal für Konvertierungsstatus und Fehlermeldung
    timeout = 15  # Maximale Ausführungszeit in Sekunden

    def __init__(self, pdf_path, output_path):
        """Initialisiert den Konvertierungs-Thread."""
        super().__init__()
        self.pdf_path = pdf_path        # Pfad zur Eingabe-PDF
        self.output_path = output_path  # Pfad für die Ausgabe-DOCX
        self._is_running = True         # Flag für laufende Konvertierung
        self.cv = None                  # Converter-Instanz

    def stop(self):
        """Stoppt den Konvertierungsprozess sicher."""
        self._is_running = False                # Setze Stopp-Flag
        if self.cv:
            try:
                self.cv.close()                 # Schließe Converter falls vorhanden
            except:
                pass
        self.terminate()                        # Erzwinge Thread-Beendigung

    def run(self):
        """Führt die eigentliche Konvertierung durch."""
        try:
            # Starte Watchdog-Timer für Timeout-Überwachung
            watchdog = QTimer()                 # Timer für Timeout-Überwachung
            watchdog.setSingleShot(True)        # Timer läuft nur einmal
            watchdog.timeout.connect(self.stop) # Verbinde mit Stopp-Funktion
            watchdog.start(self.timeout * 1000) # Starte Timer mit Timeout in ms
            
            # Führe Konvertierung durch
            self.cv = Converter(self.pdf_path)  # Erstelle Converter-Instanz
            if not self._is_running:            # Prüfe auf vorzeitigen Abbruch
                raise Exception("Timeout")
                
            self.cv.convert(self.output_path)   # Starte Konvertierung
            self.cv.close()                     # Schließe Converter
            
            if self._is_running:
                self.finished.emit(True, "")     # Signalisiere erfolgreiche Konvertierung
            else:
                # Lösche unvollständige Ausgabedatei bei Abbruch
                try:
                    if os.path.exists(self.output_path):
                        os.remove(self.output_path)  # Entferne unvollständige Datei
                except:
                    pass
                self.finished.emit(False, "Konvertierung nicht möglich: Die PDF enthält möglicherweise komplexe Vektorgrafiken oder andere nicht unterstützte Elemente.")
            
        except Exception as e:
            # Fehlerbehandlung bei Konvertierungsproblemen
            try:
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)  # Entferne fehlerhafte Ausgabedatei
            except:
                pass
            
            if not self._is_running:
                self.finished.emit(False, "Konvertierung nicht möglich: Die PDF enthält möglicherweise komplexe Vektorgrafiken oder andere nicht unterstützte Elemente.")
            else:
                self.finished.emit(False, str(e))  # Gebe Original-Fehlermeldung zurück

class ConversionDialog(QMessageBox):
    """Dialog zur Anzeige des Konvertierungsfortschritts mit Animation."""
    def __init__(self, parent=None):
        """Initialisiert den Konvertierungsdialog."""
        super().__init__(parent)
        self.setIcon(QMessageBox.Information)    # Setze Info-Icon
        self.setWindowTitle("Konvertierung")     # Setze Fenstertitel
        self.setText("Konvertierung des PDF-Dokumentes\nnach DOCX")  # Setze Anfangstext
        self.setStandardButtons(QMessageBox.NoButton)  # Keine Buttons initial
        
        # Initialisiere Animation
        self.dots = ""                           # Punkte für Animation
        self.timer = QTimer(self)                # Timer für Animation
        self.timer.timeout.connect(self.update_animation)  # Verbinde mit Update-Funktion
        self.timer.start(500)                    # Starte Timer (500ms Intervall)
        
    def update_animation(self):
        """Aktualisiert die animierten Punkte im Dialog."""
        self.dots = "." * ((len(self.dots) + 1) % 4)  # Aktualisiere Animations-Punkte
        self.setText(f"Konvertierung des PDF-Dokumentes\nnach DOCX{self.dots}")  # Aktualisiere Text
        
    def conversion_finished(self, success, error_msg=None):
        """Zeigt das Ergebnis der Konvertierung an."""
        self.timer.stop()                        # Stoppe Animation
        if success:
            self.setText("Konvertierung des PDF-Dokumentes\nnach DOCX - Erfolg!")  # Erfolgstext
            self.setStandardButtons(QMessageBox.Ok)  # Zeige OK-Button
        else:
            self.setIcon(QMessageBox.Critical)   # Setze Fehler-Icon
            self.setText(f"Die PDF konnte nicht konvertiert werden:\n{error_msg}")  # Fehlertext
            self.setStandardButtons(QMessageBox.Ok)  # Zeige OK-Button

class PDFToWordWidget(QWidget):
    """Widget zur Konvertierung von PDF-Dokumenten in das DOCX-Format."""
    def __init__(self, stacked_widget, parent=None):
        """Initialisiert das PDF zu Word Konvertierungs-Widget."""
        super().__init__(parent)
        self.stacked_widget = stacked_widget      # Übergeordnetes Widget
        self.conversion_thread = None             # Thread für Konvertierung
        
        # Erstelle Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 0, 20, 20)  # Setze Randabstände
        layout.setSpacing(10)                      # Setze Abstand zwischen Elementen

        # Erstelle Vorschau-Container
        preview_container = QWidget()
        preview_container.setMinimumSize(400, 600)  # Setze Mindestgröße
        preview_container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)                                        # Setze Stil
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)  # Keine Ränder
        preview_layout.setSpacing(0)                    # Kein Abstand

        # Erstelle scrollbaren Vorschaubereich
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)           # Ermögliche Größenanpassung
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Horizontale Scrollbar
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)    # Vertikale Scrollbar
        scroll_area.setContentsMargins(0, 0, 0, 0)     # Keine Ränder
        
        # Erstelle Vorschau-Label
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)  # Zentriere Inhalt
        scroll_area.setWidget(self.preview_label)        # Füge Label hinzu
        preview_layout.addWidget(scroll_area)            # Füge Scroll-Bereich hinzu
        
        layout.addWidget(preview_container, 1)           # Füge Container hinzu

        self.setLayout(layout)                          # Setze Layout

    def showEvent(self, event):
        """Wird beim Anzeigen des Widgets aufgerufen."""
        super().showEvent(event)
        main_window = self.window()                     # Hole Hauptfenster
        pdf_path = main_window.get_current_pdf()        # Hole aktuelle PDF
        
        if pdf_path:
            self.show_preview(pdf_path)                 # Zeige Vorschau
        else:
            self.preview_label.clear()                  # Lösche Vorschau
            self.preview_label.setText("Keine PDF-Datei geöffnet")  # Zeige Info-Text

    def show_preview(self, pdf_path):
        """Zeigt eine Vorschau der ersten PDF-Seite."""
        try:
            # Rendere erste Seite
            pix = render_page(pdf_path, 0, 1.0)        # Rendere in Originalgröße
            
            # Berechne optimalen Zoom
            visible_width = self.preview_label.parent().width() - 40   # Verfügbare Breite
            visible_height = self.preview_label.parent().height() - 40  # Verfügbare Höhe
            width_ratio = visible_width / pix.width      # Breiten-Verhältnis
            height_ratio = visible_height / pix.height   # Höhen-Verhältnis
            zoom = min(width_ratio, height_ratio)        # Optimaler Zoom-Faktor
            
            # Rendere mit Zoom
            pix = render_page(pdf_path, 0, zoom)         # Rendere in angepasster Größe
            
            # Konvertiere und zeige an
            img_data = pix.tobytes("ppm")               # Konvertiere zu Bilddaten
            qimg = QImage.fromData(img_data)            # Erstelle QImage
            pixmap = QPixmap.fromImage(qimg)            # Konvertiere zu Pixmap
            self.preview_label.setPixmap(pixmap)        # Zeige Vorschau
            
        except Exception as e:
            self.preview_label.clear()                  # Lösche Vorschau
            self.preview_label.setText(f"Fehler beim Laden der Vorschau:\n{str(e)}")  # Zeige Fehler

    def convert_to_word(self):
        """Startet die Konvertierung der PDF in DOCX."""
        # Hole aktuelle PDF
        main_window = self.window()                     # Hole Hauptfenster
        pdf_path = main_window.get_current_pdf()        # Hole PDF-Pfad
        
        if not pdf_path:
            QMessageBox.warning(
                self,
                "Keine PDF geöffnet",
                "Bitte öffnen Sie zuerst eine PDF-Datei."
            )                                           # Zeige Warnung
            return

        # Bestimme Ausgabepfad
        default_name = os.path.basename(pdf_path).rsplit('.', 1)[0] + '.docx'  # Erstelle Standardnamen
        output_path = show_save_dialog(
            self,
            "Word-Dokument speichern",
            default_name,
            ("Word Dateien", "*.docx"),
            use_export_dir=True                         # Nutze Export-Verzeichnis
        )
        
        if output_path:
            try:
                # Starte Konvertierung
                self.progress_dialog = ConversionDialog(self)  # Erstelle Dialog
                self.progress_dialog.show()                    # Zeige Dialog
                QApplication.processEvents()                   # Aktualisiere UI
                
                # Erstelle und starte Thread
                self.conversion_thread = ConversionThread(pdf_path, output_path)  # Erstelle Thread
                self.conversion_thread.finished.connect(self.conversion_finished)  # Verbinde Signal
                self.conversion_thread.start()                                    # Starte Thread
                
            except Exception as e:
                if hasattr(self, 'progress_dialog'):
                    self.progress_dialog.conversion_finished(False, str(e))  # Zeige Fehler

    def conversion_finished(self, success, error_msg):
        """Wird nach Abschluss der Konvertierung aufgerufen."""
        try:
            if hasattr(self, 'progress_dialog') and self.progress_dialog:
                self.progress_dialog.conversion_finished(success, error_msg)  # Aktualisiere Dialog
                
            if hasattr(self, 'conversion_thread') and self.conversion_thread:
                self.conversion_thread.wait()    # Warte auf Thread-Ende
                self.conversion_thread = None    # Lösche Thread-Referenz
                
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Fehler beim Abschluss der Konvertierung:\n{str(e)}"
            ) 