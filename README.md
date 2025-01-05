# PDF Tool

Ein einfaches PDF-Tool mit einer grafischen Oberfläche (PyQt5) und Funktionen zur PDF-Bearbeitung (PyMuPDF).

## Installation

```bash
pip install -r requirements.txt

## So starten Sie die Anwendung

Befolgen Sie diese Schritte, um die Anwendung im Terminal einzurichten und zu starten:

1. **Erstellen Sie eine virtuelle Umgebung**  
   Öffnen Sie Ihr Terminal und erstellen Sie eine virtuelle Umgebung mit dem folgenden Befehl:
   ```bash
   python -m venv .venv
   ```

2. **Aktivieren Sie die virtuelle Umgebung**  
   Aktivieren Sie die virtuelle Umgebung mit dem folgenden Befehl:
   - Unter Windows:
     ```bash
     .\.venv\Scripts\Activate
     ```
   - Unter macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

3. **Installieren Sie die Abhängigkeiten**  
   Installieren Sie die erforderlichen Abhängigkeiten aus der Datei `requirements.txt` mit folgendem Befehl:
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional) Installieren Sie zusätzliche Pakete**  
   Obwohl dies normalerweise nicht notwendig ist, können Sie `PyQt5` und `PyMuPDF` explizit installieren:
   ```bash
   .venv\Scripts\python.exe -m pip install pyQt5 pyMuPDF
   ```

5. **Starten Sie die Anwendung**  
   Führen Sie die Anwendung mit dem folgenden Befehl aus:
   ```bash
   python run.py
   ```

### Hinweise
- Stellen Sie sicher, dass Sie sich im Stammverzeichnis Ihres Projekts befinden, bevor Sie diese Befehle ausführen.
- Die virtuelle Umgebung hilft dabei, Ihre Abhängigkeiten von der globalen Python-Installation zu isolieren.
