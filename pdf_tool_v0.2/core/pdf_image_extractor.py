import fitz  # PyMuPDF, für die PDF-Bearbeitung
import os


class PDFImageExtractor:
    """Verantwortlich für die Extraktion von Bildern aus PDF-Dateien."""

    @staticmethod
    def extract_images(pdf_path, output_dir):
        """
        Extrahiert alle Bilder aus einem PDF und speichert sie im angegebenen Verzeichnis.

        Args:
            pdf_path (str): Pfad zur PDF-Datei.
            output_dir (str): Verzeichnis, in dem die extrahierten Bilder gespeichert werden sollen.

        Returns:
            list: Liste der Pfade zu den extrahierten Bildern.
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF-Datei nicht gefunden: {pdf_path}")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Öffne das PDF
        doc = fitz.open(pdf_path)
        image_paths = []

        for page_num, page in enumerate(doc, start=1):
            for img_index, img in enumerate(page.get_images(full=True)):
                # Hole die Bilddaten
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Erstelle den Dateinamen
                image_filename = os.path.join(output_dir, f"page_{page_num}_image_{img_index + 1}.{image_ext}")

                # Speichere das Bild
                with open(image_filename, "wb") as img_file:
                    img_file.write(image_bytes)

                image_paths.append(image_filename)

        doc.close()
        return image_paths
