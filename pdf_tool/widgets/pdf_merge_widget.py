from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QMessageBox, QFileDialog, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QImage, QPixmap
from ..utils.pdf_functions import merge_pdfs, render_page
import os
from datetime import datetime

class PDFPreviewTile(QWidget):
    """Widget für ein einzelnes PDF-Vorschaubild in einer quadratischen Kachel."""
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.selected = False
        
        # Layout erstellen
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Container für das Vorschaubild
        self.preview_container = QLabel()
        self.preview_container.setFixedSize(200, 200)
        self.preview_container.setAlignment(Qt.AlignCenter)
        self.update_style()
        layout.addWidget(self.preview_container)
        
        # Label für den Dateinamen
        filename = os.path.basename(pdf_path)
        self.name_label = QLabel(filename)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        
        self.setLayout(layout)
        
        # Lade die Vorschau
        self.load_preview()

    def update_style(self):
        """Aktualisiert den Stil basierend auf dem Auswahlstatus."""
        border_color = "#2196F3" if self.selected else "#cccccc"
        border_width = "3px" if self.selected else "1px"
        self.preview_container.setStyleSheet(f"""
            QLabel {{
                border: {border_width} solid {border_color};
                background-color: white;
                padding: 5px;
            }}
        """)

    def mousePressEvent(self, event):
        """Behandelt Mausklicks auf die Kachel."""
        if event.button() == Qt.LeftButton:
            self.selected = not self.selected
            self.update_style()
            # Informiere das übergeordnete Widget über die Änderung
            if isinstance(self.parent(), QWidget):
                parent = self.parent()
                while parent and not isinstance(parent, PDFMergeWidget):
                    parent = parent.parent()
                if parent:
                    parent.update_delete_button()

    def load_preview(self):
        """Lädt die Vorschau der ersten Seite der PDF."""
        try:
            # Rendere die erste Seite
            pix = render_page(self.pdf_path, 0, 1.0)
            
            # Berechne den optimalen Zoom-Faktor
            available_size = self.preview_container.size()
            width_ratio = (available_size.width() - 10) / pix.width
            height_ratio = (available_size.height() - 10) / pix.height
            zoom = min(width_ratio, height_ratio)
            
            # Rendere mit optimalem Zoom
            pix = render_page(self.pdf_path, 0, zoom)
            
            # Konvertiere zu QPixmap und zeige an
            img_data = pix.tobytes("ppm")
            qimg = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(qimg)
            self.preview_container.setPixmap(pixmap)
            
        except Exception as e:
            self.preview_container.setText("Vorschau\nnicht verfügbar")

