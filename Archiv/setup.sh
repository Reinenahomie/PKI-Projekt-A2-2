#!/bin/bash

# Projektverzeichnis
PROJECT_DIR="pdf_tool_v0.2"

# Verzeichnisstruktur
DIRECTORIES=(
    "$PROJECT_DIR"
    "$PROJECT_DIR/gui"
    "$PROJECT_DIR/core"
    "$PROJECT_DIR/utils"
)

# Dateien, die erstellt werden sollen
FILES=(
    "$PROJECT_DIR/main.py"
    "$PROJECT_DIR/gui/__init__.py"
    "$PROJECT_DIR/gui/main_window.py"
    "$PROJECT_DIR/gui/pdf_viewer.py"
    "$PROJECT_DIR/gui/action_buttons.py"
    "$PROJECT_DIR/gui/navigation_bar.py"
    "$PROJECT_DIR/core/__init__.py"
    "$PROJECT_DIR/core/pdf_handler.py"
    "$PROJECT_DIR/core/pdf_text_extractor.py"
    "$PROJECT_DIR/core/pdf_image_extractor.py"
    "$PROJECT_DIR/core/pdf_rotator.py"
    "$PROJECT_DIR/core/pdf_merger.py"
    "$PROJECT_DIR/utils/__init__.py"
    "$PROJECT_DIR/utils/utils.py"
    "$PROJECT_DIR/utils/config.py"
)

# Funktion: Verzeichnisse erstellen
create_directories() {
    echo "Erstelle Verzeichnisse..."
    for dir in "${DIRECTORIES[@]}"; do
        mkdir -p "$dir"
        echo "Verzeichnis erstellt: $dir"
    done
}

# Funktion: Dateien erstellen
create_files() {
    echo "Erstelle Dateien..."
    for file in "${FILES[@]}"; do
        touch "$file"
        echo "Datei erstellt: $file"
    done
}

# Funktion: .gitignore erstellen
create_gitignore() {
    echo "Erstelle .gitignore..."
    cat <<EOL > "$PROJECT_DIR/.gitignore"
# Virtuelle Umgebung
.venv/

# Python-spezifisch
__pycache__/
*.pyc
*.pyo

# Temporäre Dateien
*.log
temp_preview.png
EOL
    echo ".gitignore erstellt."
}

# Ausführung
create_directories
create_files
create_gitignore

echo "Verzeichnisstruktur für $PROJECT_DIR erstellt!"

