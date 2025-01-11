#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - GUI-Komponenten

Sammlung spezialisierter GUI-Komponenten für die verschiedenen PDF-Operationen.
Jede Komponente ist für eine spezifische Funktion optimiert und bietet eine
benutzerfreundliche Oberfläche.

Komponenten-Übersicht:
- HomeWidget: Startseite mit Willkommenstext
- PDFPreviewWidget: PDF-Vorschau und Navigation
- PDFSplitWidget: Trennen von PDFs in Einzelseiten
- PDFMergeWidget: Zusammenführen mehrerer PDFs
- PDFToWordWidget: Konvertierung nach Word
- PDFImageExtractorWidget: Extraktion von Bildern
- EInvoiceReaderWidget: Anzeige von ZUGFeRD-Daten

Technische Details:
- Basiert auf PyQt5-Widgets
- Einheitliches Design und Verhalten
- Responsive Layouts
- Threadsichere Implementierung

Autor: Team A2-2
"""

from .home_widget import HomeWidget
from .pdf_preview_widget import PDFPreviewWidget
from .pdf_split_widget import PDFSplitWidget
from .pdf_merge_widget import PDFMergeWidget
from .pdf_to_word_widget import PDFToWordWidget
from .pdf_image_extractor_widget import PDFImageExtractorWidget
from .zugferd_reader_widget import EInvoiceReaderWidget

__all__ = [
    'HomeWidget',              # Startseite
    'PDFPreviewWidget',        # PDF-Vorschau
    'PDFSplitWidget',         # PDF-Trennung
    'PDFMergeWidget',         # PDF-Zusammenführung
    'PDFToWordWidget',        # PDF zu Word
    'PDFImageExtractorWidget', # Bildextraktion
    'EInvoiceReaderWidget'    # ZUGFeRD-Anzeige
]
