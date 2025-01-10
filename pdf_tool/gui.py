#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - Hauptfenster und GUI-Komponenten

Diese Datei implementiert das Hauptfenster der Anwendung und verwaltet die
verschiedenen GUI-Komponenten und deren Interaktionen.

Fensteraufbau:
- Linke Seite: Menüleiste mit Funktionskacheln
  - Datei öffnen/schließen
  - PDF-Operationen (Trennen, Zusammenführen, etc.)
  - Kontextabhängige Aktionsbuttons
- Rechte Seite: Hauptarbeitsbereich
  - Wechselnde Widgets je nach ausgewählter Funktion
  - PDF-Vorschau und Bearbeitungsfunktionen

Funktionsweise:
1. Initialisierung des Hauptfensters
   - Erstellen der GUI-Komponenten
   - Einrichten der Layouts
   - Konfiguration der Buttons

2. Verwaltung der Widgets
   - Dynamisches Laden der Funktionswidgets
   - Kontextabhängige Anzeige von Aktionsbuttons
   - Statusverwaltung (aktive PDF, etc.)

3. Ereignisbehandlung
   - Button-Klicks und Benutzerinteraktionen
   - Dateioperationen
   - Statusaktualisierungen

Technische Details:
- Basiert auf PyQt5
- Verwendet QStackedWidget für Seitenwechsel
- Responsive Layouts
- Thread-sichere Implementierung

Autor: Team A2-2
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout, QPushButton,
    QStackedWidget, QHBoxLayout, QLabel, QMessageBox, QApplication, QFrame, QFileDialog, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os

from pdf_tool.widgets import (
    HomeWidget, PDFPreviewWidget, PDFSplitWidget, PDFMergeWidget,
    PDFToWordWidget, PDFImageExtractorWidget, EInvoiceReaderWidget
)

