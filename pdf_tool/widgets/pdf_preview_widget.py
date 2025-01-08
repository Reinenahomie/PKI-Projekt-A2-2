from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QMessageBox, QScrollArea, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from ..utils.pdf_functions import load_pdf, render_page, show_pdf_open_dialog
import os

class PDFPreviewWidget(QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.current_page = 0
        self.total_pages = 0
        self.pdf_path = None
        self.zoom_factor = 1.0
        
        # Layout erstellen
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 0, 20, 20)  # Seitliche Ränder auf 20px
        layout.setSpacing(10)  # Reduziere den Abstand zwischen den Elementen

        # Container für die Vorschau
        preview_container = QWidget()
        preview_container.setMinimumSize(400, 600)  # Angepasste Mindestgröße für Hochformat
        preview_container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll-Bereich für die Vorschau
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Vorschaubereich
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        scroll_area.setWidget(self.preview_label)
        preview_layout.addWidget(scroll_area)
        
        layout.addWidget(preview_container, 1)  # 1 gibt dem Container die Priorität beim Dehnen

        # Erste Zeile: Seitennavigation und Info
        nav_layout = QHBoxLayout()
        
        # Navigations-Buttons mit fester Breite
        button_width = 150
        
        self.prev_button = QPushButton("Vorherige Seite")
        self.prev_button.clicked.connect(self.show_previous_page)
        self.prev_button.setEnabled(False)
        self.prev_button.setFixedWidth(button_width)
        nav_layout.addWidget(self.prev_button)
        
        # Info-Label für Seiten und Zoom
        self.info_label = QLabel("Seite 0 von 0 - Zoom: 100%")
        self.info_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.info_label)
        
        self.next_button = QPushButton("Nächste Seite")
        self.next_button.clicked.connect(self.show_next_page)
        self.next_button.setEnabled(False)
        self.next_button.setFixedWidth(button_width)
        nav_layout.addWidget(self.next_button)
        
        layout.addLayout(nav_layout)

        # Zweite Zeile: Zoom-Kontrollen
        zoom_layout = QHBoxLayout()
        
        self.zoom_out_button = QPushButton("Verkleinern")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_out_button.setFixedWidth(button_width)
        zoom_layout.addWidget(self.zoom_out_button)
        
        self.fit_button = QPushButton("An Fenstergröße anpassen")
        self.fit_button.clicked.connect(self.fit_to_window)
        zoom_layout.addWidget(self.fit_button)
        
        self.zoom_in_button = QPushButton("Vergrößern")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setFixedWidth(button_width)
        zoom_layout.addWidget(self.zoom_in_button)
        
        layout.addLayout(zoom_layout)

        self.setLayout(layout)

    def open_file_dialog(self):
        """Öffnet den Dateiauswahl-Dialog und lädt die ausgewählte PDF."""
        # Wenn bereits eine PDF geöffnet ist, wechsle zuerst zur Vorschau
        main_window = self.window()
        if main_window.get_current_pdf():
            main_window.stacked_widget.setCurrentIndex(4)
            main_window.setWindowTitle("PDF Tool")

        # Öffne den Dateiauswahl-Dialog
        pdf_path = show_pdf_open_dialog(self)
        if pdf_path:
            try:
                # Lade die PDF und zeige die erste Seite
                self.pdf_path = pdf_path
                self.total_pages = load_pdf(pdf_path)
                self.current_page = 0
                
                # Aktiviere die Navigation wenn mehr als eine Seite
                self.prev_button.setEnabled(self.total_pages > 1)
                self.next_button.setEnabled(self.total_pages > 1)
                
                # Aktualisiere die Seitenanzeige
                self.update_page_display()
                
                # Registriere die PDF im Hauptfenster
                main_window.set_current_pdf(pdf_path)
                
                # Wechsle zur Vorschau-Ansicht und vergrößere das Fenster
                main_window.stacked_widget.setCurrentIndex(4)
                main_window.setWindowTitle("PDF Tool")
                
                # Hole die Bildschirmgröße
                screen = QApplication.primaryScreen().availableGeometry()
                # Setze die Fenstergröße auf 70% der Bildschirmhöhe und 40% der Breite
                window_height = int(screen.height() * 0.7)
                window_width = int(screen.width() * 0.4)
                # Behalte die aktuelle Position bei und ändere nur die Größe
                main_window.resize(window_width, window_height)
                
                # Setze den Zoom-Faktor zurück und passe an Fenstergröße an
                self.zoom_factor = 1.0
                self.fit_to_window()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Fehler beim Laden",
                    f"Die PDF konnte nicht geladen werden:\n{str(e)}"
                )

    def show_previous_page(self):
        """Zeigt die vorherige Seite an."""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_display()
            self.render_current_page()

    def show_next_page(self):
        """Zeigt die nächste Seite an."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page_display()
            self.render_current_page()

    def update_page_display(self):
        """Aktualisiert die Seitenanzeige."""
        self.info_label.setText(f"Seite {self.current_page + 1} von {self.total_pages} - Zoom: {int(self.zoom_factor * 100)}%")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < self.total_pages - 1)

    def zoom_in(self):
        """Vergrößert die Ansicht."""
        self.zoom_factor += 0.25  # Größere Zoom-Schritte
        self.update_zoom_label()
        self.render_current_page()

    def zoom_out(self):
        """Verkleinert die Ansicht, aber nicht kleiner als 25%."""
        if self.zoom_factor > 0.25:  # Minimaler Zoom-Faktor
            self.zoom_factor -= 0.25  # Größere Zoom-Schritte
            self.update_zoom_label()
            self.render_current_page()

    def update_zoom_label(self):
        """Aktualisiert die Zoom-Anzeige."""
        zoom_percent = int(self.zoom_factor * 100)
        self.info_label.setText(f"Seite {self.current_page + 1} von {self.total_pages} - Zoom: {zoom_percent}%")

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
        """Rendert die aktuelle Seite und zeigt sie an."""
        if self.pdf_path:
            try:
                # Beim ersten Laden oder Fenstergrößenänderung
                if self.zoom_factor == 1.0:
                    # Rendere zunächst mit Zoom 1.0 um die Originalgröße zu erhalten
                    pix = render_page(self.pdf_path, self.current_page, 1.0)
                    # Berechne den optimalen Zoom-Faktor
                    self.zoom_factor = self.calculate_fit_zoom_factor(pix)
                    self.update_zoom_label()
                
                # Rendere die Seite mit dem aktuellen Zoom-Faktor
                pix = render_page(self.pdf_path, self.current_page, self.zoom_factor)
                
                # Konvertiere zu QPixmap und zeige an
                img_data = pix.tobytes("ppm")
                qimg = QImage.fromData(img_data)
                pixmap = QPixmap.fromImage(qimg)
                
                # Setze die Pixmap
                self.preview_label.setPixmap(pixmap)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Fehler beim Rendern",
                    f"Die Seite konnte nicht angezeigt werden:\n{str(e)}"
                )

    def return_to_home(self):
        """Kehrt zur Startseite zurück."""
        self.stacked_widget.setCurrentIndex(0)
        self.window().setWindowTitle("PDF Tool")

    def resizeEvent(self, event):
        """Wird aufgerufen, wenn sich die Fenstergröße ändert."""
        super().resizeEvent(event)
        # Setze den Zoom-Faktor zurück und rendere neu
        if self.pdf_path:
            self.zoom_factor = 1.0
            self.render_current_page() 

    def fit_to_window(self):
        """Passt die Ansicht an die Fenstergröße an."""
        if self.pdf_path:
            # Rendere zunächst mit Zoom 1.0 um die Originalgröße zu erhalten
            pix = render_page(self.pdf_path, self.current_page, 1.0)
            # Berechne den optimalen Zoom-Faktor
            self.zoom_factor = self.calculate_fit_zoom_factor(pix)
            self.update_zoom_label()
            self.render_current_page() 