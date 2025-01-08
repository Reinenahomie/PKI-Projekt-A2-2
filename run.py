# Importiere die Hauptfunktion aus dem pdf_tool Paket
from pdf_tool.main import main

# Dies ist der Einstiegspunkt des Programms
# Die if-Bedingung stellt sicher, dass der Code nur ausgeführt wird,
# wenn die Datei direkt gestartet wird (z.B. mit 'python run.py')
# und nicht, wenn sie als Modul importiert wird
if __name__ == "__main__":
    main()  # Startet die Hauptanwendung

