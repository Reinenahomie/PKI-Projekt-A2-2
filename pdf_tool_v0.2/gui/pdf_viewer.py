from PyQt5.QtWidgets import QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from utils.utils import Utils
from utils.config import Config

import fitz

class PDFViewer:
    """Verwaltet die Anzeige und das Rendern von PDF-Seiten."""

    def __init__(self, pdf_handler):
        """
        Initialisiert die PDF-Anzeige.

        Args:
            pdf_handler (PDFHandler): Die zentrale PDF-Logik.
        """
        print(f"PDFViewer.__init__() aufgerufen mit pdf_handler={pdf_handler}")
        self.pdf_handler = pdf_handler
        self.layout = QVBoxLayout()

        # Anzeige-Label für die PDF-Vorschau
        self.label = QLabel("Öffne ein PDF, um die Vorschau anzuzeigen.")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

    def render_page(self):
        """Rendert die aktuelle Seite des PDFs und zeigt sie an."""
        if not self.pdf_handler.current_pdf:
            self.label.setText("Öffne ein PDF, um die Vorschau anzuzeigen.")
            return

        try:
            # Hole die aktuelle Seite
            page = self.pdf_handler.current_pdf[self.pdf_handler.current_page_index]

            # Dynamische Skalierung basierend auf Widget-Größe
            widget_width = self.label.width()
            widget_height = self.label.height()
            scale = Utils.calculate_scaling(widget_width, widget_height, page.rect.width, page.rect.height)
            dpi_scale_factor = Config.DEFAULT_DPI / 72  # Umwandlung von Standard-DPI

            # Korrekte Transformation mit fitz.Matrix
            matrix = fitz.Matrix(scale * dpi_scale_factor, scale * dpi_scale_factor)

            # Rendern der Seite
            pixmap = page.get_pixmap(matrix=matrix)
            image_path = Utils.get_unique_filename(Config.DEFAULT_OUTPUT_DIR, "temp_preview", ".png")
            Utils.ensure_directory_exists(Config.DEFAULT_OUTPUT_DIR)
            pixmap.save(image_path)

            # Pixmap in QLabel anzeigen
            self.update_preview(QPixmap(image_path))

        except Exception as e:
            self.label.setText(f"Fehler beim Rendern: {e}")
            print(f"Fehler beim Rendern: {e}")

    def update_preview(self, pixmap):
        """
        Aktualisiert die Anzeige basierend auf der aktuellen Pixmap.

        Args:
            pixmap (QPixmap): Die Pixmap, die im QLabel angezeigt werden soll.
        """
        if pixmap:
            scaled_pixmap = pixmap.scaled(
                self.label.width(),
                self.label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.label.setPixmap(scaled_pixmap)

    def resize_event(self):
        """Wird aufgerufen, wenn das Fenster in der Größe geändert wird."""
        self.render_page()
