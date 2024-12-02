# PyQt5 Bibliotheken
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget


# Projektinterne Imports
# from gui.navigation_buttons import NavigationButtons
from gui.pdf_preview import PDFPreview
from gui.gui_elements import ActionButtons, NavigationButtons


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Team Project")
        self.setGeometry(100, 100, 800, 600)

        # Hauptlayout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Linke Seite: PDF-Vorschau und Navigation
        self.pdf_preview = PDFPreview()
        
        self.navigation_buttons = NavigationButtons(self.pdf_preview)
        self.main_layout.addLayout(self.pdf_preview.layout, stretch=3)

        # Rechte Seite: Aktionsbuttons
        self.action_buttons = ActionButtons(self.pdf_preview)
        self.main_layout.addLayout(self.action_buttons.layout, stretch=1)
