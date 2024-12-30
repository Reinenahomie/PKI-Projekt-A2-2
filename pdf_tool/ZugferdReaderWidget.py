from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from .pdf_functions import show_pdf_open_dialog, extract_zugferd_data

class ZugferdReaderWidget(QWidget):
    """Widget zum Lesen und Anzeigen von ZUGFeRD-Rechnungsdaten."""
    
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.pdf_path = None
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # PDF öffnen Button
        self.open_button = QPushButton("PDF öffnen")
        self.open_button.clicked.connect(self.open_file_dialog)
        main_layout.addWidget(self.open_button)

        # Tabelle für die Rechnungsdaten
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Feld", "Wert"])
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

        # XML Anzeige
        self.xml_view = QTextEdit()
        self.xml_view.setReadOnly(True)
        self.xml_view.setPlaceholderText("XML-Daten werden hier angezeigt")
        main_layout.addWidget(self.xml_view)

        # Zurück-Button
        back_button = QPushButton("Zur Übersicht")
        back_button.clicked.connect(self.return_to_home)
        main_layout.addWidget(back_button)

        self.setLayout(main_layout)

    def return_to_home(self):
        self.stacked_widget.setCurrentIndex(0)

    def open_file_dialog(self):
        pdf_path = show_pdf_open_dialog(self, "ZUGFeRD-Rechnung öffnen")
        if pdf_path:
            self.load_zugferd(pdf_path)

    def load_zugferd(self, pdf_path):
        """Lädt und analysiert eine ZUGFeRD-Rechnung."""
        try:
            xml_data, parsed_data = extract_zugferd_data(pdf_path)
            self.display_data(xml_data, parsed_data)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler beim Laden",
                f"Die ZUGFeRD-Daten konnten nicht geladen werden:\n{str(e)}"
            )

    def display_data(self, xml_data, parsed_data):
        """Zeigt die extrahierten Daten an."""
        # XML-Daten anzeigen
        self.xml_view.setText(xml_data)

        # Tabelle mit geparsten Daten füllen
        self.table.setRowCount(len(parsed_data))
        for row, (key, value) in enumerate(parsed_data.items()):
            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(row, 1, QTableWidgetItem(str(value))) 