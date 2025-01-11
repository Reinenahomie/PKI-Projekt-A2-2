# PDF-Tool

Ein leistungsfähiges Python-Tool zur Verarbeitung und Analyse von PDF-Dokumenten.

## Funktionen

- **PDF-Verarbeitung**
  - PDF zu Word Konvertierung
  - PDF-Dateien trennen (Einzelseiten)
  - PDF-Dateien zusammenfügen
  - Strukturierte Datenextraktion (E-Rechnungen)

- **Bildverarbeitung**
  - Extraktion von Bildern aus PDF-Dokumenten
  - Vorschau der gefundenen Bilder
  - Export als Einzelbilder oder ZIP-Archiv

- **Benutzerfreundliche Oberfläche**
  - Übersichtliche Menüstruktur
  - Funktionskacheln für schnellen Zugriff
  - Detaillierte Funktionsbeschreibungen
  - Kontextabhängige Aktionsbuttons

## Installation

1. Python-Umgebung vorbereiten:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Unter Unix/macOS
   # ODER
   .venv\Scripts\activate     # Unter Windows
   ```

2. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

## Systemvoraussetzungen

- Python 3.8 oder höher
- Installierte Pakete (siehe requirements.txt):
  - PyQt5 (GUI-Framework)
  - lxml (XML-Verarbeitung)
  - PyMuPDF (PDF-Verarbeitung)
  - pdf2docx (PDF-zu-Word Konvertierung)
  - weitere Abhängigkeiten siehe requirements.txt

## Verwendung

1. Starten Sie das Tool:
   ```bash
   python run.py
   ```

2. Hauptfunktionen:
   - PDF öffnen:
     - Über den Button "Datei öffnen"
     - Über das Menü "Datei" -> "Öffnen..." (Ctrl+O)
   - Gewünschte Funktion in der linken Seitenleiste auswählen:
     - "PDF to Word": Konvertiert PDF in DOCX-Format
     - "PDF trennen": Erstellt separate PDFs für jede Seite
     - "PDF zusammenfügen": Kombiniert mehrere PDFs
     - "Bilder extrahieren": Speichert eingebettete Bilder
     - "E-Rechnung anzeigen": Zeigt strukturierte Rechnungsdaten
   - Kontextabhängige Aktionen im unteren Bereich der Seitenleiste nutzen

## Projektstruktur

```
pdf_tool/
├── run.py              # Programmstart
├── main.py            # Haupteinstiegspunkt
├── config.py          # Konfigurationsdatei
├── gui_components/    # GUI-Komponenten
│   ├── gui.py         # Hauptfenster
│   ├── home_widget.py
│   ├── pdf_preview_widget.py
│   └── weitere Komponenten
└── utils/            # Hilfsfunktionen
    └── pdf_functions.py
```

## Features im Detail

### PDF-Verarbeitung
- PDF zu Word:
  - Konvertierung mit Layout-Erhaltung
  - Unterstützung für Tabellen und Bilder
- PDF trennen:
  - Automatische Einzelseiten-Extraktion
  - Zeitstempel-basierte Ordnerstruktur
- PDF zusammenfügen:
  - Mehrere PDFs kombinieren
  - Flexible Reihenfolge-Anpassung
- E-Rechnungen:
  - Unterstützung für ZUGFeRD 1.0 und 2.0
  - Strukturierte Datenansicht

### Bildverarbeitung
- Intelligente Bilderkennung in PDFs
- Vorschau aller gefundenen Bilder
- Export-Optionen:
  - Einzelbilder speichern
  - Komprimiertes ZIP-Archiv
  - Original-Qualität und -Format

## Entwicklung

- Entwickelt von: Team A2-2 (Nahomie Reine Sigha Tagne, Delia Altewischer, Pascal Schäfer, Jörg Helkamp)

- Bearbeitungszeitraum: Nov24-Jan25

