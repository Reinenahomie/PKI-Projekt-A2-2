import fitz  # PyMuPDF
from docx import Document

def pdf_to_word(pdf_path, word_output_path):
    """
    Diese Funktion extrahiert den Text aus einer PDF und speichert ihn in einem Word-Dokument.
    
    :param pdf_path: Der Pfad zur PDF-Datei.
    :param word_output_path: Der Pfad, unter dem das Word-Dokument gespeichert werden soll.
    """
    try:
        # Öffne die PDF mit PyMuPDF
        pdf_document = fitz.open(pdf_path)
        
        # Erstelle ein neues Word-Dokument
        doc = Document()
        
        # Gehe alle Seiten der PDF durch und extrahiere den Text
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)  # Seite laden
            text = page.get_text()  # Text der Seite extrahieren
            
            # Füge den extrahierten Text zum Word-Dokument hinzu
            doc.add_paragraph(text)
        
        # Speichere das Word-Dokument
        doc.save(word_output_path)
        
        print(f"Das PDF wurde erfolgreich in ein Word-Dokument umgewandelt: {word_output_path}")
    
    except Exception as e:
        print(f"Fehler beim Umwandeln der PDF: {str(e)}")

# Beispiel-Aufruf
pdf_path = "C:\\Users\\Delia\\OneDrive - NEXWORLD\\Desktop\\Delia\\Studium Ki\\Test.pdf"
word_output_path = "C:\\Users\\Delia\\OneDrive - NEXWORLD\\Desktop\\Delia\\Studium Ki\\Test.docx"  # Pfad zum Speichern des Word-Dokuments
pdf_to_word(pdf_path, word_output_path)