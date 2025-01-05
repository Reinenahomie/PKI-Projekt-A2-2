from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTreeWidget, QTreeWidgetItem, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from .pdf_functions import show_pdf_open_dialog, extract_zugferd_data
import xml.etree.ElementTree as ET

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

        # XML Tree View mit angepasster Spaltenbreite
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Element", "Wert"])
        self.tree.setColumnCount(2)
        
        # Header-Konfiguration in der richtigen Reihenfolge
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Erste Spalte fixiert
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Zweite Spalte dehnbar
        self.tree.setColumnWidth(0, int(self.width() * 0.5))  # Float zu Integer konvertieren
        
        main_layout.addWidget(self.tree)

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
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Keine ZUGFeRD-Daten",
                "Diese PDF enthält keine ZUGFeRD-Rechnungsdaten."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler beim Laden",
                f"Die ZUGFeRD-Daten konnten nicht geladen werden:\n{str(e)}"
            )

    def create_tree_item(self, element):
        """Erstellt ein TreeWidgetItem aus einem XML-Element."""
        item = QTreeWidgetItem()
        
        # Namespace aus Tag entfernen für bessere Lesbarkeit
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        item.setText(0, tag)
        
        # Text und Attribute anzeigen
        if element.text and element.text.strip():
            item.setText(1, element.text.strip())
        
        # Attribute als Kinder hinzufügen
        for key, value in element.attrib.items():
            attr_item = QTreeWidgetItem()
            attr_item.setText(0, f"@{key}")
            attr_item.setText(1, value)
            item.addChild(attr_item)
        
        # Rekursiv für alle Kindelemente
        for child in element:
            item.addChild(self.create_tree_item(child))
        
        return item

    def display_data(self, xml_data, parsed_data):
        """Zeigt die extrahierten Daten formatiert an."""
        # Tabelle mit geparsten Daten füllen
        self.table.setRowCount(len(parsed_data))
        for row, (key, value) in enumerate(parsed_data.items()):
            self.table.setItem(row, 0, QTableWidgetItem(key))
            self.table.setItem(row, 1, QTableWidgetItem(str(value)))

        # XML-Baum erstellen
        self.tree.clear()
        root = ET.fromstring(xml_data)
        root_item = self.create_tree_item(root)
        self.tree.addTopLevelItem(root_item)
        self.tree.expandToDepth(2)  # Erste drei Ebenen automatisch öffnen

    def resizeEvent(self, event):
        """Behandelt Größenänderungen des Widgets"""
        super().resizeEvent(event)
        # Aktualisiere Spaltenbreite bei Größenänderung
        self.tree.setColumnWidth(0, int(self.width() * 0.5))  # Float zu Integer konvertieren 