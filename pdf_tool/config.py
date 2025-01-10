#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - Konfigurationsmodul

Zentrale Konfigurationseinstellungen für das PDF Tool.
Definiert wichtige Konstanten und Einstellungen, die im gesamten Programm
verwendet werden.

Konfigurationsbereiche:
- Dateipfade und Verzeichnisse
- GUI-Einstellungen (Fenstergrößen, Schriftarten)
- PDF-Verarbeitungsoptionen
- Temporäre Dateien und Caching

Verwendung:
    from pdf_tool.config import BASE_DIR, HOME_IMAGE_PATH
    
    # Pfad zum Startbild
    image_path = HOME_IMAGE_PATH
    
    # Pfad zum Export-Verzeichnis
    export_path = os.path.join(EXPORT_DIR, 'output.pdf')

Autor: Team A2-2
"""

import os

# Basis-Pfad zum Projektverzeichnis
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Pfad zum Startbild relativ zum Projektverzeichnis
HOME_IMAGE_PATH = os.path.join(BASE_DIR, 'pictures', 'start.png')

# Pfad zum Beispiel-PDF-Verzeichnis
SAMPLE_PDF_DIR = os.path.join(BASE_DIR, 'sample_pdf')

# Pfad zum Export-Verzeichnis
EXPORT_DIR = os.path.join(BASE_DIR, 'export_folder')
