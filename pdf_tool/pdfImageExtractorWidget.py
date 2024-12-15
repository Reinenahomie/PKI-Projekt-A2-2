from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QScrollArea
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from .pdf_functions import extract_images_from_pdf  # Annahme: Funktion wird in `pdf_functions` implementiert


class PDFImageExtractorWidget(QWidget):
    """Widget für die Bildextraktion aus PDF-Dateien."""

    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.pdf_path = None
        self.image_paths = []

        # Hauptlayout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Titel
        title_label = QLabel("Bilder aus PDF extrahieren")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Bereich für Bildvorschau
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_preview = QLabel("Bitte eine PDF-Datei hochladen.")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_preview)
        main_layout.addWidget(self.scroll_area)

        # Buttons
        upload_button = QPushButton("PDF hochladen")
        upload_button.clicked.connect(self.open_file_dialog)
        main_layout.addWidget(upload_button)

        extract_button = QPushButton("Bilder extrahieren und speichern")
        extract_button.clicked.connect(self.extract_images)
        extract_button.setEnabled(False)  # Aktiviert, sobald eine PDF geladen ist
        self.extract_button = extract_button
        main_layout.addWidget(extract_button)

        back_button = QPushButton("Zurück")
        back_button.clicked.connect(self.return_to_home)
        main_layout.addWidget(back_button)

        self.setLayout(main_layout)

    def return_to_home(self):
        """Zurück zur Startseite."""
        self.stacked_widget.setCurrentIndex(0)

    def open_file_dialog(self):
        """Öffnet den Dialog zum Auswählen einer PDF-Datei."""
        file_path, _ = QFileDialog.getOpenFileName(self, "PDF auswählen", "", "PDF Dateien (*.pdf)")
        if file_path:
            self.load_pdf(file_path)

    def load_pdf(self, pdf_path):
        """Lädt die PDF und zeigt eine Bildvorschau an."""
        self.pdf_path = pdf_path
        self.image_paths = []  # Zurücksetzen, falls vorher geladen

        try:
            # Bildvorschau anzeigen (nur erstes Bild der PDF, falls vorhanden)
            images = extract_images_from_pdf(pdf_path, preview_only=True)
            if images:
                pixmap = QPixmap(images[0])
                self.image_preview.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.image_preview.setAlignment(Qt.AlignCenter)
                self.extract_button.setEnabled(True)
            else:
                self.image_preview.setText("Keine Bilder in der PDF gefunden.")
                self.extract_button.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"PDF konnte nicht geladen werden: {e}")

    def extract_images(self):
        """Extrahiert Bilder und speichert sie in einem Zielverzeichnis."""
        if not self.pdf_path:
            QMessageBox.warning(self, "Fehler", "Keine PDF ausgewählt.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Zielverzeichnis auswählen")
        if not output_dir:
            return

        try:
            # Bilder extrahieren und speichern
            extracted_images = extract_images_from_pdf(self.pdf_path, output_dir=output_dir)
            if extracted_images:
                QMessageBox.information(
                    self, "Erfolg", f"{len(extracted_images)} Bilder wurden gespeichert:\n{output_dir}"
                )
            else:
                QMessageBox.information(self, "Erfolg", "Keine Bilder in der PDF gefunden.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Bilder konnten nicht extrahiert werden: {e}")
