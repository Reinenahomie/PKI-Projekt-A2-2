#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - PDF Funktionen

Implementiert grundlegende Funktionen für die Verarbeitung von PDF-Dokumenten.
Diese Funktionen werden von den verschiedenen Widgets des PDF Tools verwendet
und bieten eine einheitliche Schnittstelle für PDF-Operationen.

Funktionen:
- PDF Laden und Rendern
- Dateidialoge und Benutzerinteraktion
- PDF Konvertierung (Word, Einzelseiten)
- Bildextraktion und -verarbeitung
- ZUGFeRD Datenextraktion
- Hilfsfunktionen für Text und Dateien

Technische Details:
- Basiert auf PyMuPDF (fitz) für PDF-Verarbeitung
- Verwendet pdf2docx für Word-Konvertierung
- Integriert Qt-Dialoge für Benutzerinteraktion
- Optimierte Speicher- und Ressourcenverwaltung
- Fehlerbehandlung und Logging

Verwendung:
    # PDF laden und rendern
    pages = load_pdf('dokument.pdf')
    image = render_page('dokument.pdf', 0, 1.0)
    
    # PDF konvertieren
    pdf_to_word('dokument.pdf', 'ausgabe.docx')
    
    # Bilder extrahieren
    images = extract_images_from_pdf('dokument.pdf', 'bilder/')
    
    # ZUGFeRD Daten lesen
    xml_data = extract_zugferd_data('rechnung.pdf')

Autor: Team A2-2
"""

import os
import fitz  # PyMuPDF
import zipfile
from docx import Document
from PyQt5.QtWidgets import (
    QFileDialog, QPushButton, QLabel, QLineEdit, QComboBox, 
    QDialogButtonBox, QBoxLayout
)
from PyQt5.QtCore import Qt
from pdf2docx import Converter
from ..config import SAMPLE_PDF_DIR, EXPORT_DIR

def load_pdf(pdf_path):
    """
    Lädt ein PDF-Dokument und gibt die Anzahl der Seiten zurück.
    
    Diese Funktion öffnet eine PDF-Datei, ermittelt die Gesamtzahl der Seiten
    und schließt das Dokument wieder. Sie ist nützlich für die initiale
    Analyse einer PDF-Datei.
    
    Args:
        pdf_path (str): Pfad zur PDF-Datei
        
    Returns:
        int: Anzahl der Seiten im PDF-Dokument
        
    Raises:
        RuntimeError: Wenn die PDF nicht geladen werden kann
    """
    try:
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        pdf_document.close()
        return total_pages
    except Exception as e:
        raise RuntimeError(f"Fehler beim Laden der PDF: {e}")

def render_page(pdf_path, page_number, zoom_factor=1.0):
    """
    Rendert eine bestimmte Seite einer PDF mit angegebenem Zoom-Faktor.
    
    Diese Funktion öffnet die PDF, rendert die gewünschte Seite und erstellt
    ein Pixmap-Objekt, das für die Anzeige verwendet werden kann. Der
    Zoom-Faktor ermöglicht die Skalierung der Ausgabe.
    
    Args:
        pdf_path (str): Pfad zur PDF-Datei
        page_number (int): Nummer der zu rendernden Seite (0-basiert)
        zoom_factor (float): Zoom-Faktor für die Darstellung (Standard: 1.0)
        
    Returns:
        fitz.Pixmap: Das gerenderte Seitenbild
        
    Raises:
        RuntimeError: Wenn die Seite nicht gerendert werden kann
    """
    try:
        pdf_document = fitz.open(pdf_path)
        page = pdf_document[page_number]
        # Erstelle die Transformationsmatrix mit dem Zoom-Faktor
        matrix = fitz.Matrix(zoom_factor, zoom_factor)
        pix = page.get_pixmap(matrix=matrix)
        pdf_document.close()
        return pix
    except Exception as e:
        raise RuntimeError(f"Fehler beim Rendern der Seite {page_number}: {e}")

def show_pdf_open_dialog(parent, title="PDF auswählen"):
    """
    Zeigt einen einheitlichen Dialog zum Öffnen von PDF-Dateien.
    
    Implementiert einen benutzerfreundlichen Dateiauswahldialog mit deutschen
    Beschriftungen und standardisierten Einstellungen. Der Dialog startet im
    konfigurierten Beispiel-PDF-Verzeichnis.
    
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
    
    # Setze das Standardverzeichnis auf 'sample_pdf'
    if os.path.exists(SAMPLE_PDF_DIR):
        dialog.setDirectory(SAMPLE_PDF_DIR)
    
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

