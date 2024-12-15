import os
import fitz  # PyMuPDF
import zipfile

def load_pdf(pdf_path):
    """Lädt ein PDF und gibt die Anzahl der Seiten zurück."""
    try:
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        pdf_document.close()
        return total_pages
    except Exception as e:
        raise RuntimeError(f"Fehler beim Laden der PDF: {e}")

def render_page(pdf_path, page_number, zoom_factor=1.0):
    """Render eine bestimmte Seite mit dem angegebenen Zoom-Faktor."""
    try:
        pdf_document = fitz.open(pdf_path)
        page = pdf_document[page_number]
        matrix = fitz.Matrix(zoom_factor, zoom_factor)
        pix = page.get_pixmap(matrix=matrix)
        pdf_document.close()
        return pix
    except Exception as e:
        raise RuntimeError(f"Fehler beim Rendern der Seite {page_number}: {e}")

def split_pdf_into_pages(pdf_path, output_dir):
    """
    Nimmt den Pfad zu einer PDF entgegen und speichert jede Seite als einzelne 
    PDF in `output_dir`. Gibt eine Liste der erstellten Datei-Pfade zurück.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        page_files = []
        for page_num in range(total_pages):
            single_page_pdf = fitz.open()
            single_page_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            page_file = os.path.join(output_dir, f"page_{page_num+1}.pdf")
            single_page_pdf.save(page_file)
            single_page_pdf.close()
            page_files.append(page_file)
        pdf_document.close()
        return page_files
    except Exception as e:
        raise RuntimeError(f"Fehler beim Trennen der PDF: {e}")

def create_zip_from_files(file_list, zip_path):
    """
    Nimmt eine Liste von Dateipfaden entgegen und erstellt daraus eine ZIP-Datei 
    unter `zip_path`.
    """
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filepath in file_list:
                filename = os.path.basename(filepath)
                zipf.write(filepath, arcname=filename)
    except Exception as e:
        raise RuntimeError(f"Fehler beim Erstellen des ZIP-Archivs: {e}")
    
    import fitz  # PyMuPDF
import os

def extract_images_from_pdf(pdf_path, output_dir=None, preview_only=False):
    """
    Extrahiert Bilder aus einer PDF.

    Args:
        pdf_path (str): Pfad zur PDF-Datei.
        output_dir (str): Zielverzeichnis für extrahierte Bilder (optional).
        preview_only (bool): Wenn True, wird nur eine Vorschau des ersten Bildes erzeugt.

    Returns:
        list: Liste der Pfade zu extrahierten Bildern oder der Vorschau (falls preview_only=True).
    """
    extracted_images = []
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF-Datei nicht gefunden: {pdf_path}")

    doc = fitz.open(pdf_path)
    
    try:
        for page_num, page in enumerate(doc):
            # Alle Bilder auf der aktuellen Seite extrahieren
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Dateinamen erstellen
                image_name = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                if output_dir:
                    image_path = os.path.join(output_dir, image_name)
                else:
                    image_path = image_name

                # Bild speichern
                if not preview_only:
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                extracted_images.append(image_path)

                # Nur Vorschau: Rückgabe nach dem ersten Bild
                if preview_only:
                    with open(image_name, "wb") as img_file:
                        img_file.write(image_bytes)
                    extracted_images = [image_name]
                    return extracted_images

    finally:
        doc.close()

    return extracted_images




