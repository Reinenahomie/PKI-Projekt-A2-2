from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton
# from PyQt5.QtWidgets import QHBoxLayout, QPushButton

class ActionButtons:
    def __init__(self, pdf_preview):
        # 
        self.layout = QVBoxLayout()
        self.pdf_preview = pdf_preview

        self.open_button = QPushButton("PDF öffnen")
        self.open_button.clicked.connect(self.open_pdf)
        self.layout.addWidget(self.open_button)

        self.text_button = QPushButton("Text extrahieren")
        self.text_button.setEnabled(False)
        self.layout.addWidget(self.text_button)

        self.image_button = QPushButton("Bilder extrahieren")
        self.image_button.setEnabled(False)
        self.layout.addWidget(self.image_button)

        self.layout.addStretch()

    def open_pdf(self):
        # Öffnet ein Datei-Dialog und lädt ein PDF
        pass

class NavigationButtons:
    def __init__(self, pdf_preview):
        self.pdf_preview = pdf_preview
        self.layout = QHBoxLayout()

        self.prev_button = QPushButton("Seite zurück")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setEnabled(False)
        self.layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Seite vor")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        self.layout.addWidget(self.next_button)

    def previous_page(self):
        if self.pdf_preview.current_page_index > 0:
            self.pdf_preview.current_page_index -= 1
            self.pdf_preview.render_page()
            self.update_buttons()

    def next_page(self):
        if self.pdf_preview.current_page_index < self.pdf_preview.total_pages - 1:
            self.pdf_preview.current_page_index += 1
            self.pdf_preview.render_page()
            self.update_buttons()

    def update_buttons(self):
        self.prev_button.setEnabled(self.pdf_preview.current_page_index > 0)
        self.next_button.setEnabled(self.pdf_preview.current_page_index < self.pdf_preview.total_pages - 1)