class MainWindow(QMainWindow):
    """
    Hauptfenster der Anwendung.
    
    Diese Klasse implementiert das zentrale Fenster des PDF Tools und
    verwaltet alle GUI-Komponenten und deren Interaktionen.
    
    Attribute:
        current_pdf_path (str): Pfad zur aktuell geöffneten PDF-Datei
        stacked_widget (QStackedWidget): Container für die verschiedenen Ansichten
        menu_widget (QWidget): Container für die Menüleiste
        function_buttons (dict): Sammlung aller Funktionsbuttons
        action_buttons_container (QWidget): Container für kontextabhängige Buttons
    
    Funktionen:
        - PDF-Datei öffnen und schließen
        - Navigation zwischen verschiedenen Ansichten
        - Verwaltung der Funktionsbuttons
        - Anzeige kontextabhängiger Aktionen
        - Styling und Layout-Management
    """
    def __init__(self, parent=None):
        """Initialisiert das Hauptfenster und setzt alle UI-Komponenten auf."""
        super().__init__(parent)
        # Setze Fenstertitel und Grundabmessungen
        self.setWindowTitle("PDF Tool")
        
        # Hole die Bildschirmgröße
        screen = QApplication.primaryScreen().availableGeometry()
        # Setze die Fenstergröße auf 70% der Bildschirmhöhe und 40% der Breite
        window_height = int(screen.height() * 0.7)
        window_width = int(screen.width() * 0.4)
        # Zentriere das Fenster
        x = (screen.width() - window_width) // 2
        y = (screen.height() - window_height) // 2
        self.setGeometry(x, y, window_width, window_height)
        
        # Aktuelle PDF-Datei
        self.current_pdf_path = None
        
        # Erstelle das zentrale Widget und Hauptlayout
        central_widget = QWidget()
        main_layout = QHBoxLayout()  # Horizontales Layout für Buttons links, Inhalt rechts
        main_layout.setContentsMargins(10, 10, 10, 10)  # Reduziere die Ränder
        main_layout.setSpacing(10)  # Reduziere den Abstand zwischen Menü und Inhalt
        
        # Erstelle den Menü-Bereich für die Funktionskacheln
        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout(self.menu_widget)  # Vertikales Layout für Buttons
        menu_layout.setSpacing(10)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        
        # Erstelle die Funktionskacheln (Buttons)
        open_file_button = self.create_tile_button("Datei öffnen")
        split_pdf_button = self.create_tile_button("PDF trennen")
        pdf_to_word_button = self.create_tile_button("PDF to Word")
        merge_pdf_button = self.create_tile_button("PDF zusammenfügen")
        extract_images_button = self.create_tile_button("Bilder extrahieren")
        e_invoice_button = self.create_tile_button("E-Rechnung anzeigen")
        close_file_button = self.create_tile_button("Datei schließen")
        
        # Initial alle Funktions-Buttons deaktivieren
        split_pdf_button.setEnabled(False)
        pdf_to_word_button.setEnabled(False)
        merge_pdf_button.setEnabled(False)
        extract_images_button.setEnabled(False)
        e_invoice_button.setEnabled(False)
        close_file_button.setEnabled(False)
        
        # Speichere die Buttons als Instanzvariablen für späteren Zugriff
        self.function_buttons = {
            'split': split_pdf_button,
            'word': pdf_to_word_button,
            'merge': merge_pdf_button,
            'images': extract_images_button,
            'invoice': e_invoice_button,
            'close': close_file_button
        }
        
        # Füge die Buttons vertikal hinzu
        menu_layout.addWidget(open_file_button)
        menu_layout.addWidget(split_pdf_button)
        menu_layout.addWidget(pdf_to_word_button)
        menu_layout.addWidget(merge_pdf_button)
        menu_layout.addWidget(extract_images_button)
        menu_layout.addWidget(e_invoice_button)
        menu_layout.addWidget(close_file_button)
        
        # Trennlinie für Aktions-Buttons (initial versteckt)
        self.action_separator = QFrame()
        self.action_separator.setFrameShape(QFrame.HLine)
        self.action_separator.setFrameShadow(QFrame.Sunken)
        self.action_separator.hide()
        menu_layout.addWidget(self.action_separator)
        
        # Container für die Aktions-Buttons (initial versteckt)
        self.action_buttons_container = QWidget()
        self.action_buttons_layout = QVBoxLayout(self.action_buttons_container)
        self.action_buttons_layout.setContentsMargins(0, 10, 0, 0)
        self.action_buttons_layout.setSpacing(10)
        self.action_buttons_container.hide()
        menu_layout.addWidget(self.action_buttons_container)
        
        menu_layout.addStretch()  # Fügt flexiblen Platz am Ende hinzu
        
        # Füge das Menü-Layout zum Hauptlayout hinzu
        main_layout.addWidget(self.menu_widget)
        
        # Erstelle den Stapel-Widget-Container für die verschiedenen Ansichten
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Initialisiere alle Funktions-Widgets
        self.page_home = HomeWidget()
        self.page_pdf_to_word = PDFToWordWidget(self.stacked_widget)
        self.page_extract_images = PDFImageExtractorWidget(self.stacked_widget)
        self.page_merge_pdf = PDFMergeWidget(self.stacked_widget)
        self.page_pdf_preview = PDFPreviewWidget(self.stacked_widget)
        self.page_split_pdf = PDFSplitWidget(self.stacked_widget)
        self.page_zugferd = EInvoiceReaderWidget(self.stacked_widget)
        
        # Füge alle Widgets zum Stapel hinzu
        self.stacked_widget.addWidget(self.page_home)
        self.stacked_widget.addWidget(self.page_pdf_to_word)
        self.stacked_widget.addWidget(self.page_extract_images)
        self.stacked_widget.addWidget(self.page_merge_pdf)
        self.stacked_widget.addWidget(self.page_pdf_preview)
        self.stacked_widget.addWidget(self.page_split_pdf)
        self.stacked_widget.addWidget(self.page_zugferd)
        
        # Verbinde die Buttons mit ihren jeweiligen Funktionen
        open_file_button.clicked.connect(self.page_pdf_preview.open_file_dialog)
        split_pdf_button.clicked.connect(self.start_pdf_split)
        pdf_to_word_button.clicked.connect(self.start_pdf_to_word)
        merge_pdf_button.clicked.connect(self.switch_to_pdf_merger)
        extract_images_button.clicked.connect(self.switch_to_image_extractor)
        e_invoice_button.clicked.connect(lambda: self.switch_page(6, "PDF Tool - E-Rechnung anzeigen"))
        close_file_button.clicked.connect(self.close_current_pdf)
        
        # Setze das Hauptlayout für das zentrale Widget
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Wende das definierte Stylesheet auf das Fenster an
        self.apply_stylesheet()

        self._create_menu()

    def apply_stylesheet(self):
        """
        Wendet das CSS-ähnliche Styling auf die Anwendung an.
        Definiert das Aussehen verschiedener UI-Elemente.
        """
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;  /* Hintergrundfarbe */
                font-family: 'Segoe UI';    /* Schriftart */
                font-size: 14px;            /* Schriftgröße */
            }
            QPushButton {
                background-color: #ffffff;   /* Button-Hintergrund */
                border: 1px solid #cccccc;   /* Button-Rahmen */
                border-radius: 3px;          /* Abgerundete Ecken */
                padding: 10px;               /* Innenabstand */
                font-size: 15px;             /* Button-Schriftgröße */
                text-align: center;          /* Text-Ausrichtung */
                font-weight: 500;            /* Schriftstärke */
            }
            QPushButton:hover {
                background-color: #f0f0f0;   /* Hover-Effekt */
                border-color: #999999;       /* Dunklerer Rahmen beim Hover */
            }
            QLabel {
                font-size: 14px;             /* Label-Schriftgröße */
            }
            QScrollArea {
                border: none;                /* Keine Rahmen für Scroll-Bereiche */
            }
        """)

    def create_tile_button(self, text):
        """
        Erstellt einen formatierten Button für das Hauptmenü.
        
        Args:
            text (str): Der anzuzeigende Text auf dem Button
            
        Returns:
            QPushButton: Ein formatierter Button mit fester Größe
        """
        button = QPushButton(text)
        button.setFixedWidth(250)  # Feste Breite für einheitliches Aussehen
        button.setMinimumHeight(40)  # Minimale Höhe
        return button

    def enable_function_buttons(self):
        """Aktiviert alle Funktions-Buttons nachdem eine Datei geladen wurde."""
        for button in self.function_buttons.values():
            button.setEnabled(True)

    def switch_page(self, index, title):
        """
        Wechselt zu einer anderen Ansicht und aktualisiert den Fenstertitel.
        
        Args:
            index (int): Der Index der anzuzeigenden Seite im Stapel-Widget
            title (str): Der neue Fenstertitel
        """
        # Setze zuerst den Index und Titel
        self.stacked_widget.setCurrentIndex(index)
        self.setWindowTitle(title)
        
        # Verstecke Aktions-Buttons, wenn nicht auf Bilder extrahieren oder PDF zusammenfügen
        if index not in [2, 3]:  # 2 = Bilder extrahieren, 3 = PDF zusammenfügen
            self.hide_action_buttons()
        
        # Zeige Info-Text für die verschiedenen Funktionen
        if index == 1:  # PDF to Word
            self.show_action_buttons([], "Konvertieren Sie die PDF-Datei in das DOCX-Format. Die Konvertierung behält das Layout und die Formatierung bei. Tabellen und Bilder werden bestmöglich übernommen.")
        elif index == 5:  # PDF trennen
            self.show_action_buttons([], "Trennen Sie die PDF-Datei in einzelne Seiten auf. Jede Seite wird als separate PDF-Datei gespeichert. Die getrennten Seiten werden in einem Ordner mit Zeitstempel gespeichert und sind nach Seitenzahlen benannt. Ideal für das Aufteilen großer Dokumente.")
        elif index == 6:  # E-Rechnung anzeigen
            self.show_action_buttons([], "Zeigt die ZUGFeRD-Daten der geöffneten PDF-Datei an. Unterstützt werden die Versionen 1.0 und 2.0 des ZUGFeRD-Standards. Die extrahierten Daten werden übersichtlich in einer Baumstruktur dargestellt. Sie können die Rechnungsdaten einsehen und die strukturierten Informationen wie Beträge, Steuern und Zahlungsbedingungen prüfen.")

    def set_current_pdf(self, pdf_path):
        """Setzt den Pfad zur aktuell geöffneten PDF-Datei."""
        self.current_pdf_path = pdf_path
        # Aktiviere die Funktions-Buttons
        self.enable_function_buttons()
        
    def get_current_pdf(self):
        """Gibt den Pfad zur aktuell geöffneten PDF-Datei zurück."""
        return self.current_pdf_path

    def switch_to_image_extractor(self):
        """Wechselt zum Bild-Extraktor und aktualisiert die Vorschau."""
        # Aktions-Buttons für Bildextraktor anzeigen
        self.show_action_buttons(
            [
                ("Bilder speichern", self.page_extract_images.extract_images),
                ("Bilder als ZIP speichern", self.page_extract_images.extract_images_to_zip)
            ],
            "Extrahieren Sie Bilder aus der geöffneten PDF-Datei. Die Bilder werden in ihrer ursprünglichen Qualität und Größe extrahiert. Unterstützt werden gängige Bildformate wie JPEG, PNG und TIFF. Die Bilder können einzeln oder als ZIP-Archiv gespeichert werden. Die Bilder werden automatisch nach Seitenzahl sortiert und mit aussagekräftigen Namen versehen. Ideal für die Weiterverarbeitung von Bildern aus Dokumenten."
        )
        
        # Wechsle zur Ansicht und zeige Vorschau
        self.switch_page(2, "PDF Tool - Bilder extrahieren")
        self.page_extract_images.show_preview()

    def switch_to_pdf_merger(self):
        """Wechselt zum PDF-Zusammenfügen-Widget."""
        # Aktions-Buttons für PDF-Zusammenfügen anzeigen
        self.show_action_buttons(
            [
                ("Weitere PDF hinzufügen", self.page_merge_pdf.add_pdf),
                ("Ausgewählte PDF entfernen", self.page_merge_pdf.remove_selected_pdf),
                ("Gesamtes PDF speichern", self.page_merge_pdf.merge_pdfs)
            ],
            "Fügen Sie mehrere PDF-Dateien zu einem Dokument zusammen. Die Reihenfolge kann durch die Auswahl der Dateien bestimmt werden. Bereits hinzugefügte PDFs können durch Anklicken ausgewählt und wieder entfernt werden. Die Seitenreihenfolge bleibt erhalten und die Qualität der Original-PDFs wird nicht beeinträchtigt. Perfekt für das Zusammenstellen von Dokumenten aus verschiedenen Quellen."
        )
        
        # Wechsle zur Ansicht
        self.switch_page(3, "PDF Tool - PDF zusammenfügen")

    def show_action_buttons(self, button_configs, info_text=None):
        """
        Zeigt die Aktions-Buttons für das aktuelle Widget an.
        
        Args:
            button_configs: Liste von Tupeln (Button-Text, Callback-Funktion)
            info_text: Optionaler Erklärungstext
        """
        # Lösche alte Buttons
        for i in reversed(range(self.action_buttons_layout.count())): 
            self.action_buttons_layout.itemAt(i).widget().setParent(None)
        
        # Füge neue Buttons hinzu
        for text, callback in button_configs:
            button = self.create_tile_button(text)
            button.clicked.connect(callback)
            self.action_buttons_layout.addWidget(button)
        
        # Zeige Trennlinie und Container
        self.action_separator.show()
        self.action_buttons_container.show()
        
        # Füge Info-Text hinzu, wenn vorhanden
        if info_text:
            # Zweite Trennlinie vor dem Info-Text
            info_separator = QFrame()
            info_separator.setFrameShape(QFrame.HLine)
            info_separator.setFrameShadow(QFrame.Sunken)
            info_separator.setFixedWidth(250)
            self.action_buttons_layout.addWidget(info_separator)
            
            # Info-Text
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            info_label.setFixedWidth(250)
            info_label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    background-color: transparent;
                }
            """)
            self.action_buttons_layout.addWidget(info_label)

    def hide_action_buttons(self):
        """Versteckt die Aktions-Buttons."""
        self.action_separator.hide()
        self.action_buttons_container.hide()

    def close_current_pdf(self):
        """Schließt die aktuell geöffnete PDF-Datei."""
        self.current_pdf_path = None
        # Deaktiviere alle Funktions-Buttons
        for button in self.function_buttons.values():
            button.setEnabled(False)
        # Wechsle zur Startseite
        self.switch_page(0, "PDF Tool")

    def start_pdf_split(self):
        """Startet den PDF-Trennvorgang."""
        self.show_action_buttons([], "Trennen Sie die PDF-Datei in einzelne Seiten auf.")
        self.switch_page(5, "PDF Tool - PDF trennen")
        # Starte die Trennung direkt
        self.page_split_pdf.split_pdf()

    def start_pdf_to_word(self):
        """Startet die PDF zu Word Konvertierung."""
        self.show_action_buttons([], "Konvertieren Sie die PDF-Datei in ein Word-Dokument.")
        self.switch_page(1, "PDF Tool - PDF to Word")
        # Starte die Konvertierung direkt
        self.page_pdf_to_word.convert_to_word()

    def show_pdf_merge(self):
        """Zeigt das PDF Merge Widget an."""
        if not hasattr(self, 'pdf_merge_widget'):
            self.pdf_merge_widget = PDFMergeWidget(self.stacked_widget)
            self.stacked_widget.addWidget(self.pdf_merge_widget)
        self.stacked_widget.setCurrentWidget(self.pdf_merge_widget)
        self.setWindowTitle("PDF Tool - PDF zusammenfügen")

    def _create_menu(self):
        """Erstellt die Menüleiste mit allen Menüpunkten."""
        menubar = self.menuBar()                      # Erstelle Menüleiste
        
        # Datei-Menü
        file_menu = menubar.addMenu('&Datei')        # Erstelle Datei-Menü
        
        # Öffnen-Aktion
        open_action = QAction('Öffnen...', self)     # Erstelle Öffnen-Aktion
        open_action.setShortcut('Ctrl+O')            # Setze Tastaturkürzel
        open_action.setStatusTip('PDF-Datei öffnen') # Setze Statustipp
        open_action.triggered.connect(self.page_pdf_preview.open_file_dialog)  # Verbinde mit der gleichen Funktion wie Button
        file_menu.addAction(open_action)             # Füge Aktion zum Menü hinzu
        
        # Trenner
        file_menu.addSeparator()                     # Füge Trennlinie ein
        
        # Beenden-Aktion
        exit_action = QAction('Beenden', self)       # Erstelle Beenden-Aktion
        exit_action.setShortcut('Ctrl+Q')            # Setze Tastaturkürzel
        exit_action.setStatusTip('Anwendung beenden')  # Setze Statustipp
        exit_action.triggered.connect(self.close)     # Verbinde mit Schließen-Funktion
        file_menu.addAction(exit_action)             # Füge Aktion zum Menü hinzu

    def _create_status_bar(self):
        """Erstellt die Statusleiste."""
        self.statusBar().showMessage("Bereit")      # Zeige Standardnachricht