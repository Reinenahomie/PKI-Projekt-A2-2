from PyQt5.QtWidgets import QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import fitz  # PyMuPDF

class PDFPreview:
    def __init__(self):
        self.layout = QVBoxLayout()
        self.label = QLabel("Öffne ein PDF, um die Vorschau anzuzeigen.")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.current_pdf = None
        self.current_page_index = 0
        self.total_pages = 0
        self.current_pixmap = None

    def open_pdf(self, file_path):
        doc = fitz.open(file_path)
        self.current_pdf = doc
        self.total_pages = len(doc)
        self.current_page_index = 0
        self.render_page()

    def render_page(self):
        if self.current_pdf:
            page = self.current_pdf[self.current_page_index]
            pix = page.get_pixmap()
            image_path = "temp_preview.png"
            pix.save(image_path)
            self.current_pixmap = QPixmap(image_path)
            self.update_preview()

    def update_preview(self):
        if self.current_pixmap:
            scaled_pixmap = self.current_pixmap.scaled(
                self.label.width(), self.label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.label.setPixmap(scaled_pixmap)
