#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - Utility-Modul

Sammlung von Hilfsfunktionen für die PDF-Verarbeitung und allgemeine Dateioperationen.
Stellt zentrale Funktionalitäten für die verschiedenen Komponenten des PDF Tools bereit.

Funktionen:
- PDF-Operationen (laden, speichern, rendern)
- Bildextraktion und -verarbeitung
- Dateidialoge und Pfadoperationen
- ZUGFeRD-Datenextraktion
- PDF-Konvertierung und -Manipulation

Verwendung:
    from pdf_tool.utils import load_pdf, render_page
    
    # PDF laden und Seitenanzahl erhalten
    total_pages = load_pdf('dokument.pdf')
    
    # Seite als Bild rendern
    page_image = render_page('dokument.pdf', 0)

Technische Details:
- Basiert auf PyMuPDF für PDF-Operationen
- Verwendet Qt-Dialoge für Dateioperationen
- Thread-sichere Implementierung
- Automatische Ressourcenbereinigung

Autor: Team A2-2
"""

# Importiere die PDF-Funktionen, damit sie direkt aus dem utils-Paket verfügbar sind
from .pdf_functions import (
    # PDF-Grundfunktionen
    load_pdf,           # Laden einer PDF-Datei
    render_page,        # Rendern einer PDF-Seite
    
    # Dateioperationen
    show_pdf_open_dialog,    # Dialog zum Öffnen einer PDF
    show_save_dialog,        # Dialog zum Speichern einer Datei
    show_directory_dialog,   # Dialog zur Verzeichnisauswahl
    
    # PDF-Verarbeitung
    pdf_to_word,            # PDF zu Word Konvertierung
    split_pdf_into_pages,   # PDF in Einzelseiten trennen
    merge_pdfs,            # PDFs zusammenführen
    extract_images_from_pdf, # Bilder aus PDF extrahieren
    extract_zugferd_data,   # ZUGFeRD-Daten extrahieren
    
    # Hilfsfunktionen
    clean_text,            # Text bereinigen
    create_zip_from_files  # ZIP-Archiv erstellen
)
