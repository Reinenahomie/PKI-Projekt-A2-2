import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog,
    QLabel, QGridLayout, QScrollArea, QSpinBox, QStackedWidget, QComboBox, QMessageBox, QListWidget
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QImage
from PyQt5.QtCore import Qt, QSize
from .pdfImageExtractorWidget import PDFImageExtractorWidget  # Importiere das neue Widget
from .pdf_functions import load_pdf, render_page, split_pdf_into_pages, create_zip_from_files, show_pdf_open_dialog, merge_pdfs
from .config import HOME_IMAGE_PATH  # hier wird der Pfad aus der config geladen
from .ZugferdReaderWidget import ZugferdReaderWidget  # Importiere das neue Widget


class HomeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)
        layout.setSpacing(20)

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)

        # Lade das Startbild
        if os.path.exists(HOME_IMAGE_PATH):
            pixmap = QPixmap(HOME_IMAGE_PATH)
            # Optional skalieren, wenn zu groß:
            # pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
        else:
            label.setText("Startbild nicht gefunden.")

        layout.addWidget(label)
        self.setLayout(layout)




class PDFPreviewWidget(QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.pdf_path = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_factor = 1.0

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top-Bar mit Exit-Button
        top_bar = QHBoxLayout()
        top_bar.addStretch()  # Platzhalter nach links
        close_button = QPushButton("X")
        close_button.setFixedSize(40,40)
        close_button.clicked.connect(self.return_to_home)
        top_bar.addWidget(close_button)
        main_layout.addLayout(top_bar)

        self.scroll_area = QScrollArea()
        self.page_label = QLabel("Lade eine PDF, um die Vorschau anzuzeigen")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.page_label)
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        # Steuerungsbereich
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.previous_button = QPushButton("←")
        self.previous_button.clicked.connect(self.previous_page)
        self.previous_button.setEnabled(False)
        controls_layout.addWidget(self.previous_button)

        self.next_button = QPushButton("→")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        controls_layout.addWidget(self.next_button)

        self.page_input = QSpinBox()
        self.page_input.setMinimum(1)
        self.page_input.setMaximum(1)
        self.page_input.setValue(1)
        self.page_input.valueChanged.connect(self.jump_to_page)
        controls_layout.addWidget(self.page_input)

        self.page_info = QLabel("/ 1")
        controls_layout.addWidget(self.page_info)

        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        controls_layout.addWidget(self.zoom_out_button)

        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        controls_layout.addWidget(self.zoom_in_button)

        main_layout.addLayout(controls_layout)

        self.upload_button = QPushButton("PDF öffnen")
        self.upload_button.clicked.connect(self.open_file_dialog)
        main_layout.addWidget(self.upload_button)

        self.setLayout(main_layout)

    def return_to_home(self):
        self.stacked_widget.setCurrentIndex(0)

    def open_file_dialog(self):
        """Öffnet den Dialog zum Auswählen einer PDF-Datei."""
        pdf_path = show_pdf_open_dialog(self)
        if pdf_path:
            self.load_pdf(pdf_path)

    def load_pdf(self, pdf_path):
        self.pdf_path = pdf_path
        self.current_page = 0
        self.zoom_factor = 1.0

        try:
            self.total_pages = load_pdf(pdf_path)
            self.page_input.setMaximum(self.total_pages)
            self.page_input.setValue(1)
            self.page_info.setText(f"/ {self.total_pages}")

            self.previous_button.setEnabled(False)
            self.next_button.setEnabled(self.total_pages > 1)

            self.display_page()

        except Exception as e:
            self.page_label.setText(str(e))

    def display_page(self):
        if not self.pdf_path or self.current_page < 0 or self.current_page >= self.total_pages:
            return

        try:
            pix = render_page(self.pdf_path, self.current_page, self.zoom_factor)
            image_path = f"temp_page_{self.current_page}.png"
            pix.save(image_path)

            pixmap = QPixmap(image_path)
            self.page_label.setPixmap(pixmap)
            self.page_label.setAlignment(Qt.AlignCenter)

            os.remove(image_path)

            self.previous_button.setEnabled(self.current_page > 0)
            self.next_button.setEnabled(self.current_page < self.total_pages - 1)
            self.page_input.setValue(self.current_page + 1)

        except Exception as e:
            self.page_label.setText(str(e))

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page()

    def jump_to_page(self):
        requested_page = self.page_input.value() - 1
        if 0 <= requested_page < self.total_pages:
            self.current_page = requested_page
            self.display_page()

    def zoom_in(self):
        self.zoom_factor += 0.1
        self.display_page()

    def zoom_out(self):
        if self.zoom_factor > 0.2:
            self.zoom_factor -= 0.1
            self.display_page()


