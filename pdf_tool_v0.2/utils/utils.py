import os


class Utils:
    """Hilfsfunktionen für die PDF-Anwendung."""

    @staticmethod
    def ensure_directory_exists(directory):
        """
        Erstellt das Verzeichnis, falls es nicht existiert.

        Args:
            directory (str): Pfad zum Verzeichnis.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def get_unique_filename(directory, base_name, extension):
        """
        Generiert einen eindeutigen Dateinamen, falls eine Datei mit dem gleichen Namen existiert.

        Args:
            directory (str): Verzeichnis, in dem die Datei gespeichert wird.
            base_name (str): Basisname der Datei.
            extension (str): Dateierweiterung (z. B. ".txt" oder ".png").

        Returns:
            str: Ein eindeutiger Dateiname im Format "base_name_1.extension".
        """
        file_path = os.path.join(directory, f"{base_name}{extension}")
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(directory, f"{base_name}_{counter}{extension}")
            counter += 1
        return file_path

    @staticmethod
    def calculate_scaling(widget_width, widget_height, pdf_width, pdf_height):
        """
        Berechnet den Skalierungsfaktor für das Rendern eines PDFs, um das Seitenverhältnis beizubehalten.

        Args:
            widget_width (int): Breite des Widgets.
            widget_height (int): Höhe des Widgets.
            pdf_width (float): Breite der PDF-Seite.
            pdf_height (float): Höhe der PDF-Seite.

        Returns:
            float: Der Skalierungsfaktor.
        """
        scale_x = widget_width / pdf_width
        scale_y = widget_height / pdf_height
        return min(scale_x, scale_y)

    @staticmethod
    def human_readable_size(size_in_bytes):
        """
        Konvertiert eine Dateigröße in Bytes in ein lesbares Format (z. B. KB, MB, GB).

        Args:
            size_in_bytes (int): Dateigröße in Bytes.

        Returns:
            str: Lesbare Größe (z. B. "10.5 MB").
        """
        for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024
