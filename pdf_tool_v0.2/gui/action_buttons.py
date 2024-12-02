from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from core.pdf_text_extractor import PDFTextExtractor
from core.pdf_image_extractor import PDFImageExtractor
from core.pdf_rotator import PDFRotator
from core.pdf_merger import PDFMerger
from utils.config import Config


class ActionButtons:
    """Verwaltet die Aktions-Buttons auf der rechten Seite."""

    def __init__(self, pdf_handler, pdf_viewer, navigation_bar):
        """
        Initialisiert die Aktions-Buttons.

        Args:
            pdf_handler (PDFHandler): Die zentrale PDF-Logik.
            pdf_viewer (PDFViewer): Referenz auf die PDF-Anzeige.
            navigation_bar (NavigationBar): Referenz auf die Navigationsleiste.
        """
        self.pdf_handler = pdf_handler
        self.pdf_viewer = pdf_viewer
        self.navigation_bar = navigation_bar
        self.layout = QVBoxLayout()

        # Buttons erstellen
        self.create_buttons()

        # Platzhalter hinzufügen, um Buttons nach oben zu drücken
        self.layout.addStretch()

    def create_buttons(self):
        """Erstellt die Buttons und verbindet sie mit den Aktionen."""
        # PDF öffnen
        self.open_button = QPushButton("PDF öffnen")
        self.open_button.clicked.connect(self.open_pdf)
        self.layout.addWidget(self.open_button)

        # Text extrahieren
        self.extract_text_button = QPushButton("Text extrahieren")
        self.extract_text_button.clicked.connect(self.extract_text)
        self.extract_text_button.setEnabled(False)
        self.layout.addWidget(self.extract_text_button)

        # Bilder extrahieren
        self.extract_images_button = QPushButton("Bilder extrahieren")
        self.extract_images_button.clicked.connect(self.extract_images)
        self.extract_images_button.setEnabled(False)
        self.layout.addWidget(self.extract_images_button)

        # PDF drehen
        self.rotate_pdf_button = QPushButton("PDF drehen")
        self.rotate_pdf_button.clicked.connect(self.rotate_pdf)
        self.rotate_pdf_button.setEnabled(False)
        self.layout.addWidget(self.rotate_pdf_button)

        # PDF zusammenführen
        self.add_pages_button = QPushButton("Seiten hinzufügen")
        self.add_pages_button.clicked.connect(self.add_pages)
        self.add_pages_button.setEnabled(False)
        self.layout.addWidget(self.add_pages_button)

    def enable_buttons(self):
        """Aktiviert die Buttons, wenn ein PDF geladen ist."""
        self.extract_text_button.setEnabled(True)
        self.extract_images_button.setEnabled(True)
        self.rotate_pdf_button.setEnabled(True)
        self.add_pages_button.setEnabled(True)

    def open_pdf(self):
        """Öffnet ein PDF und zeigt es in der PDF-Anzeige an."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(None, "PDF Datei auswählen", "", "PDF Dateien (*.pdf)", options=options)
        if file_path:
            self.pdf_handler.open_pdf(file_path)
            self.pdf_viewer.render_page()
            self.navigation_bar.update_buttons()
            self.enable_buttons()

    def extract_text(self):
        """Extrahiert den Text aus der aktuellen PDF und speichert ihn."""
        if not self.pdf_handler.current_pdf:
            QMessageBox.warning(None, "Keine Datei geöffnet", "Bitte zuerst ein PDF öffnen.")
            return

        output_file, _ = QFileDialog.getSaveFileName(None, "Text speichern", "", "Textdateien (*.txt)")
        if not output_file:
            return

        try:
            PDFTextExtractor.extract_text(self.pdf_handler.file_path, output_file)
            QMessageBox.information(None, "Erfolg", f"Text erfolgreich gespeichert in: {output_file}")
        except Exception as e:
            QMessageBox.critical(None, "Fehler", f"Text konnte nicht extrahiert werden:\n{e}")

    def extract_images(self):
        """Extrahiert Bilder aus der aktuellen PDF und speichert sie."""
        if not self.pdf_handler.current_pdf:
            QMessageBox.warning(None, "Keine Datei geöffnet", "Bitte zuerst ein PDF öffnen.")
            return

        output_dir = QFileDialog.getExistingDirectory(None, "Zielverzeichnis auswählen", Config.DEFAULT_OUTPUT_DIR)
        if not output_dir:
            return

        try:
            PDFImageExtractor.extract_images(self.pdf_handler.file_path, output_dir)
            QMessageBox.information(None, "Erfolg", f"Bilder erfolgreich gespeichert in: {output_dir}")
        except Exception as e:
            QMessageBox.critical(None, "Fehler", f"Bilder konnten nicht extrahiert werden:\n{e}")

    def rotate_pdf(self):
        """Dreht eine spezifische Seite der aktuellen PDF."""
        if not self.pdf_handler.current_pdf:
            QMessageBox.warning(None, "Keine Datei geöffnet", "Bitte zuerst ein PDF öffnen.")
            return

        text, ok = QFileDialog.getText(None, "Seite drehen", "Seite und Winkel eingeben (z.B. 1,90):")
        if not ok or not text:
            return

        try:
            page_number, angle = map(int, text.split(","))
            PDFRotator.rotate_pages(self.pdf_handler.file_path, self.pdf_handler.file_path, {page_number: angle})
            self.pdf_viewer.render_page()  # Vorschau aktualisieren
            QMessageBox.information(None, "Erfolg", f"Seite {page_number} wurde um {angle}° gedreht.")
        except Exception as e:
            QMessageBox.critical(None, "Fehler", f"Seite konnte nicht gedreht werden:\n{e}")

    def add_pages(self):
        """Fügt ein weiteres PDF zur aktuellen Datei hinzu."""
        if not self.pdf_handler.current_pdf:
            QMessageBox.warning(None, "Keine Datei geöffnet", "Bitte zuerst ein PDF öffnen.")
            return

        files, _ = QFileDialog.getOpenFileNames(None, "Weitere PDFs auswählen", "", "PDF Dateien (*.pdf)")
        if not files:
            return

        output_file, _ = QFileDialog.getSaveFileName(None, "Zusammengeführte Datei speichern", "", "PDF Dateien (*.pdf)")
        if not output_file:
            return

        try:
            input_files = [self.pdf_handler.file_path] + files
            PDFMerger.merge_pdfs(input_files, output_file)
            QMessageBox.information(None, "Erfolg", f"PDFs erfolgreich zusammengeführt in: {output_file}")
        except Exception as e:
            QMessageBox.critical(None, "Fehler", f"Zusammenführung fehlgeschlagen:\n{e}")
