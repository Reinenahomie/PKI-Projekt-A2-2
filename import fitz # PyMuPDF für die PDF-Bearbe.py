import fitz  # PyMuPDF für die PDF-Bearbeitung
import os

def extract_text_from_pdf(pdf_path, output_path=None):
    """
    Extrahiert den Text aus einer PDF-Datei und speichert ihn optional in einer Textdatei.

    Args:
        pdf_path (str): Der Pfad zur PDF-Datei, aus der der Text extrahiert werden soll.
        output_path (str, optional): Der Pfad, unter dem der extrahierte Text gespeichert werden soll.
                                      Wenn None, wird der Text nur zurückgegeben, aber nicht gespeichert.

    Returns:
        str: Der extrahierte Text.
    """
    # Überprüfen, ob die Datei existiert
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF-Datei nicht gefunden: {pdf_path}")

    # Öffne die PDF-Datei mit PyMuPDF
    doc = fitz.open(pdf_path)
    text = ""

    # Durch alle Seiten iterieren und Text extrahieren
    for page in doc:
        text += page.get_text()

    doc.close()

    # Überprüfen, ob Text extrahiert wurde
    if not text.strip():
        raise ValueError("Kein Text in der PDF gefunden.")

    # Speichern des extrahierten Texts, falls ein Ausgabe-Pfad angegeben ist
    if output_path:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Text wurde erfolgreich in {output_path} gespeichert.")
    else:
        print("Text wurde erfolgreich extrahiert.")

    return text

def main():
    # Eingabepfad der PDF-Datei
    pdf_path = input("Gib den Pfad zur PDF-Datei ein: ")

    # Optionaler Ausgabepfad für die Textdatei
    output_path = input("Gib den Pfad zum Speichern der Textdatei ein (oder drücke Enter, um den Text nur anzuzeigen): ")

    # Text extrahieren und ggf. speichern
    try:
        extracted_text = extract_text_from_pdf(pdf_path, output_path if output_path else None)
        print("\nExtrahierter Text:\n")
        print(extracted_text[:1000])  # Zeige die ersten 1000 Zeichen des extrahierten Textes an
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    main()





    ### Abfrage aktueller Pfad

    import os
print("Aktuelles Arbeitsverzeichnis:", os.getcwd())