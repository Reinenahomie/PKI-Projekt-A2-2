from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from ..utils.pdf_functions import split_pdf_into_pages, render_page, show_directory_dialog
import os

class PDFSplitWidget(QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        
        # Layout erstellen
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 0, 20, 20)  # Seitliche Ränder auf 20px
        layout.setSpacing(10)

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
        preview_layout.setSpacing(0)  # Kein Abstand zwischen Elementen

        # Scroll-Bereich für die Vorschau
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setContentsMargins(0, 0, 0, 0)  # Keine Ränder
        
        # Vorschaubereich
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        scroll_area.setWidget(self.preview_label)
        preview_layout.addWidget(scroll_area)
        
        layout.addWidget(preview_container, 1)  # 1 gibt dem Container die Priorität beim Dehnen

        # Erste Zeile: Status-Informationen
        nav_layout = QHBoxLayout()
        
        # Platzhalter links mit fester Breite (für konsistentes Layout)
        left_spacer = QWidget()
        left_spacer.setFixedWidth(150)
        nav_layout.addWidget(left_spacer)
        
        # Status-Label in der Mitte
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("QLabel { color: #666666; }")
        nav_layout.addWidget(self.status_label)
        
        # Platzhalter rechts mit fester Breite (für konsistentes Layout)
        right_spacer = QWidget()
        right_spacer.setFixedWidth(150)
        nav_layout.addWidget(right_spacer)
        
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def showEvent(self, event):
        """Wird aufgerufen, wenn das Widget angezeigt wird."""
        super().showEvent(event)
        # Hole die aktuelle PDF vom Hauptfenster
        main_window = self.window()
        pdf_path = main_window.get_current_pdf()
        
        if pdf_path:
            self.show_preview(pdf_path)
            self.status_label.clear()  # Status zurücksetzen
        else:
            self.preview_label.clear()
            self.preview_label.setText("Keine PDF-Datei geöffnet")

    def show_preview(self, pdf_path):
        """Zeigt eine Vorschau der ersten Seite der PDF."""
        try:
            # Rendere die erste Seite
            pix = render_page(pdf_path, 0, 1.0)
            
            # Berechne den optimalen Zoom-Faktor
            visible_width = self.preview_label.parent().width() - 40
            visible_height = self.preview_label.parent().height() - 40
            width_ratio = visible_width / pix.width
            height_ratio = visible_height / pix.height
            zoom = min(width_ratio, height_ratio)
            
            # Rendere mit optimalem Zoom
            pix = render_page(pdf_path, 0, zoom)
            
            # Konvertiere zu QPixmap und zeige an
            img_data = pix.tobytes("ppm")
            qimg = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(qimg)
            self.preview_label.setPixmap(pixmap)
            
        except Exception as e:
            self.preview_label.clear()
            self.preview_label.setText(f"Fehler beim Laden der Vorschau:\n{str(e)}")

    def split_pdf(self):
        """Trennt die aktuelle PDF in Einzelseiten."""
        # Hole die aktuelle PDF-Datei vom Hauptfenster
        main_window = self.window()
        pdf_path = main_window.get_current_pdf()
        
        if not pdf_path:
            QMessageBox.warning(
                self,
                "Keine PDF geöffnet",
                "Bitte öffnen Sie zuerst eine PDF-Datei."
            )
            return

        # Bestimme den Ausgabeordner mit dem einheitlichen Dialog
        output_dir = show_directory_dialog(
            self,
            "Ausgabeordner für getrennte Seiten",
            use_export_dir=True  # Verwende den Export-Ordner als Standard
        )
        
        if output_dir:
            try:
                self.status_label.setText("PDF wird getrennt...")
                self.status_label.setStyleSheet("QLabel { color: #FFA500; }")  # Orange
                
                # Trenne die PDF in einzelne Seiten
                split_pdf_into_pages(pdf_path, output_dir)
                
                # Status zurücksetzen
                self.status_label.clear()
                self.status_label.setStyleSheet("QLabel { color: #666666; }")
                
                QMessageBox.information(
                    self,
                    "Erfolg",
                    "Die PDF wurde erfolgreich in Einzelseiten getrennt."
                )
                
            except Exception as e:
                # Status zurücksetzen
                self.status_label.clear()
                self.status_label.setStyleSheet("QLabel { color: #666666; }")
                
                QMessageBox.critical(
                    self,
                    "Fehler bei der Trennung",
                    f"Die PDF konnte nicht getrennt werden:\n{str(e)}"
                ) 