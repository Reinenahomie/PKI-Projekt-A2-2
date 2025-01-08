from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, 
    QScrollArea, QGridLayout, QFrame, QHBoxLayout, QSizePolicy
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
    """Widget zur Extraktion von Bildern aus PDF-Dateien."""

    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        
        # Layout erstellen
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 0, 20, 20)
        layout.setSpacing(20)

        # Scroll-Bereich für die Bildvorschauen
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container für das Grid
        self.preview_container = QWidget()
        self.preview_container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)
        
        # Grid-Layout
        self.grid_layout = QGridLayout(self.preview_container)
        self.grid_layout.setSpacing(15)  # Etwas kleinerer Abstand zwischen den Kacheln
        self.grid_layout.setContentsMargins(15, 15, 15, 15)  # Kleinere Ränder
        self.grid_layout.setAlignment(Qt.AlignTop)
        
        # Initial-Label
        self.initial_label = QLabel("Keine Bilder gefunden.")
        self.initial_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(self.initial_label, 0, 0, 1, 3)  # Über 3 Spalten
        
        # Setze den Container in den ScrollArea
        scroll_area.setWidget(self.preview_container)
        
        # Füge ScrollArea zum Layout hinzu
        layout.addWidget(scroll_area, 1)
        
        self.setLayout(layout)

    def show_preview(self):
        """Zeigt eine Vorschau der Bilder aus der aktuellen PDF."""
        main_window = self.window()
        pdf_path = main_window.get_current_pdf()
        
        if not pdf_path:
            self.initial_label.setText("Keine PDF-Datei geöffnet.")
            return

        try:
            # Bestehende Vorschaubilder entfernen
            while self.grid_layout.count():
                item = self.grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            images = extract_images_from_pdf(pdf_path, preview_only=True)
            
            if images:
                # Bilder in einem Grid mit 3 Spalten anordnen
                for index, image_path in enumerate(images):
                    container = ImageContainer(image_path)
                    row = index // 3  # 3 Bilder pro Zeile
                    col = index % 3
                    self.grid_layout.addWidget(container, row, col, Qt.AlignTop)
            else:
                label = QLabel("Keine Bilder in der PDF gefunden.")
                label.setAlignment(Qt.AlignCenter)
                self.grid_layout.addWidget(label, 0, 0, 1, 3)  # Über 3 Spalten

        except Exception as e:
            error_msg = f"Die Bilder konnten nicht geladen werden:\n{str(e)}"
            QMessageBox.critical(self, "Fehler beim Laden", error_msg)

    def extract_images(self):
        """Extrahiert die Bilder aus der PDF und speichert sie im ausgewählten Verzeichnis."""
        main_window = self.window()
        pdf_path = main_window.get_current_pdf()
        
        if not pdf_path:
            QMessageBox.warning(self, "Fehler", "Bitte öffnen Sie zuerst eine PDF-Datei.")
            return
            
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Speicherverzeichnis auswählen")
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # Verwende PyQt Dialog
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            save_dir = file_dialog.selectedFiles()[0]
            try:
                extracted_images = extract_images_from_pdf(pdf_path, output_dir=save_dir)
                if extracted_images:
                    QMessageBox.information(self, "Erfolg", f"{len(extracted_images)} Bilder wurden erfolgreich extrahiert.")
                else:
                    QMessageBox.information(self, "Keine Bilder", "Es wurden keine Bilder in der PDF gefunden.")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Extrahieren der Bilder: {str(e)}")

    def extract_images_to_zip(self):
        """Extrahiert die Bilder aus der PDF und speichert sie in einer ZIP-Datei."""
        main_window = self.window()
        pdf_path = main_window.get_current_pdf()
        
        if not pdf_path:
            QMessageBox.warning(self, "Fehler", "Bitte öffnen Sie zuerst eine PDF-Datei.")
            return
            
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("ZIP-Datei speichern")
        file_dialog.setNameFilter("ZIP-Dateien (*.zip)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("zip")
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # Verwende PyQt Dialog
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            zip_path = file_dialog.selectedFiles()[0]
            try:
                # Temporäres Verzeichnis für die Bilder
                import tempfile
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Bilder extrahieren
                    extracted_images = extract_images_from_pdf(pdf_path, output_dir=temp_dir)
                    if extracted_images:
                        # ZIP erstellen
                        from ..utils.pdf_functions import create_zip_from_files
                        create_zip_from_files(extracted_images, zip_path)
                        QMessageBox.information(self, "Erfolg", f"{len(extracted_images)} Bilder wurden erfolgreich als ZIP-Datei gespeichert.")
                    else:
                        QMessageBox.information(self, "Keine Bilder", "Es wurden keine Bilder in der PDF gefunden.")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Erstellen der ZIP-Datei: {str(e)}")
