import fitz  # PyMuPDF, für die PDF-Bearbeitung
import os


class PDFRotator:
    """Verantwortlich für das Drehen von Seiten in PDF-Dokumenten."""

    @staticmethod
    def rotate_pages(pdf_path, output_path, rotations):
        """
        Dreht Seiten eines PDFs um bestimmte Winkel.

        Args:
            pdf_path (str): Pfad zur PDF-Datei.
            output_path (str): Pfad zur Ausgabedatei.
            rotations (dict): Ein Dictionary, das die Seiten und die Rotationswinkel angibt.
                Beispiel: {1: 90, 2: -90} (Dreht Seite 1 um 90° und Seite 2 um -90°).

        Returns:
            bool: True, wenn das Drehen erfolgreich war.

        Raises:
            FileNotFoundError: Wenn die Eingabedatei nicht existiert.
            ValueError: Wenn das Dictionary `rotations` leer ist oder ungültige Seiten enthält.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF-Datei nicht gefunden: {pdf_path}")

        if not rotations:
            raise ValueError("Das Rotations-Dictionary ist leer.")

        # Öffne das PDF
        doc = fitz.open(pdf_path)

        for page_number, angle in rotations.items():
            if page_number < 1 or page_number > len(doc):
                raise ValueError(f"Ungültige Seite: {page_number}")
            page = doc[page_number - 1]
            page.set_rotation(angle)

        # Speichere das gedrehte PDF
        doc.save(output_path)
        doc.close()
        return True
