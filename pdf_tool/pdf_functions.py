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



