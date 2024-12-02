import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Startet die PDF-Anwendung."""
    # Erstelle die QApplication-Instanz
    app = QApplication(sys.argv)

    # Initialisiere das Hauptfenster
    main_window = MainWindow()
    main_window.show()

    # Startet die Haupt-Event-Schleife
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
