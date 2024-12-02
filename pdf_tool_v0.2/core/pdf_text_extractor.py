import fitz  # PyMuPDF, für die PDF-Bearbeitung
import os


class PDFTextExtractor:
    """Verantwortlich für die Extraktion von Text aus PDF-Dateien."""

    @staticmethod
    def extract_text(pdf_path, output_path=None):
        """
        Extrahiert den gesamten Text aus einer PDF-Datei.

        Args:
            pdf_path (str): Pfad zur PDF-Datei.
            output_path (str, optional): Pfad, um den extrahierten Text zu speichern. Wenn None, wird der Text nur zurückgegeben.

        Returns:
            str: Der extrahierte Text.

        Raises:
            FileNotFoundError: Wenn die Eingabedatei nicht existiert.
            ValueError: Wenn die PDF-Datei leer ist oder keinen Text enthält.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF-Datei nicht gefunden: {pdf_path}")

        # Öffne das PDF
        doc = fitz.open(pdf_path)
        text = ""

        # Iteriere durch alle Seiten und extrahiere Text
        for page in doc:
            text += page.get_text()

        doc.close()

        # Prüfe, ob Text extrahiert wurde
        if not text.strip():
            raise ValueError("Kein Text im PDF gefunden.")

        # Speichere den Text, falls ein Ausgabe-Pfad angegeben ist
        if output_path:
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(text)

        return text
