#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - PDF Preview Widget

Implementiert eine fortschrittliche Vorschaufunktion für PDF-Dokumente mit
Zoom- und Navigationsmöglichkeiten. Das Widget ermöglicht das komfortable
Betrachten von PDF-Dateien mit verschiedenen Anzeigeoptionen.

Funktionen:
- Hochqualitative PDF-Vorschau
- Stufenloser Zoom (Vergrößern/Verkleinern)
- Navigation zwischen Seiten
- Anpassbare Darstellungsgröße
- Seitenrotation und -anpassung
- Statusanzeige mit Seitenzahlen

Layout:
- Vertikales Hauptlayout
- Scrollbarer Vorschaubereich
- Navigationselemente (Vor/Zurück)
- Zoom-Kontrollen
- Statusleiste

Technische Details:
- Basiert auf QWidget und PyMuPDF
- Threadsichere Rendering-Engine
- Optimierte Speicherverwaltung
- Cache-System für schnelle Darstellung
- Fehlerbehandlung und Benutzer-Feedback

Verwendung:
    preview = PDFPreviewWidget()
    preview.show()
    
    # PDF laden
    preview.load_pdf('document.pdf')
    
    # Zoom anpassen
    preview.set_zoom(1.5)  # 150%
    
    # Zur Seite springen
    preview.goto_page(3)

Autor: Team A2-2
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QMessageBox, QScrollArea, QApplication, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from ..utils.pdf_functions import load_pdf, render_page, show_pdf_open_dialog
import os