class PDFMergeWidget(QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.preview_tiles = []  # Liste der Vorschau-Kacheln
        
        # Layout erstellen
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 0, 20, 20)  # Seitliche Ränder auf 20px
        layout.setSpacing(20)

        # Scroll-Bereich für die PDF-Vorschauen
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container für das Grid
        self.preview_container = QWidget()
        self.preview_container.setMinimumSize(400, 600)  # Angepasste Mindestgröße für Hochformat
        self.preview_container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)
        
        # Grid-Layout mit zwei Spalten
        self.grid_layout = QGridLayout(self.preview_container)
        self.grid_layout.setSpacing(20)  # Abstand zwischen den Kacheln
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        
        # Initial-Label
        self.initial_label = QLabel("Keine PDFs ausgewählt.")
        self.initial_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(self.initial_label, 0, 0, 1, 2)
        
        scroll_area.setWidget(self.preview_container)
        layout.addWidget(scroll_area, 1)

        self.setLayout(layout)

        # Liste der PDF-Pfade
        self.pdf_paths = []

    def showEvent(self, event):
        """Wird aufgerufen, wenn das Widget angezeigt wird."""
        super().showEvent(event)
        # Hole die aktuelle PDF vom Hauptfenster
        main_window = self.window()
        current_pdf = main_window.get_current_pdf()
        
        # Setze die Liste zurück und aktualisiere die Vorschau
        self.pdf_paths = []
        if current_pdf:
            self.pdf_paths.append(current_pdf)
        self.update_preview()

    def add_pdf(self):
        """Öffnet einen Dialog zum Auswählen mehrerer PDF-Dateien."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("PDF-Dateien auswählen")
        file_dialog.setNameFilter("PDF-Dateien (*.pdf)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)  # Erlaube Mehrfachauswahl
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # Verwende PyQt Dialog
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            selected_files = file_dialog.selectedFiles()
            self.pdf_paths.extend(selected_files)  # Füge alle ausgewählten Dateien hinzu
            self.update_preview()

    def remove_selected_pdf(self):
        """Entfernt die ausgewählten PDFs aus der Liste."""
        # Sammle alle ausgewählten PDFs
        selected_paths = []
        for tile in self.preview_tiles:
            if tile.selected:
                selected_paths.append(tile.pdf_path)
        
        # Entferne die ausgewählten PDFs
        if selected_paths:
            for path in selected_paths:
                self.pdf_paths.remove(path)
            self.update_preview()

    def update_preview(self):
        """Aktualisiert die Vorschau-Kacheln."""
        # Lösche alle bestehenden Widgets
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # Leere die Liste der Vorschau-Kacheln
        self.preview_tiles = []
        
        if not self.pdf_paths:
            # Zeige Initial-Label wenn keine PDFs ausgewählt
            self.initial_label = QLabel("Keine PDFs ausgewählt.")
            self.initial_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(self.initial_label, 0, 0, 1, 2)
            return
        
        # Füge Vorschau-Kacheln hinzu
        for index, pdf_path in enumerate(self.pdf_paths):
            preview = PDFPreviewTile(pdf_path)
            self.preview_tiles.append(preview)
            row = index // 2
            col = index % 2
            self.grid_layout.addWidget(preview, row, col)
        
        self.update_delete_button()

    def update_delete_button(self):
        """Aktiviert oder deaktiviert den Lösch-Button basierend auf der Auswahl."""
        # Prüfe, ob mindestens eine PDF ausgewählt ist
        has_selection = any(tile.selected for tile in self.preview_tiles)
        
        # Finde den "Ausgewählte PDF entfernen" Button in der Seitenleiste
        main_window = self.window()
        if main_window:
            # Suche nach dem Button im action_buttons_container
            for i in range(main_window.action_buttons_layout.count()):
                button = main_window.action_buttons_layout.itemAt(i).widget()
                if isinstance(button, QPushButton) and button.text() == "Ausgewählte PDF entfernen":
                    button.setEnabled(has_selection)
                    break

    def merge_pdfs(self):
        """Führt die ausgewählten PDFs zusammen."""
        if len(self.pdf_paths) < 2:
            QMessageBox.warning(self, "Fehler", "Bitte wählen Sie mindestens zwei PDF-Dateien aus.")
            return
        
        # Erstelle standardisierten Dateinamen mit aktuellem Datum
        default_filename = f"Merge_{datetime.now().strftime('%Y-%m-%d')}.pdf"
        
        # Stelle sicher, dass das export_folder existiert
        export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "export_folder")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Zusammengefügte PDF speichern")
        file_dialog.setNameFilter("PDF-Dateien (*.pdf)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("pdf")
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # Verwende PyQt Dialog
        
        # Setze Standardverzeichnis und -dateinamen
        default_path = os.path.join(export_dir, default_filename)
        file_dialog.selectFile(default_path)
        
        if file_dialog.exec_() == QFileDialog.Accepted:
            output_path = file_dialog.selectedFiles()[0]
            try:
                merge_pdfs(self.pdf_paths, output_path)
                QMessageBox.information(self, "Erfolg", "Die PDF-Dateien wurden erfolgreich zusammengefügt.")
                # Liste leeren und Vorschau aktualisieren
                self.pdf_paths = []
                self.update_preview()
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Zusammenfügen der PDF-Dateien: {str(e)}") 