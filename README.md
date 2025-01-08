# PDF Tool

Ein Tool zur Bearbeitung von PDF-Dateien mit verschiedenen Funktionen.

## Features

- PDF zu Word Konvertierung
- Bilder aus PDF extrahieren
- PDFs zusammenfügen
- PDF Vorschau mit Zoom-Funktion
- PDF in Einzelseiten trennen
- ZUGFeRD Rechnungen lesen (Version 1.0 und 2.0)

## Installation

1. **Virtuelle Umgebung erstellen**
   ```bash
   python -m venv .venv
   ```

2. **Virtuelle Umgebung aktivieren**
   - Windows:
     ```bash
     .\.venv\Scripts\Activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

3. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

## Verwendung

Starten Sie das Tool mit:
```bash
python run.py
```

## Projektstruktur

```
pdf_tool/
├── widgets/                    # GUI-Widgets
│   ├── home_widget.py         # Startseite
│   ├── pdf_preview_widget.py  # PDF-Vorschau
│   ├── pdf_split_widget.py    # PDF-Trennung
│   ├── pdf_merge_widget.py    # PDF-Zusammenführung
│   ├── pdf_to_word_widget.py  # PDF zu Word
│   └── zugferd_reader_widget.py # ZUGFeRD-Leser
├── utils/
│   └── pdf_functions.py       # PDF-Verarbeitungsfunktionen
├── config.py                  # Konfigurationsdatei
├── gui.py                     # Hauptfenster
└── main.py                    # Programmstart
```

## Entwicklung

- Python 3.8+
- PyQt5 für die GUI
- PyMuPDF (fitz) für PDF-Verarbeitung
- pdf2docx für PDF zu Word Konvertierung

## Lizenz

[Ihre Lizenz hier]