def clean_text(text):
    """
    Bereinigt Text von nicht-XML-kompatiblen Zeichen.
    
    Diese Funktion entfernt problematische Zeichen aus einem Text, behält aber
    wichtige Formatierungszeichen wie Zeilenumbrüche bei. Sie wird hauptsächlich
    für die Verarbeitung von XML-Daten verwendet.
    
    Args:
        text (str): Der zu bereinigende Text
        
    Returns:
        str: Bereinigter Text, sicher für XML-Verarbeitung
    """
    # Entferne NULL-Bytes und Steuerzeichen, behalte aber Zeilenumbrüche und Tabulatoren
    return ''.join(char for char in text if char in '\n\t\r' or (ord(char) >= 32 and ord(char) != 127))

def pdf_to_word(pdf_path, output_dir):
    """
    Konvertiert eine PDF-Datei in ein Word-Dokument.
    
    Verwendet die pdf2docx-Bibliothek für eine hochwertige Konvertierung, die
    Layout, Formatierung und eingebettete Elemente bestmöglich erhält. Die
    Funktion ist optimiert für komplexe PDF-Dokumente.
    
    Args:
        pdf_path (str): Pfad zur PDF-Datei
        output_dir (str): Pfad für das Word-Dokument
        
    Raises:
        RuntimeError: Wenn die Konvertierung fehlschlägt
    """
    try:
        # Konvertiere PDF zu Word mit pdf2docx
        cv = Converter(pdf_path)
        cv.convert(output_dir)
        cv.close()
    except Exception as e:
        raise RuntimeError(f"Fehler beim Umwandeln der PDF: {str(e)}")

def split_pdf_into_pages(pdf_path, output_dir):
    """
    Teilt eine PDF-Datei in einzelne Seiten auf.
    
    Erstellt für jede Seite der PDF eine separate PDF-Datei in einem
    Zeitstempel-Verzeichnis. Die Funktion behält die Qualität der
    ursprünglichen PDF bei.
    
    Args:
        pdf_path (str): Pfad zur PDF-Datei
        output_dir (str): Basisverzeichnis für die Ausgabe
        
    Returns:
        list: Liste der Pfade zu den erstellten Einzelseiten-PDFs
        
    Raises:
        RuntimeError: Wenn die Aufteilung fehlschlägt
    """
    try:
        # Erstelle Zeitstempel-Verzeichnis
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_subdir = os.path.join(output_dir, timestamp)
        os.makedirs(output_subdir, exist_ok=True)
        
        pdf_document = fitz.open(pdf_path)
        total_pages = len(pdf_document)
        page_files = []
        
        for page_num in range(total_pages):
            single_page_pdf = fitz.open()
            single_page_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            page_file = os.path.join(output_subdir, f"page_{page_num+1}.pdf")
            single_page_pdf.save(page_file)
            single_page_pdf.close()
            page_files.append(page_file)
            
        pdf_document.close()
        return page_files
        
    except Exception as e:
        raise RuntimeError(f"Fehler beim Trennen der PDF: {e}")

def create_zip_from_files(file_list, zip_path):
    """
    Erstellt ein ZIP-Archiv aus einer Liste von Dateien.
    
    Komprimiert die angegebenen Dateien in ein ZIP-Archiv und verwendet dabei
    den Dateinamen ohne Pfad als Archivnamen. Die Funktion ist optimiert für
    die Verarbeitung von PDF- und Bilddateien.
    
    Args:
        file_list (list): Liste der zu archivierenden Dateipfade
        zip_path (str): Pfad für das ZIP-Archiv
        
    Raises:
        RuntimeError: Wenn die ZIP-Erstellung fehlschlägt
    """
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filepath in file_list:
                filename = os.path.basename(filepath)
                zipf.write(filepath, arcname=filename)
    except Exception as e:
        raise RuntimeError(f"Fehler beim Erstellen des ZIP-Archivs: {e}")

def extract_images_from_pdf(pdf_path, output_dir=None, preview_only=False):
    """
    Extrahiert Bilder aus einer PDF-Datei.
    
    Identifiziert und extrahiert alle eingebetteten Bilder aus der PDF.
    Die Bilder werden mit aussagekräftigen Namen versehen und optional
    nur als Vorschau erstellt.
    
    Args:
        pdf_path (str): Pfad zur PDF-Datei
        output_dir (str, optional): Zielverzeichnis für die Bilder
        preview_only (bool): Wenn True, werden nur temporäre Vorschaubilder erstellt
        
    Returns:
        list: Liste der Pfade zu den extrahierten Bildern
        
    Raises:
        RuntimeError: Wenn die Bildextraktion fehlschlägt
    """
    extracted_images = []
    
    # Erstelle pdf_tool/temp Verzeichnis falls es nicht existiert
    base_temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pdf_tool", "temp")
    if not os.path.exists(base_temp_dir):
        os.makedirs(base_temp_dir)
    
    # Setze temp_preview als Unterverzeichnis von pdf_tool/temp
    temp_dir = os.path.join(base_temp_dir, "temp_preview") if preview_only else output_dir
    
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

