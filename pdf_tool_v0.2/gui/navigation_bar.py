from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QMessageBox


class NavigationBar:
    """Verwaltet die Navigation durch die Seiten des PDFs."""

    def __init__(self, pdf_handler, pdf_viewer):
        """
        Initialisiert die Navigationsleiste.

        Args:
            pdf_handler (PDFHandler): Die zentrale PDF-Logik.
            pdf_viewer (PDFViewer): Referenz auf die PDF-Anzeige.
        """
        self.pdf_handler = pdf_handler
        self.pdf_viewer = pdf_viewer
        self.layout = QHBoxLayout()

        # Vorherige Seite Button
        self.prev_button = QPushButton("Seite zurück")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setEnabled(False)
        self.layout.addWidget(self.prev_button)

        # Nächste Seite Button
        self.next_button = QPushButton("Seite vor")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        self.layout.addWidget(self.next_button)

    def update_buttons(self):
        """Aktualisiert die Aktivierung der Buttons basierend auf der aktuellen Seite."""
        if self.pdf_handler.current_pdf:
            current_page = self.pdf_handler.current_page_index
            total_pages = self.pdf_handler.total_pages

            self.prev_button.setEnabled(current_page > 0)
            self.next_button.setEnabled(current_page < total_pages - 1)
        else:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)

    def previous_page(self):
        """Wechselt zur vorherigen Seite des PDFs."""
        if not self.pdf_handler.current_pdf:
            QMessageBox.warning(None, "Keine Datei geöffnet", "Bitte zuerst ein PDF öffnen.")
            return

        if self.pdf_handler.current_page_index > 0:
            self.pdf_handler.current_page_index -= 1
            self.pdf_viewer.render_page()
            self.update_buttons()

    def next_page(self):
        """Wechselt zur nächsten Seite des PDFs."""
        if not self.pdf_handler.current_pdf:
            QMessageBox.warning(None, "Keine Datei geöffnet", "Bitte zuerst ein PDF öffnen.")
            return

        if self.pdf_handler.current_page_index < self.pdf_handler.total_pages - 1:
            self.pdf_handler.current_page_index += 1
            self.pdf_viewer.render_page()
            self.update_buttons()
