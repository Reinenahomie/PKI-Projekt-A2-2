import os

# Basis-Pfad zum Projektverzeichnis
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Pfad zum Startbild relativ zum Projektverzeichnis
HOME_IMAGE_PATH = os.path.join(BASE_DIR, 'pictures', 'start.png')

# Pfad zum Beispiel-PDF-Verzeichnis
SAMPLE_PDF_DIR = os.path.join(BASE_DIR, 'sample_pdf')

# Pfad zum Export-Verzeichnis
EXPORT_DIR = os.path.join(BASE_DIR, 'export_folder')
