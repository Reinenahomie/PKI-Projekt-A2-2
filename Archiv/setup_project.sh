#!/bin/bash

# Projektname
PROJECT_NAME="pdf_team_project"

# Verzeichnisstruktur
DIRECTORIES=(
    "$PROJECT_NAME"
    "$PROJECT_NAME/gui"
    "$PROJECT_NAME/core"
)

# Dateien, die erstellt werden sollen
FILES=(
    "$PROJECT_NAME/main.py"
    "$PROJECT_NAME/gui/__init__.py"
    "$PROJECT_NAME/gui/main_window.py"
    "$PROJECT_NAME/gui/pdf_preview.py"
    "$PROJECT_NAME/gui/navigation_buttons.py"
    "$PROJECT_NAME/gui/action_buttons.py"
    "$PROJECT_NAME/core/__init__.py"
    "$PROJECT_NAME/core/pdf_handler.py"
    "$PROJECT_NAME/core/utils.py"
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
    cat <<EOL > "$PROJECT_NAME/.gitignore"
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

echo "Verzeichnisstruktur für $PROJECT_NAME erstellt!"

