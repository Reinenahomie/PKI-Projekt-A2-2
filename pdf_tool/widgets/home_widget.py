import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from ..config import HOME_IMAGE_PATH

class HomeWidget(QWidget):
    """
    Widget für die Startseite der Anwendung.
    
    Zeigt ein Willkommensbild oder eine Nachricht an.
    Das Widget verwendet ein vertikales Layout und zeigt entweder:
    - Ein konfiguriertes Startbild aus HOME_IMAGE_PATH
    - Eine Fehlermeldung, falls das Bild nicht gefunden wird
    """
    def __init__(self, parent=None):
        """
        Initialisiert das HomeWidget.
        
        Args:
            parent: Optional, das übergeordnete Widget
        """
        super().__init__(parent)
        
        # Layout erstellen
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 0, 20, 20)  # Oberer Rand auf 0
        layout.setSpacing(20)
        
        # Container mit grauem Hintergrund
        container = QWidget()
        container.setMinimumSize(400, 600)  # Gleiche Mindestgröße wie im PDFPreviewWidget
        container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(10)
        
        # Erstelle ein Label für das Bild oder die Fehlermeldung
        label = QLabel()
        label.setAlignment(Qt.AlignCenter)  # Zentriere den Inhalt
        label.setStyleSheet("""
            QLabel {
                background-color: transparent;
            }
        """)

        # Versuche das Startbild zu laden
        if os.path.exists(HOME_IMAGE_PATH):
            # Wenn das Bild existiert, lade es als Pixmap
            pixmap = QPixmap(HOME_IMAGE_PATH)
            label.setPixmap(pixmap)
        else:
            # Wenn das Bild nicht gefunden wurde, zeige eine Fehlermeldung
            label.setText("Startbild nicht gefunden.")
            
        # Füge das Label zum Container-Layout hinzu
        container_layout.addWidget(label)
        
        # Füge Container zum Hauptlayout hinzu mit Stretch-Priorität
        layout.addWidget(container, 1)  # 1 gibt dem Container die Priorität beim Dehnen
        
        self.setLayout(layout) 