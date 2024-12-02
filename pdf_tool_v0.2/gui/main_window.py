# Imports
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout
# Imports /core
from core.pdf_handler import PDFHandler
# Imports /gui
from gui.pdf_viewer import PDFViewer
from gui.action_buttons import ActionButtons
from gui.navigation_bar import NavigationBar
# Imports /utils
from utils.config import Config
from utils.utils import Utils


class MainWindow(QMainWindow):
    """Hauptfenster der PDF-Anwendung."""

    def __init__(self):
        super().__init__()

        # Fenstereinstellungen
        self.setWindowTitle(Config.APP_NAME)
        self.setGeometry(100, 100, 800, 600)

        # Zentral-Widget und Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # PDF-Handler initialisieren
        self.pdf_handler = PDFHandler()

        # GUI-Komponenten initialisieren

        print(f"Instanziiere PDFViewer mit pdf_handler={self.pdf_handler}")
        self.pdf_viewer = PDFViewer(self.pdf_handler)
        self.navigation_bar = NavigationBar(self.pdf_handler, self.pdf_viewer)
        self.action_buttons = ActionButtons(self.pdf_handler, self.pdf_viewer, self.navigation_bar)

        # GUI-Komponenten hinzufügen
        self.main_layout.addLayout(self.pdf_viewer.layout, stretch=3)
        self.main_layout.addLayout(self.action_buttons.layout, stretch=1)
