import os
import fitz  # PyMuPDF
import zipfile
from PyQt5.QtWidgets import QFileDialog, QPushButton

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
        pdf_path (str): Pfad zur PDF-Datei
        output_dir (str, optional): Zielverzeichnis für extrahierte Bilder
        preview_only (bool): Wenn True, werden temporäre Vorschaubilder erstellt

    Returns:
        list: Liste der Pfade zu extrahierten Bildern
    """
    extracted_images = []
    temp_dir = "temp_preview" if preview_only else output_dir
    
    if preview_only and not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    try:
        doc = fitz.open(pdf_path)
        
        # Zähle zuerst die Gesamtanzahl der Bilder
        total_images = sum(len(page.get_images(full=True)) for page in doc)
        current_image = 0
        
        for page_num, page in enumerate(doc):
            page_images = page.get_images(full=True)
            for img_index, img in enumerate(page_images):
                current_image += 1
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Neues Benennungsschema
                image_name = f"Bild_{current_image:02d}_von_{total_images:02d}_(S._{page_num + 1:02d}).{image_ext}"
                image_path = os.path.join(temp_dir, image_name)
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                extracted_images.append(image_path)
                
        doc.close()
        return extracted_images
        
    except Exception as e:
        raise RuntimeError(f"Fehler beim Extrahieren der Bilder: {e}")
    finally:
        if preview_only:
            import atexit
            import shutil
            atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))

def show_pdf_open_dialog(parent, title="PDF auswählen"):
    """
    Zeigt einen einheitlichen Dialog zum Öffnen von PDF-Dateien.
    
    Args:
        parent: Das übergeordnete Widget (für Modal-Dialog)
        title (str): Titel des Dialogs, Standard ist "PDF auswählen"
    
    Returns:
        str: Pfad zur ausgewählten PDF-Datei oder None, wenn abgebrochen
    """
    dialog = QFileDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setNameFilter("PDF Dateien (*.pdf)")
    dialog.setFileMode(QFileDialog.ExistingFile)
    
    # Deutsche Beschriftungen für die Standardbuttons
    dialog.setLabelText(QFileDialog.FileName, "Name:")
    dialog.setLabelText(QFileDialog.Accept, "Öffnen")
    dialog.setLabelText(QFileDialog.Reject, "Abbrechen")
    dialog.setLabelText(QFileDialog.FileType, "Dateityp:")
    dialog.setLabelText(QFileDialog.LookIn, "Suchen in:")
    
    # Zusätzliche deutsche Beschriftungen
    dialog.setOption(QFileDialog.DontUseNativeDialog)
    new_folder_button = dialog.findChild(QPushButton, "newFolderButton")
    if new_folder_button:
        new_folder_button.setText("Neuer Ordner")

    if dialog.exec_() == QFileDialog.Accepted:
        selected_files = dialog.selectedFiles()
        if selected_files:
            return selected_files[0]
    return None

def extract_zugferd_data(pdf_path):
    """
    Extrahiert ZUGFeRD XML-Daten aus einer PDF/A-3 Datei.
    
    Args:
        pdf_path (str): Pfad zur PDF-Datei

    Returns:
        tuple: (xml_string, parsed_data_dict)
    """
    try:
        doc = fitz.open(pdf_path)
        
        for i in range(doc.embfile_count()):
            embfile_info = doc.embfile_info(i)
            filename = embfile_info["filename"]
            
            if filename.lower().endswith(".xml"):
                xml_data = doc.embfile_get(i)
                xml_string = xml_data.decode('utf-8')
                
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_string)
                
                # ZUGFeRD-Version ermitteln
                version = "1.0"  # Standard-Version
                try:
                    # Für ZUGFeRD 2.0
                    if "CrossIndustryInvoice:100" in xml_string:
                        version = "2.0"
                        ns = {
                            'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
                            'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
                            'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100',
                            'qdt': 'urn:un:unece:uncefact:data:standard:QualifiedDataType:100'
                        }
                    # Für ZUGFeRD 1.0
                    else:
                        ns = {
                            'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:12',
                            'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:15'
                        }
                    print(f"Erkannte ZUGFeRD-Version: {version}")
                except Exception as e:
                    print(f"Fehler bei der Versionserkennung: {e}")
                
                def safe_find_multiple(xpaths_by_version):
                    """Sucht nach Version-spezifischen XPaths"""
                    xpaths = xpaths_by_version.get(version, xpaths_by_version["1.0"])
                    for xpath in xpaths:
                        element = root.find(xpath, ns)
                        if element is not None and element.text:
                            return element.text
                    return "Nicht verfügbar"
                
                parsed_data = {
                    'Rechnungsnummer': safe_find_multiple({
                        "1.0": [
                            './/ram:ExchangedDocument/ram:ID',  # ZUGFeRD 1.0 Pfad
                            './/ram:InvoiceNumber'  # Alternativer Pfad
                        ],
                        "2.0": [
                            './/rsm:ExchangedDocument/ram:ID',  # ZUGFeRD 2.0 Pfad
                            './/ram:InvoiceNumber',
                            './/ram:ID'
                        ]
                    }),
                    'Datum': safe_find_multiple({
                        "1.0": ['.//ram:IssueDateTime/udt:DateTimeString'],
                        "2.0": ['.//ram:IssueDateTime/udt:DateTimeString', './/ram:FormattedIssueDateTime']
                    }),
                    'Gesamtbetrag': safe_find_multiple({
                        "1.0": ['.//ram:GrandTotalAmount'],
                        "2.0": ['.//ram:GrandTotalAmount', './/ram:DuePayableAmount']
                    }),
                    'Währung': safe_find_multiple({
                        "1.0": ['.//ram:InvoiceCurrencyCode'],
                        "2.0": ['.//ram:InvoiceCurrencyCode', './/ram:CurrencyCode']
                    }),
                    'Verkäufer': safe_find_multiple({
                        "1.0": ['.//ram:SellerTradeParty/ram:Name', './/ram:Seller'],
                        "2.0": ['.//ram:SellerTradeParty/ram:Name', './/ram:Seller']
                    }),
                    'Käufer': safe_find_multiple({
                        "1.0": ['.//ram:BuyerTradeParty/ram:Name', './/ram:Buyer'],
                        "2.0": ['.//ram:BuyerTradeParty/ram:Name', './/ram:Buyer']
                    }),
                    'Nettobetrag': safe_find_multiple({
                        "1.0": ['.//ram:LineTotalAmount'],
                        "2.0": ['.//ram:LineTotalAmount', './/ram:NetAmount']
                    }),
                    'Steuerbetrag': safe_find_multiple({
                        "1.0": ['.//ram:TaxTotalAmount'],
                        "2.0": ['.//ram:TaxTotalAmount', './/ram:TaxAmount']
                    }),
                    'Zahlungsbedingungen': safe_find_multiple({
                        "1.0": ['.//ram:PaymentTerms/ram:Description'],
                        "2.0": ['.//ram:PaymentTerms/ram:Description', './/ram:PaymentTerms']
                    }),
                    'Leistungsdatum': safe_find_multiple({
                        "1.0": ['.//ram:ActualDeliverySupplyChainEvent/ram:OccurrenceDateTime/udt:DateTimeString'],
                        "2.0": ['.//ram:ActualDeliverySupplyChainEvent/ram:OccurrenceDateTime/udt:DateTimeString', './/ram:ActualDeliverySupplyChainEvent/ram:OccurrenceDateTime']
                    })
                }
                
                return xml_string, parsed_data
                
        raise ValueError("Keine ZUGFeRD XML-Datei gefunden")
        
    except Exception as e:
        raise RuntimeError(f"Fehler beim Extrahieren der ZUGFeRD-Daten: {e}")
    finally:
        doc.close()


def merge_pdfs(pdf_files, output_path):
    """
    Fügt eine Liste von PDF-Dateien zu einer einzigen Datei zusammen.
    
    Args:
        pdf_files (list): Liste der Pfade zu den PDF-Dateien
        output_path (str): Pfad zur Ausgabedatei
    """
    try:
        pdf_document = fitz.open()
        for pdf_file in pdf_files:
            pdf_document.insert_pdf(fitz.open(pdf_file))
        pdf_document.save(output_path)
        pdf_document.close()
    except Exception as e:
        raise RuntimeError(f"Fehler beim Zusammenführen der PDFs: {e}")