def extract_zugferd_data(pdf_path):
    """
    Extrahiert ZUGFeRD XML-Daten aus einer PDF/A-3 Datei.
    
    Durchsucht die PDF nach eingebetteten XML-Dateien und extrahiert die
    ZUGFeRD-Daten. Die Funktion unterstützt sowohl ZUGFeRD 1.0 als auch 2.0
    und validiert die gefundenen XML-Daten.
    
    Args:
        pdf_path (str): Pfad zur PDF-Datei
        
    Returns:
        tuple: (xml_string, parsed_data_dict) oder (None, None) wenn keine
               ZUGFeRD-Daten gefunden wurden
        
    Raises:
        RuntimeError: Wenn die Datenextraktion fehlschlägt
    """
    doc = None
    try:
        doc = fitz.open(pdf_path)
        
        if doc.embfile_count() == 0:
            print("Keine eingebetteten Dateien gefunden")
            return None, None
            
        xml_found = False
        for i in range(doc.embfile_count()):
            try:
                embfile_info = doc.embfile_info(i)
                if not embfile_info:
                    continue
                    
                filename = embfile_info.get("filename", "")
                if not filename or not filename.lower().endswith(".xml"):
                    continue
                    
                xml_data = doc.embfile_get(i)
                if not xml_data:
                    continue
                    
                xml_string = xml_data.decode('utf-8')
                if not xml_string:
                    continue
                    
                xml_found = True
                
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_string)
                
                # ZUGFeRD-Version ermitteln
                version = "1.0"  # Standard-Version
                ns = {}
                
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
                    continue
                
                def safe_find_multiple(xpaths_by_version):
                    """Sucht nach Version-spezifischen XPaths"""
                    xpaths = xpaths_by_version.get(version, xpaths_by_version["1.0"])
                    for xpath in xpaths:
                        try:
                            element = root.find(xpath, ns)
                            if element is not None and element.text:
                                return element.text
                        except Exception as e:
                            print(f"Fehler beim XPath {xpath}: {e}")
                            continue
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
                        "1.0": [
                            './/ram:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString',
                            './/ram:IssueDateTime/udt:DateTimeString'
                        ],
                        "2.0": [
                            './/rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString',
                            './/ram:IssueDateTime/udt:DateTimeString'
                        ]
                    }),
                    'Gesamtbetrag': safe_find_multiple({
                        "1.0": [
                            './/ram:GrandTotalAmount',
                            './/ram:TotalAmount'
                        ],
                        "2.0": [
                            './/ram:GrandTotalAmount',
                            './/ram:TotalAmount'
                        ]
                    }),
                    'Währung': safe_find_multiple({
                        "1.0": [
                            './/ram:GrandTotalAmount/@currencyID',
                            './/ram:TotalAmount/@currencyID'
                        ],
                        "2.0": [
                            './/ram:GrandTotalAmount/@currencyID',
                            './/ram:TotalAmount/@currencyID'
                        ]
                    })
                }
                
                return xml_string, parsed_data
                
            except Exception as e:
                print(f"Fehler bei der Verarbeitung der eingebetteten Datei {i}: {e}")
                continue
                
        if not xml_found:
            print("Keine ZUGFeRD XML-Datei gefunden")
            
        return None, None
        
    except Exception as e:
        print(f"Fehler beim Extrahieren der ZUGFeRD-Daten: {e}")
        return None, None
        
    finally:
        if doc:
            try:
                doc.close()
            except:
                pass

def merge_pdfs(pdf_paths, output_path):
    """
    Fügt mehrere PDF-Dateien zu einem Dokument zusammen.
    
    Kombiniert die angegebenen PDF-Dateien in der gegebenen Reihenfolge zu
    einer einzigen PDF-Datei. Die Funktion behält die Qualität der
    ursprünglichen PDFs bei.
    
    Args:
        pdf_paths (list): Liste der Pfade zu den PDF-Dateien
        output_path (str): Pfad für die zusammengefügte PDF
        
    Raises:
        RuntimeError: Wenn das Zusammenfügen fehlschlägt
    """
    try:
        merged_pdf = fitz.open()
        for pdf_path in pdf_paths:
            with fitz.open(pdf_path) as pdf:
                merged_pdf.insert_pdf(pdf)
        merged_pdf.save(output_path)
        merged_pdf.close()
    except Exception as e:
        raise RuntimeError(f"Fehler beim Zusammenfügen der PDFs: {e}") 

