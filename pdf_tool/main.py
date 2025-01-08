# Importiere die notwendigen PyQt5-Komponenten für die GUI-Anwendung
from PyQt5.QtWidgets import QApplication
# Importiere das Hauptfenster aus dem lokalen gui-Modul
from .gui import MainWindow
# Importiere das sys-Modul für Systemfunktionen und Programmbeendigung
import sys

def main():
    """
    Hauptfunktion der Anwendung.
    
    Diese Funktion initialisiert die GUI-Anwendung und startet die Ereignisschleife.
    Sie führt folgende Schritte aus:
    1. Erstellt eine neue QApplication-Instanz
    2. Erstellt und zeigt das Hauptfenster
    3. Startet die Ereignisschleife und beendet die Anwendung ordnungsgemäß
    """
    # Erstelle eine neue QApplication-Instanz
    # sys.argv ermöglicht die Übergabe von Kommandozeilenargumenten
    app = QApplication(sys.argv)
    
    # Erstelle eine Instanz des Hauptfensters
    window = MainWindow()
    
    # Zeige das Hauptfenster an
    window.show()
    
    # Starte die Ereignisschleife und beende die Anwendung ordnungsgemäß
    # app.exec_() startet die Hauptschleife
    # sys.exit() stellt sicher, dass die Anwendung mit dem korrekten Status beendet wird
    sys.exit(app.exec_())

# Wenn diese Datei direkt ausgeführt wird (nicht importiert),
# starte die Hauptfunktion
if __name__ == "__main__":
    main()