class PDFPreviewWidget(QWidget):
    """
    Widget zur Anzeige und Navigation von PDF-Dokumenten.
    
    Bietet eine interaktive Vorschau von PDF-Dateien mit Navigationsmöglichkeiten
    und Zoom-Funktionen. Das Widget verwaltet den Zustand der PDF-Anzeige und
    kommuniziert Änderungen an das Hauptfenster.
    
    Attribute:
        current_page (int): Aktuelle Seitennummer (0-basiert)
        total_pages (int): Gesamtanzahl der Seiten
        pdf_path (str): Pfad zur aktuellen PDF-Datei
        preview_label (QLabel): Label für die PDF-Vorschau
        page_label (QLabel): Label für die Seitennummerierung
    
    Signals:
        pdf_opened (str): Signal wenn eine neue PDF geöffnet wurde
        
    Verwendung:
        widget = PDFPreviewWidget()
        widget.pdf_opened.connect(on_pdf_opened)  # Signal verbinden
        widget.show()
    """
    
    # Signal das emittiert wird, wenn eine PDF geöffnet wurde
    pdf_opened = pyqtSignal(str)

    def __init__(self, stacked_widget, parent=None):
        """
        Initialisiert das PDF-Vorschau-Widget mit allen notwendigen Steuerelementen
        für die Navigation und Zoom-Funktionen.
        """
        super().__init__(parent)
        self.stacked_widget = stacked_widget          # Übergeordnetes StackedWidget
        self.current_page = 0                         # Aktuelle Seitennummer (0-basiert)
        self.total_pages = 0                         # Gesamtanzahl der Seiten
        self.pdf_path = None                         # Pfad zur aktuellen PDF
        self.zoom_factor = 1.0                       # Aktueller Zoom-Faktor (100%)
        self.base_zoom = 1.0                         # Basis-Zoom für 100% Darstellung
        self.render_quality = 2.0  # Faktor für höhere Renderqualität
        
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
        preview_layout.setContentsMargins(0, 0, 0, 0)   # Keine inneren Ränder

        # Scroll-Bereich für die Vorschau
        self.scroll_area = QScrollArea()              # Scrollbarer Bereich
        self.scroll_area.setWidgetResizable(True)     # Automatische Größenanpassung
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Horizontale Scrollbar
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)    # Vertikale Scrollbar
        
        # Vorschaubereich
        self.preview_label = QLabel()                 # Label für PDF-Vorschau
        self.preview_label.setAlignment(Qt.AlignCenter)  # Zentrierte Ausrichtung
        self.scroll_area.setWidget(self.preview_label)  # Label in Scroll-Bereich
        preview_layout.addWidget(self.scroll_area)    # Scroll-Bereich in Container
        
        layout.addWidget(preview_container, 1)        # Container mit Stretch-Faktor 1

        # Erste Zeile: Seitennavigation und Info
        nav_layout = QHBoxLayout()                    # Horizontales Layout
        
        button_width = 150                            # Einheitliche Buttonbreite
        
        # Zurück-Button
        self.prev_button = QPushButton("<<")  # Button für vorherige Seite
        self.prev_button.clicked.connect(self.show_previous_page)  # Verbinde Klick-Event
        self.prev_button.setEnabled(False)            # Initial deaktiviert
        self.prev_button.setFixedWidth(button_width)  # Feste Breite
        nav_layout.addWidget(self.prev_button)        # Zum Layout hinzufügen
        
        # Info-Label für Seiten und Zoom
        info_layout = QHBoxLayout()
        
        # Seitenauswahl Combo Box
        self.page_combo = QComboBox()
        self.page_combo.setFixedWidth(80)
        self.page_combo.setMaxVisibleItems(10)  # Maximal 10 Einträge sichtbar
        self.page_combo.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Scrollbar wenn nötig
        self.page_combo.currentIndexChanged.connect(self.on_page_selected)
        info_layout.addWidget(self.page_combo)
        
        info_layout.addWidget(QLabel("von"))
        self.total_pages_label = QLabel("0")
        info_layout.addWidget(self.total_pages_label)
        
        info_layout.addWidget(QLabel("-"))
        
        self.zoom_label = QLabel("Zoom: 100%")
        info_layout.addWidget(self.zoom_label)
        
        nav_layout.addLayout(info_layout)
        
        # Weiter-Button
        self.next_button = QPushButton(">>")  # Button für nächste Seite
        self.next_button.clicked.connect(self.show_next_page)  # Verbinde Klick-Event
        self.next_button.setEnabled(False)            # Initial deaktiviert
        self.next_button.setFixedWidth(button_width)  # Feste Breite
        nav_layout.addWidget(self.next_button)        # Zum Layout hinzufügen
        
        layout.addLayout(nav_layout)                  # Navigation zum Hauptlayout

        # Zweite Zeile: Zoom-Kontrollen
        zoom_layout = QHBoxLayout()                   # Horizontales Layout
        
        # Zoom Out Button
        self.zoom_out_button = QPushButton("Zoom -")  # Button zum Verkleinern
        self.zoom_out_button.clicked.connect(self.zoom_out)  # Verbinde Klick-Event
        self.zoom_out_button.setFixedWidth(button_width)  # Feste Breite
        zoom_layout.addWidget(self.zoom_out_button)   # Zum Layout hinzufügen
        
        # Fit Button
        self.fit_button = QPushButton("An Fenstergröße anpassen")  # Anpassungs-Button
        self.fit_button.clicked.connect(self.fit_to_window)  # Verbinde Klick-Event
        zoom_layout.addWidget(self.fit_button)        # Zum Layout hinzufügen
        
        # Zoom In Button
        self.zoom_in_button = QPushButton("Zoom +")  # Button zum Vergrößern
        self.zoom_in_button.clicked.connect(self.zoom_in)  # Verbinde Klick-Event
        self.zoom_in_button.setFixedWidth(button_width)  # Feste Breite
        zoom_layout.addWidget(self.zoom_in_button)    # Zum Layout hinzufügen
        
        layout.addLayout(zoom_layout)                 # Zoom-Kontrollen zum Hauptlayout

        self.setLayout(layout)                        # Layout dem Widget zuweisen

    def open_file_dialog(self):
        """
        Öffnet einen Dialog zur PDF-Auswahl und lädt die ausgewählte Datei.
        Passt die Fenstergröße an und initialisiert die Vorschau mit optimaler
        Darstellung.
        """
        main_window = self.window()                   # Hole Hauptfenster-Referenz
        if main_window.get_current_pdf():             # Wenn bereits PDF geöffnet
            main_window.stacked_widget.setCurrentIndex(4)  # Zur Vorschau wechseln
            main_window.setWindowTitle("PDF Tool")    # Titel zurücksetzen

        pdf_path = show_pdf_open_dialog(self)         # Zeige Dateiauswahl-Dialog
        if pdf_path:                                  # Wenn PDF ausgewählt
            try:
                self.pdf_path = pdf_path              # Speichere PDF-Pfad
                self.total_pages = load_pdf(pdf_path)  # Lade PDF und hole Seitenzahl
                self.current_page = 0                 # Starte bei erster Seite
                
                # Aktualisiere Combo Box
                self.page_combo.clear()
                self.page_combo.addItems([str(i+1) for i in range(self.total_pages)])
                self.page_combo.setCurrentIndex(0)
                
                # Aktiviere Navigation wenn mehrere Seiten
                self.prev_button.setEnabled(self.total_pages > 1)  # Vorherige-Seite-Button
                self.next_button.setEnabled(self.total_pages > 1)  # Nächste-Seite-Button
                
                self.update_page_display()            # Aktualisiere Seitenanzeige
                main_window.set_current_pdf(pdf_path)  # Registriere PDF im Hauptfenster
                
                # Wechsle zur Vorschau
                main_window.stacked_widget.setCurrentIndex(4)  # Zeige Vorschau-Widget
                main_window.setWindowTitle("PDF Tool")  # Setze Fenstertitel
                
                # Passe Fenstergröße an
                screen = QApplication.primaryScreen().availableGeometry()  # Hole Bildschirmgröße
                window_height = int(screen.height() * 0.7)  # 70% der Bildschirmhöhe
                window_width = int(screen.width() * 0.4)   # 40% der Bildschirmbreite
                main_window.resize(window_width, window_height)  # Setze neue Größe
                
                self.fit_to_window()                  # Passe an Fenstergröße an
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Fehler beim Laden",
                    f"Die PDF konnte nicht geladen werden:\n{str(e)}"
                )                                     # Zeige Fehlermeldung

    def show_previous_page(self):
        """
        Zeigt die vorherige Seite der PDF an, wenn verfügbar.
        """
        if self.current_page > 0:
            self.current_page -= 1
            self.page_combo.setCurrentIndex(self.current_page)
            self.update_zoom_label()  # Verwende update_zoom_label statt update_page_display
            self.prev_button.setEnabled(self.current_page > 0)
            self.next_button.setEnabled(self.current_page < self.total_pages - 1)
            self.render_current_page()

    def show_next_page(self):
        """
        Zeigt die nächste Seite der PDF an, wenn verfügbar.
        """
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.page_combo.setCurrentIndex(self.current_page)
            self.update_zoom_label()  # Verwende update_zoom_label statt update_page_display
            self.prev_button.setEnabled(self.current_page > 0)
            self.next_button.setEnabled(self.current_page < self.total_pages - 1)
            self.render_current_page()

    def update_page_display(self):
        """
        Aktualisiert die Anzeige der aktuellen Seitennummer und aktiviert/deaktiviert
        die Navigationsbuttons je nach Position.
        """
        self.total_pages_label.setText(str(self.total_pages))
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < self.total_pages - 1)

    def zoom_in(self):
        """
        Vergrößert die Ansicht um 20%.
        """
        self.zoom_factor = self.zoom_factor * 1.2  # Erhöhe Zoom um 20%
        self.update_zoom_label()
        self.render_current_page()

    def zoom_out(self):
        """
        Verkleinert die Ansicht um 20%.
        """
        self.zoom_factor = self.zoom_factor * 0.8  # Reduziere Zoom um 20%
        self.update_zoom_label()
        self.render_current_page()

    def update_zoom_label(self):
        """
        Aktualisiert die Zoom-Anzeige im Zoom-Label.
        Der initiale Zoom (fit_to_window) wird als 100% angezeigt.
        """
        zoom_percent = int((self.zoom_factor / self.base_zoom) * 100)
        self.zoom_label.setText(f"Zoom: {zoom_percent}%")

    def calculate_fit_zoom_factor(self, page_pixmap):
        """
        Berechnet den Zoom-Faktor, der die Seite optimal in den sichtbaren Bereich einpasst.
        """
        # Hole die Größe des sichtbaren Bereichs
        visible_width = self.preview_label.parent().width() - 40  # Scroll-Bereich minus Ränder
        visible_height = self.preview_label.parent().height() - 40

        # Hole die Originalgröße der Seite
        page_width = page_pixmap.width
        page_height = page_pixmap.height

        # Berechne die Skalierungsfaktoren für Breite und Höhe
        width_ratio = visible_width / page_width
        height_ratio = visible_height / page_height

        # Verwende den kleineren Faktor, um die Seite vollständig anzuzeigen
        zoom = min(width_ratio, height_ratio)
        
        # Runde auf 2 Dezimalstellen für bessere Anzeige
        return round(zoom, 2)

    def render_current_page(self):
        """
        Rendert die aktuelle Seite mit dem aktuellen Zoom-Faktor.
        Verwendet einen höheren Qualitätsfaktor für bessere Darstellung.
        """
        if not self.pdf_path:
            return
        
        try:
            # Rendere die Seite mit erhöhter Qualität
            render_zoom = self.zoom_factor * self.render_quality
            pix = render_page(self.pdf_path, self.current_page, render_zoom)
            if not pix:
                return
            
            # Konvertiere zu QPixmap
            img_data = pix.tobytes("ppm")
            qimg = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(qimg)
            
            # Skaliere auf die tatsächliche Anzeigegröße
            if self.render_quality != 1.0:
                display_width = int(pixmap.width() / self.render_quality)
                display_height = int(pixmap.height() / self.render_quality)
                pixmap = pixmap.scaled(
                    display_width, 
                    display_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            
            # Zeige die Pixmap
            self.preview_label.setPixmap(pixmap)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler beim Rendern",
                f"Die Seite konnte nicht gerendert werden:\n{str(e)}"
            )

    def return_to_home(self):
        """
        Wechselt zurück zur Startseite.
        Setzt die PDF-Vorschau zurück und aktualisiert den Fenstertitel.
        """
        main_window = self.window()                   # Hole Hauptfenster-Referenz
        main_window.stacked_widget.setCurrentIndex(0)  # Wechsle zur Startseite
        main_window.setWindowTitle("PDF Tool")        # Setze Titel zurück
        
        # Setze Vorschau zurück
        self.pdf_path = None                          # Lösche PDF-Pfad
        self.current_page = 0                         # Setze Seite zurück
        self.total_pages = 0                          # Setze Seitenzahl zurück
        self.zoom_factor = 1.0                        # Setze Zoom zurück
        self.preview_label.clear()                    # Lösche Vorschau
        self.update_page_display()                    # Aktualisiere Anzeige
        self.page_combo.clear()

    def resizeEvent(self, event):
        """
        Wird bei Änderung der Fenstergröße aufgerufen.
        Passt die PDF-Vorschau automatisch an die neue Größe an.
        """
        super().resizeEvent(event)                    # Rufe Basis-Implementation auf
        
        if self.pdf_path:                            # Wenn PDF geladen
            self.fit_to_window()                      # Passe an neue Größe an

    def fit_to_window(self):
        """
        Passt die Seite optimal an die Fenstergröße an.
        Der berechnete Faktor wird als Basis-Zoom (100%) verwendet.
        """
        if not self.pdf_path:
            return
        
        try:
            # Rendere die Seite zunächst mit Zoom 1.0
            pix = render_page(self.pdf_path, self.current_page, 1.0)
            if not pix:
                return
            
            # Konvertiere zu QPixmap für Größenberechnung
            img_data = pix.tobytes("ppm")
            qimg = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(qimg)
            
            # Berechne verfügbaren Platz (Viewport-Größe)
            available_width = self.scroll_area.viewport().width() - 20
            available_height = self.scroll_area.viewport().height() - 20
            
            # Berechne Skalierungsfaktoren
            width_ratio = available_width / pixmap.width()
            height_ratio = available_height / pixmap.height()
            
            # Wähle kleineren Faktor für proportionale Skalierung
            self.base_zoom = min(width_ratio, height_ratio)  # Setze dies als 100%
            self.zoom_factor = self.base_zoom  # Initialer Zoom ist 100%
            
            self.update_zoom_label()
            self.render_current_page()
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler beim Anpassen",
                f"Die Seite konnte nicht angepasst werden:\n{str(e)}"
            )

    def on_page_selected(self, index):
        """
        Wird aufgerufen, wenn eine neue Seite in der Combo Box ausgewählt wird.
        """
        if index >= 0:  # Verhindere negative Indizes
            self.current_page = index
            self.update_page_display()  # Aktualisiere Buttons und Anzeige
            self.render_current_page()
 