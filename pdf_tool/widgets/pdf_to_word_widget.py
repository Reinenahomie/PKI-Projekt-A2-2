from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog,
    QMessageBox, QScrollArea, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QImage, QPixmap
from ..utils.pdf_functions import pdf_to_word, render_page, show_save_dialog
from pdf2docx import Converter
import os

class ConversionThread(QThread):
    """Thread für die PDF zu DOCX Konvertierung."""
    finished = pyqtSignal(bool, str)  # Status und Fehlermeldung
    timeout = 15  # Timeout in Sekunden

    def __init__(self, pdf_path, output_path):
        super().__init__()
        self.pdf_path = pdf_path
        self.output_path = output_path
        self._is_running = True
        self.cv = None

    def stop(self):
        """Stoppt den Konvertierungsprozess."""
        self._is_running = False
        if self.cv:
            try:
                self.cv.close()
            except:
                pass
        self.terminate()  # Erzwinge Beendigung des Threads

    def run(self):
        try:
            # Starte Watchdog-Timer in einem separaten Thread
            watchdog = QTimer()
            watchdog.setSingleShot(True)
            watchdog.timeout.connect(self.stop)
            watchdog.start(self.timeout * 1000)
            
            # Starte Konvertierung
            self.cv = Converter(self.pdf_path)
            if not self._is_running:  # Prüfe ob bereits abgebrochen
                raise Exception("Timeout")
                
            self.cv.convert(self.output_path)
            self.cv.close()
            
            if self._is_running:
                self.finished.emit(True, "")
            else:
                # Lösche die unvollständige Datei
                try:
                    if os.path.exists(self.output_path):
                        os.remove(self.output_path)
                except:
                    pass
                self.finished.emit(False, "Konvertierung nicht möglich: Die PDF enthält möglicherweise komplexe Vektorgrafiken oder andere nicht unterstützte Elemente.")
            
        except Exception as e:
            # Lösche die unvollständige Datei
            try:
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)
            except:
                pass
            
            if not self._is_running:
                self.finished.emit(False, "Konvertierung nicht möglich: Die PDF enthält möglicherweise komplexe Vektorgrafiken oder andere nicht unterstützte Elemente.")
            else:
                self.finished.emit(False, str(e))

class ConversionDialog(QMessageBox):
    """Dialog für die Konvertierung mit Animation."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QMessageBox.Information)
        self.setWindowTitle("Konvertierung")
        self.setText("Die PDF wird in ein Word-Dokument konvertiert")
        self.setStandardButtons(QMessageBox.NoButton)
        
        # Animation initialisieren
        self.dots = ""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(500)
        
    def update_animation(self):
        """Aktualisiert die Animations-Punkte."""
        self.dots = "." * ((len(self.dots) + 1) % 4)
        self.setText(f"Die PDF wird in ein Word-Dokument konvertiert{self.dots}")
        
    def conversion_finished(self, success, error_msg=None):
        """Zeigt die Erfolgsmeldung oder Fehlermeldung an."""
        self.timer.stop()
        if success:
            self.setIcon(QMessageBox.Information)
            self.setText("Die PDF wurde erfolgreich in ein DOCX-Dokument konvertiert.")
        else:
            self.setIcon(QMessageBox.Critical)
            self.setText(f"Die PDF konnte nicht konvertiert werden:\n{error_msg}")
        self.setStandardButtons(QMessageBox.Ok)

class PDFToWordWidget(QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.conversion_thread = None
        
        # Layout erstellen
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 0, 20, 20)  # Seitliche Ränder auf 20px
        layout.setSpacing(10)

        # Container für die Vorschau
        preview_container = QWidget()
        preview_container.setMinimumSize(400, 600)  # Angepasste Mindestgröße für Hochformat
        preview_container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(0)  # Kein Abstand zwischen Elementen

        # Scroll-Bereich für die Vorschau
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setContentsMargins(0, 0, 0, 0)  # Keine Ränder
        
        # Vorschaubereich
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        scroll_area.setWidget(self.preview_label)
        preview_layout.addWidget(scroll_area)
        
        layout.addWidget(preview_container, 1)  # 1 gibt dem Container die Priorität beim Dehnen

        self.setLayout(layout)

    def showEvent(self, event):
        """Wird aufgerufen, wenn das Widget angezeigt wird."""
        super().showEvent(event)
        # Hole die aktuelle PDF vom Hauptfenster
        main_window = self.window()
        pdf_path = main_window.get_current_pdf()
        
        if pdf_path:
            self.show_preview(pdf_path)
        else:
            self.preview_label.clear()
            self.preview_label.setText("Keine PDF-Datei geöffnet")

    def show_preview(self, pdf_path):
        """Zeigt eine Vorschau der ersten Seite der PDF."""
        try:
            # Rendere die erste Seite
            pix = render_page(pdf_path, 0, 1.0)
            
            # Berechne den optimalen Zoom-Faktor
            visible_width = self.preview_label.parent().width() - 40
            visible_height = self.preview_label.parent().height() - 40
            width_ratio = visible_width / pix.width
            height_ratio = visible_height / pix.height
            zoom = min(width_ratio, height_ratio)
            
            # Rendere mit optimalem Zoom
            pix = render_page(pdf_path, 0, zoom)
            
            # Konvertiere zu QPixmap und zeige an
            img_data = pix.tobytes("ppm")
            qimg = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(qimg)
            self.preview_label.setPixmap(pixmap)
            
        except Exception as e:
            self.preview_label.clear()
            self.preview_label.setText(f"Fehler beim Laden der Vorschau:\n{str(e)}")

    def convert_to_word(self):
        """Konvertiert die aktuelle PDF in ein Word-Dokument."""
        # Hole die aktuelle PDF-Datei vom Hauptfenster
        main_window = self.window()
        pdf_path = main_window.get_current_pdf()
        
        if not pdf_path:
            QMessageBox.warning(
                self,
                "Keine PDF geöffnet",
                "Bitte öffnen Sie zuerst eine PDF-Datei."
            )
            return

        # Bestimme den Ausgabepfad mit dem einheitlichen Dialog
        default_name = os.path.basename(pdf_path).rsplit('.', 1)[0] + '.docx'
        output_path = show_save_dialog(
            self,
            "Word-Dokument speichern",
            default_name,
            ("Word Dateien", "*.docx"),
            use_export_dir=True  # Verwende den Export-Ordner als Standard
        )
        
        if output_path:
            try:
                # Zeige Konvertierungsdialog
                self.progress_dialog = ConversionDialog(self)
                self.progress_dialog.show()
                QApplication.processEvents()
                
                # Erstelle und starte den Konvertierungs-Thread
                self.conversion_thread = ConversionThread(pdf_path, output_path)
                self.conversion_thread.finished.connect(self.conversion_finished)
                self.conversion_thread.start()
                
            except Exception as e:
                if hasattr(self, 'progress_dialog'):
                    self.progress_dialog.conversion_finished(False, str(e))

    def conversion_finished(self, success, error_msg):
        """Wird aufgerufen, wenn die Konvertierung abgeschlossen ist."""
        self.progress_dialog.conversion_finished(success, error_msg)
        self.conversion_thread = None 