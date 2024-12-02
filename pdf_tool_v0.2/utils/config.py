class Config:
    """Globale Konfigurationseinstellungen für die PDF-Anwendung."""

    # Allgemeine Einstellungen
    APP_NAME = "PDF Team Project"
    APP_VERSION = "0.2"
    DEFAULT_OUTPUT_DIR = "./output"  # Standard-Ausgabeverzeichnis

    # PDF-Einstellungen
    DEFAULT_DPI = 150  # Standard-DPI für PDF-Rendering
    IMAGE_QUALITY = 90  # Qualitätsstufe für exportierte Bilder (0-100)

    # Debug-Einstellungen
    DEBUG_MODE = True  # Aktiviert Debugging (True/False)

    @staticmethod
    def log_debug(message):
        """Protokolliert Debug-Nachrichten, wenn der Debug-Modus aktiv ist."""
        if Config.DEBUG_MODE:
            print(f"[DEBUG] {message}")
