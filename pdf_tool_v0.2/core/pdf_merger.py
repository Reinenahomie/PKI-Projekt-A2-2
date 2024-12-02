import fitz  # PyMuPDF, für die PDF-Bearbeitung
import os


class PDFMerger:
    """Verantwortlich für das Zusammenfügen von PDFs."""

    @staticmethod
    def merge_pdfs(input_paths, output_path):
        """
        Fügt mehrere PDFs zu einer einzigen PDF-Datei zusammen.

        Args:
            input_paths (list of str): Liste der Pfade zu den PDF-Dateien, die zusammengeführt werden sollen.
            output_path (str): Pfad zur Ausgabedatei.

        Returns:
            bool: True, wenn das Zusammenfügen erfolgreich war.

        Raises:
            FileNotFoundError: Wenn eine der Eingabedateien nicht existiert.
            ValueError: Wenn die Liste der Eingabedateien leer ist.
        """
        if not input_paths:
            raise ValueError("Die Liste der Eingabedateien ist leer.")

        # Überprüfen, ob alle Eingabedateien existieren
        for path in input_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Datei nicht gefunden: {path}")

        # Neues PDF-Dokument erstellen
        merged_pdf = fitz.open()

        # Eingabedateien durchlaufen und Seiten hinzufügen
        for path in input_paths:
            pdf = fitz.open(path)
            merged_pdf.insert_pdf(pdf)
            pdf.close()

        # Ausgabedatei speichern
        merged_pdf.save(output_path)
        merged_pdf.close()
        return True