class PDFSplitWidget(QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.pdf_path = None
        self.total_pages = 0

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top-Bar mit Exit-Button
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        close_button = QPushButton("X")
        close_button.setFixedSize(40,40)
        close_button.clicked.connect(self.return_to_home)
        top_bar.addWidget(close_button)
        main_layout.addLayout(top_bar)

        self.options_combo = QComboBox()
        self.options_combo.addItem("Alle Seiten")
        main_layout.addWidget(self.options_combo)

        self.upload_button = QPushButton("PDF öffnen")
        self.upload_button.clicked.connect(self.open_file_dialog)
        main_layout.addWidget(self.upload_button)

        self.split_button = QPushButton("Trennen starten")
        self.split_button.setEnabled(False)
        self.split_button.clicked.connect(self.start_splitting)
        main_layout.addWidget(self.split_button)

        self.status_label = QLabel("")
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def return_to_home(self):
        self.stacked_widget.setCurrentIndex(0)

    def open_file_dialog(self):
        """Öffnet den Dialog zum Auswählen einer PDF-Datei."""
        pdf_path = show_pdf_open_dialog(self)
        if pdf_path:
            self.load_pdf(pdf_path)

    def load_pdf(self, pdf_path):
        try:
            self.pdf_path = pdf_path
            self.total_pages = load_pdf(pdf_path)
            self.split_button.setEnabled(True)
            self.status_label.setText(f"PDF geladen: {os.path.basename(pdf_path)} mit {self.total_pages} Seiten.")
        except Exception as e:
            self.status_label.setText(str(e))

    def start_splitting(self):
        if not self.pdf_path or self.total_pages == 0:
            self.status_label.setText("Keine PDF zum Trennen geladen.")
            return

        zip_path, _ = QFileDialog.getSaveFileName(self, "ZIP-Datei speichern", "seiten.zip", "ZIP Dateien (*.zip)")
        if not zip_path:
            return

        temp_dir = "temp_split"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        try:
            page_files = split_pdf_into_pages(self.pdf_path, temp_dir)
            create_zip_from_files(page_files, zip_path)

            for f in page_files:
                os.remove(f)
            os.rmdir(temp_dir)

            self.status_label.setText(f"PDF erfolgreich getrennt. ZIP gespeichert unter: {zip_path}")
            QMessageBox.information(self, "Erfolg", f"Die PDF wurde erfolgreich getrennt und als ZIP gespeichert:\n{zip_path}")

        except Exception as e:
            self.status_label.setText(str(e))


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF Tool")
        self.setGeometry(100, 100, 1000, 600)

        # Hauptlayout des Fensters
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Menü-Bereich (am oberen Rand)
        self.menu_widget = QWidget()
        menu_layout = QGridLayout(self.menu_widget)
        menu_layout.setSpacing(20)
        menu_layout.setContentsMargins(0, 0, 0, 0)

        # Kacheln erstellen (mit Icons optional)
        pdf_to_word_button = self.create_tile_button("PDF to Word")
        extract_images_button = self.create_tile_button("Bilder extrahieren")
        merge_pdf_button = self.create_tile_button("PDF zusammenfügen")
        pdf_preview_button = self.create_tile_button("PDF Vorschau")
        split_pdf_button = self.create_tile_button("PDF trennen")
        zugferd_button = self.create_tile_button("ZUGFeRD Rechnung")

        # Buttons in 2x3 Grid anordnen
        menu_layout.addWidget(pdf_to_word_button, 0, 0)    # Erste Reihe
        menu_layout.addWidget(extract_images_button, 0, 1)
        menu_layout.addWidget(merge_pdf_button, 0, 2)
        
        menu_layout.addWidget(pdf_preview_button, 1, 0)    # Zweite Reihe
        menu_layout.addWidget(split_pdf_button, 1, 1)
        menu_layout.addWidget(zugferd_button, 1, 2)

        self.menu_widget.setLayout(menu_layout)
        main_layout.addWidget(self.menu_widget)

        # Stacked Widget für unterschiedliche Ansichten
        self.stacked_widget = QStackedWidget()

        # Startseite mit Bild und instanziierten Widgets 

        self.page_home = HomeWidget()
        self.page_pdf_to_word = QWidget()  
        self.page_extract_images = PDFImageExtractorWidget(self.stacked_widget)  # Neues Widget
        self.page_merge_pdf = PDFZusammenfuegen(self.stacked_widget)
        self.page_pdf_preview = PDFPreviewWidget(self.stacked_widget)
        self.page_split_pdf = PDFSplitWidget(self.stacked_widget)
        self.page_zugferd = ZugferdReaderWidget(self.stacked_widget)

        self.stacked_widget.addWidget(self.page_home)           # Index 0 (Startseite)
        self.stacked_widget.addWidget(self.page_pdf_to_word)    # Index 1
        self.stacked_widget.addWidget(self.page_extract_images) # Index 2
        self.stacked_widget.addWidget(self.page_merge_pdf)      # Index 3
        self.stacked_widget.addWidget(self.page_pdf_preview)    # Index 4
        self.stacked_widget.addWidget(self.page_split_pdf)      # Index 5
        self.stacked_widget.addWidget(self.page_zugferd)        # Index 6

        main_layout.addWidget(self.stacked_widget)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Verknüpfungen der Buttons mit den jeweiligen Seiten
        pdf_to_word_button.clicked.connect(lambda: self.switch_page(1, "PDF Tool - PDF to Word"))
        extract_images_button.clicked.connect(lambda: self.switch_page(2, "PDF Tool - Bilder extrahieren"))
        merge_pdf_button.clicked.connect(lambda: self.switch_page(3, "PDF Tool - PDF zusammenfügen"))
        pdf_preview_button.clicked.connect(lambda: self.switch_page(4, "PDF Tool - PDF Vorschau"))
        split_pdf_button.clicked.connect(lambda: self.switch_page(5, "PDF Tool - PDF trennen"))
        zugferd_button.clicked.connect(lambda: self.switch_page(6, "PDF Tool - ZUGFeRD Rechnung"))
        
        # Stylesheet anwenden
        self.apply_stylesheet()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 10px;
                font-size: 15px;
                text-align: center;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #999999;
            }
            QLabel {
                font-size: 14px;
            }
            QScrollArea {
                border: none;
            }
        """)

    def create_tile_button(self, text, icon_path=None):
        button = QPushButton(text)
        button.setFixedSize(300, 60)
        return button

    def switch_page(self, index, title):
        """Wechselt die Seite und aktualisiert den Fenstertitel."""
        self.stacked_widget.setCurrentIndex(index)
        self.setWindowTitle(title)

    # Methode für die Rückkehr zur Startseite (in allen Widgets verwenden)
    def return_to_home(self):
        self.stacked_widget.setCurrentIndex(0)
        self.setWindowTitle("PDF Tool")  # Zurück zum Standard-Titel


class PDFZusammenfuegen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        label = QLabel("PDF Zusammenfügen")
        label.setFont(QFont("Arial", 20))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # List to show selected PDF files
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)

        # Button to open files
        self.open_button = QPushButton("PDF hinzufügen")
        self.open_button.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.open_button)

        # Button to merge files
        self.merge_button = QPushButton("PDFs zusammenfügen")
        self.merge_button.setEnabled(False)
        self.merge_button.clicked.connect(self.merge_pdfs)
        layout.addWidget(self.merge_button)

        self.setLayout(layout)

        # Store selected PDF paths
        self.pdf_paths = []

    def open_file_dialog(self):
        """Allows users to select one or more PDF files."""
        files, _ = QFileDialog.getOpenFileNames(self, "PDFs auswählen", "", "PDF Dateien (*.pdf)")
        if files:
            self.pdf_paths.extend(files)
            self.file_list.addItems(files)
            self.merge_button.setEnabled(True)

    def merge_pdfs(self):
        """Merges the selected PDFs."""
        if not self.pdf_paths:
            QMessageBox.warning(self, "Fehler", "Keine PDF-Dateien ausgewählt.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "PDF speichern", "zusammengefuegt.pdf", "PDF Dateien (*.pdf)")
        if not save_path:
            return

        try:
            merge_pdfs(self.pdf_paths, save_path)
            QMessageBox.information(self, "Erfolg", f"PDFs erfolgreich zusammengefügt und gespeichert unter:\n{save_path}")
            self.pdf_paths = []
            self.file_list.clear()
            self.merge_button.setEnabled(False)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Zusammenfügen der PDFs:\n{str(e)}")
