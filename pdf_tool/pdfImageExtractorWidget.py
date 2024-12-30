from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, 
    QScrollArea, QGridLayout, QFrame, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QSize
from .pdf_functions import extract_images_from_pdf, show_pdf_open_dialog  # Annahme: Funktion wird in `pdf_functions` implementiert
import os


class ImagePreviewWidget(QLabel):
    """Widget für ein einzelnes Vorschaubild."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 1px solid #cccccc;
                background-color: white;
                padding: 5px;
            }
        """)

    def setPixmap(self, pixmap):
        """Überschreibt setPixmap um das Seitenverhältnis zu erhalten."""
        if pixmap:
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            super().setPixmap(scaled_pixmap)

class PDFImageExtractorWidget(QWidget):
    """
    Widget zur Extraktion von Bildern aus PDF-Dateien.
    
    Diese Komponente ermöglicht:
    - Hochladen einer PDF
    - Vorschau der enthaltenen Bilder
    - Extraktion aller Bilder in ein Zielverzeichnis
    
    Verwendung:
    1. PDF hochladen über "PDF hochladen" Button
    2. Vorschau des ersten Bildes wird angezeigt
    3. "Bilder extrahieren und speichern" speichert alle Bilder
    """

    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.pdf_path = None
        self.image_paths = []

        # Hauptlayout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Buttons
        upload_button = QPushButton("PDF öffnen")
        upload_button.clicked.connect(self.open_file_dialog)
        main_layout.addWidget(upload_button)

        # Bereich für Bildvorschau
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Container für das Grid
        self.preview_container = QWidget()
        self.grid_layout = QGridLayout(self.preview_container)
        self.grid_layout.setSpacing(10)
        
        # Initial-Label
        self.initial_label = QLabel("Bitte eine PDF-Datei hochladen.")
        self.initial_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(self.initial_label, 0, 0)
        
        self.scroll_area.setWidget(self.preview_container)
        main_layout.addWidget(self.scroll_area)

        # Button-Container für horizontale Anordnung
        button_layout = QHBoxLayout()
        
        extract_button = QPushButton("Bilder speichern")
        extract_button.clicked.connect(self.extract_images)
        extract_button.setEnabled(False)
        self.extract_button = extract_button
        button_layout.addWidget(extract_button)

        zip_button = QPushButton("Bilder als ZIP-Datei speichern")
        zip_button.clicked.connect(self.extract_images_to_zip)
        zip_button.setEnabled(False)
        self.zip_button = zip_button
        button_layout.addWidget(zip_button)

        main_layout.addLayout(button_layout)

        back_button = QPushButton("Zur Übersicht")
        back_button.clicked.connect(self.return_to_home)
        main_layout.addWidget(back_button)

        self.setLayout(main_layout)

    def return_to_home(self):
        """Zurück zur Startseite."""
        self.stacked_widget.setCurrentIndex(0)
        self.window().setWindowTitle("PDF Tool")  # Titel zurücksetzen

    def open_file_dialog(self):
        """Öffnet den Dialog zum Auswählen einer PDF-Datei."""
        pdf_path = show_pdf_open_dialog(self)
        if pdf_path:
            self.load_pdf(pdf_path)

    def load_pdf(self, pdf_path):
        """
        Lädt eine PDF und zeigt Vorschaubilder aller enthaltenen Bilder.
        
        Args:
            pdf_path (str): Pfad zur PDF-Datei
        """
        self.pdf_path = pdf_path
        self.image_paths = []

        try:
            # Bestehende Vorschaubilder entfernen
            for i in reversed(range(self.grid_layout.count())): 
                self.grid_layout.itemAt(i).widget().setParent(None)

            images = extract_images_from_pdf(pdf_path, preview_only=True)
            
            if images:
                # Bilder in einem Grid anordnen
                for index, image_path in enumerate(images):
                    preview = ImagePreviewWidget()
                    pixmap = QPixmap(image_path)
                    preview.setPixmap(pixmap)
                    
                    # Position im Grid berechnen (4 Bilder pro Zeile)
                    row = index // 4
                    col = index % 4
                    self.grid_layout.addWidget(preview, row, col)
                
                self.extract_button.setEnabled(True)
                self.zip_button.setEnabled(True)
            else:
                label = QLabel("Keine Bilder in der PDF gefunden.\nBitte wählen Sie eine andere PDF-Datei.")
                label.setAlignment(Qt.AlignCenter)
                self.grid_layout.addWidget(label, 0, 0)
                self.extract_button.setEnabled(False)
                self.zip_button.setEnabled(False)

        except Exception as e:
            error_msg = f"""
            Die PDF konnte nicht geladen werden.
            
            Mögliche Gründe:
            - Die Datei ist keine gültige PDF
            - Die Datei ist beschädigt
            - Keine Leserechte
            
            Technische Details: {str(e)}
            """
            QMessageBox.critical(self, "Fehler beim Laden", error_msg)

    def extract_images(self):
        """Extrahiert alle Bilder aus der PDF."""
        if not self.pdf_path:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst eine PDF auswählen.")
            return

        output_dir = QFileDialog.getExistingDirectory(
            self, 
            "Wo sollen die Bilder gespeichert werden?"
        )
        if not output_dir:
            return

        try:
            # Bilder extrahieren
            extracted_images = extract_images_from_pdf(self.pdf_path, output_dir=output_dir)
            
            if extracted_images:
                success_msg = (
                    f"{len(extracted_images)} Bilder wurden erfolgreich gespeichert.\n\n"
                    f"Speicherort: {output_dir}"
                )
                QMessageBox.information(self, "Extraktion erfolgreich", success_msg)
            else:
                QMessageBox.information(
                    self, 
                    "Keine Bilder gefunden", 
                    "In der PDF wurden keine Bilder gefunden."
                )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Fehler bei der Extraktion", 
                f"Die Bilder konnten nicht extrahiert werden:\n{str(e)}"
            )

    def extract_images_to_zip(self):
        """Extrahiert alle Bilder und speichert sie als ZIP-Datei."""
        if not self.pdf_path:
            QMessageBox.warning(self, "Fehler", "Bitte zuerst eine PDF auswählen.")
            return

        # Generiere ZIP-Namen aus PDF-Namen
        pdf_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
        default_zip_name = f"Bilder_{pdf_name}.zip"

        zip_path, _ = QFileDialog.getSaveFileName(
            self,
            "ZIP-Datei speichern unter",
            default_zip_name,  # Vorgeschlagener Name
            "ZIP Dateien (*.zip)"
        )
        if not zip_path:
            return

        try:
            # Temporäres Verzeichnis für die Bilder
            import tempfile
            import shutil
            with tempfile.TemporaryDirectory() as temp_dir:
                # Bilder extrahieren
                extracted_images = extract_images_from_pdf(self.pdf_path, output_dir=temp_dir)
                
                if extracted_images:
                    # ZIP erstellen
                    from .pdf_functions import create_zip_from_files
                    create_zip_from_files(extracted_images, zip_path)
                    
                    success_msg = (
                        f"{len(extracted_images)} Bilder wurden erfolgreich als ZIP gespeichert.\n\n"
                        f"Speicherort: {zip_path}"
                    )
                    QMessageBox.information(self, "ZIP-Erstellung erfolgreich", success_msg)
                else:
                    QMessageBox.information(
                        self,
                        "Keine Bilder gefunden",
                        "In der PDF wurden keine Bilder gefunden."
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler bei der ZIP-Erstellung",
                f"Die ZIP-Datei konnte nicht erstellt werden:\n{str(e)}"
            )