def show_save_dialog(parent, title="Speicherort auswählen", default_name=None, file_type=None, use_export_dir=False):
    """
    Zeigt einen einheitlichen Dialog zum Speichern von Dateien.
    
    Implementiert einen benutzerfreundlichen Speicherdialog mit deutschen
    Beschriftungen und standardisierten Einstellungen. Optional kann das
    konfigurierte Export-Verzeichnis als Startverzeichnis verwendet werden.
    
    Args:
        parent: Das übergeordnete Widget (für Modal-Dialog)
        title (str): Titel des Dialogs
        default_name (str): Standardname für die zu speichernde Datei
        file_type (tuple): Tuple mit (Beschreibung, Endung), z.B. ("Word Dateien", "*.docx")
        use_export_dir (bool): Wenn True, wird das Export-Verzeichnis als Standard verwendet
    
    Returns:
        str: Pfad zum gewählten Speicherort oder None, wenn abgebrochen
    """
    dialog = QFileDialog(parent)
    dialog.setWindowTitle(title)
    
    # Setze das Standardverzeichnis
    if use_export_dir and os.path.exists(EXPORT_DIR):
        if default_name:
            dialog.selectFile(os.path.join(EXPORT_DIR, default_name))
        else:
            dialog.setDirectory(EXPORT_DIR)
    elif default_name:
        dialog.selectFile(default_name)
        
    if file_type:
        dialog.setNameFilter(f"{file_type[0]} ({file_type[1]})")
    
    # Deutsche Beschriftungen für die Standardbuttons
    dialog.setLabelText(QFileDialog.FileName, "Name:")
    dialog.setLabelText(QFileDialog.Accept, "Speichern")
    dialog.setLabelText(QFileDialog.Reject, "Abbrechen")
    dialog.setLabelText(QFileDialog.FileType, "Dateityp:")
    dialog.setLabelText(QFileDialog.LookIn, "Speichern in:")
    
    # Zusätzliche deutsche Beschriftungen
    dialog.setOption(QFileDialog.DontUseNativeDialog)
    new_folder_button = dialog.findChild(QPushButton, "newFolderButton")
    if new_folder_button:
        new_folder_button.setText("Neuer Ordner")
    
    if dialog.exec_() == QFileDialog.Accepted:
        return dialog.selectedFiles()[0]
    return None

def show_directory_dialog(parent, title="Ordner auswählen", use_export_dir=False):
    """
    Zeigt einen vereinfachten Dialog zur Ordnerauswahl.
    
    Implementiert einen benutzerfreundlichen Verzeichnisauswahldialog mit
    deutschen Beschriftungen und minimaler Benutzeroberfläche. Optional kann
    das Export-Verzeichnis als Startverzeichnis verwendet werden.
    
    Args:
        parent: Das übergeordnete Widget (für Modal-Dialog)
        title (str): Titel des Dialogs
        use_export_dir (bool): Ob das Export-Verzeichnis verwendet werden soll
        
    Returns:
        str: Pfad zum gewählten Ordner oder None, wenn abgebrochen
    """
    dialog = QFileDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.ShowDirsOnly, True)
    dialog.setOption(QFileDialog.DontUseNativeDialog, True)
    
    # Setze das Standardverzeichnis
    if use_export_dir and os.path.exists(EXPORT_DIR):
        dialog.setDirectory(EXPORT_DIR)
    
    # Deutsche Beschriftungen für die Standardbuttons
    dialog.setLabelText(QFileDialog.Accept, "Ordner auswählen")
    dialog.setLabelText(QFileDialog.Reject, "Abbrechen")
    dialog.setLabelText(QFileDialog.LookIn, "Suchen in:")
    
    # Verstecke nicht benötigte Elemente
    dialog.setOption(QFileDialog.DontUseCustomDirectoryIcons, True)
    
    # Finde und verstecke die nicht benötigten Widgets
    filename_label = dialog.findChild(QLabel, "fileNameLabel")
    if filename_label:
        filename_label.hide()
    
    filename_edit = dialog.findChild(QLineEdit, "fileNameEdit")
    if filename_edit:
        filename_edit.hide()
    
    filetype_label = dialog.findChild(QLabel, "fileTypeLabel")
    if filetype_label:
        filetype_label.hide()
    
    filetype_combo = dialog.findChild(QComboBox, "fileTypeCombo")
    if filetype_combo:
        filetype_combo.hide()
    
    # Neuer Ordner Button auf Deutsch
    new_folder_button = dialog.findChild(QPushButton, "newFolderButton")
    if new_folder_button:
        new_folder_button.setText("Neuer Ordner")
    
    # Finde die Buttons und ändere ihre Reihenfolge
    button_box = dialog.findChild(QDialogButtonBox)
    if button_box:
        # Entferne die alten Buttons
        for button in button_box.buttons():
            button_box.removeButton(button)
        
        # Erstelle neue Buttons und füge sie hinzu
        button_box.addButton(QDialogButtonBox.Cancel).setText("Abbrechen")
        button_box.addButton(QDialogButtonBox.Ok).setText("Ordner auswählen")
    
    if dialog.exec_() == QFileDialog.Accepted:
        return dialog.selectedFiles()[0]
    return None 