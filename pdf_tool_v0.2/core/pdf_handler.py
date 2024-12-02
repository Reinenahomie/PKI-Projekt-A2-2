import fitz  # PyMuPDF, für die PDF-Bearbeitung
import os


class PDFHandler:
    """Verantwortlich für grundlegende PDF-Operationen."""

    def __init__(self):
        """Initialisiert den PDF-Handler."""
        self.current_pdf = None  # Geöffnete PDF-Datei
        self.file_path = None  # Pfad zur geöffneten PDF-Datei
        self.total_pages = 0  # Gesamtanzahl der Seiten im PDF
        self.current_page_index = 0  # Index der aktuell angezeigten Seite


    def open_pdf(self, file_path):
        """Öffnet ein PDF und lädt grundlegende Informationen.

        Args:
            file_path (str): Pfad zur PDF-Datei.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Datei nicht gefunden: {file_path}")
        
        self.current_pdf = fitz.open(file_path)
        self.file_path = file_path
        self.total_pages = len(self.current_pdf)

    def extract_text(self, output_path=None):
        """Extrahiert den gesamten Text aus dem PDF.

        Args:
            output_path (str): Pfad, um den extrahierten Text zu speichern (optional).

        Returns:
            str: Der extrahierte Text.
        """
        if not self.current_pdf:
            raise ValueError("Kein PDF geöffnet. Bitte zuerst ein PDF laden.")

        text = ""
        for page in self.current_pdf:
            text += page.get_text()

        if output_path:
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(text)

        return text

    def extract_images(self, output_dir):
        """Extrahiert alle Bilder aus dem PDF und speichert sie.

        Args:
            output_dir (str): Verzeichnis, in dem die Bilder gespeichert werden.

        Returns:
            list: Liste der Pfade zu den extrahierten Bildern.
        """
        if not self.current_pdf:
            raise ValueError("Kein PDF geöffnet. Bitte zuerst ein PDF laden.")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        image_paths = []
        for page_num, page in enumerate(self.current_pdf, start=1):
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = self.current_pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = os.path.join(output_dir, f"page_{page_num}_image_{img_index + 1}.{image_ext}")
                with open(image_filename, "wb") as img_file:
                    img_file.write(image_bytes)
                image_paths.append(image_filename)

        return image_paths

    def rotate_page(self, page_number, angle):
        """Dreht eine bestimmte Seite im PDF.

        Args:
            page_number (int): Nummer der zu drehenden Seite (1-basiert).
            angle (int): Winkel, um den die Seite gedreht wird (z. B. 90, 180).

        Returns:
            bool: True, wenn die Seite erfolgreich gedreht wurde.
        """
        if not self.current_pdf:
            raise ValueError("Kein PDF geöffnet. Bitte zuerst ein PDF laden.")

        if page_number < 1 or page_number > self.total_pages:
            raise ValueError(f"Ungültige Seitenzahl: {page_number}")

        page = self.current_pdf[page_number - 1]
        page.set_rotation(angle)
        return True

    def add_pdf(self, other_pdf_path, output_path):
        """Hängt ein weiteres PDF an die aktuelle Datei an und speichert das Ergebnis.

        Args:
            other_pdf_path (str): Pfad zur PDF-Datei, die angehängt werden soll.
            output_path (str): Pfad zur Ausgabedatei.

        Returns:
            bool: True, wenn das Zusammenfügen erfolgreich war.
        """
        if not self.current_pdf:
            raise ValueError("Kein PDF geöffnet. Bitte zuerst ein PDF laden.")

        if not os.path.exists(other_pdf_path):
            raise FileNotFoundError(f"Datei nicht gefunden: {other_pdf_path}")

        # Öffne die zweite PDF-Datei
        other_pdf = fitz.open(other_pdf_path)

        # Kopiere Seiten aus der zweiten PDF in die aktuelle PDF
        for page in other_pdf:
            self.current_pdf.insert_pdf(other_pdf)

        # Speichere das Ergebnis
        self.current_pdf.save(output_path)
        other_pdf.close()
        return True

    def close_pdf(self):
        """Schließt das aktuell geöffnete PDF."""
        if self.current_pdf:
            self.current_pdf.close()
            self.current_pdf = None
            self.file_path = None
            self.total_pages = 0
