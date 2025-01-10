#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF Tool - ZUGFeRD Reader Widget

Implementiert die Funktionalität zum Lesen und Anzeigen von ZUGFeRD-Daten aus
PDF-Rechnungen. Das Widget unterstützt sowohl ZUGFeRD 1.0 als auch 2.0 und
stellt die extrahierten Daten in einer übersichtlichen Baumstruktur dar.

Funktionen:
- Automatische Erkennung der ZUGFeRD-Version (1.0/2.0)
- Extraktion aller Rechnungsdaten
- Strukturierte Darstellung in Baumform
- Detailansicht für einzelne Datenpunkte
- Export der Daten in verschiedene Formate

Layout:
- Vertikales Hauptlayout
- Baumansicht für ZUGFeRD-Daten
- Detailbereich für ausgewählte Elemente
- Statusbereich für Meldungen

Technische Details:
- Basiert auf QWidget und lxml
- XML-Parsing und Validierung
- Unterstützung mehrerer ZUGFeRD-Versionen
- Fehlerbehandlung und Benutzer-Feedback

Verwendung:
    reader = ZUGFeRDReaderWidget()
    reader.show()
    
    # Daten laden
    reader.load_zugferd_data()
    
    # Version prüfen
    version = reader.get_zugferd_version()
    print(f"ZUGFeRD Version: {version}")

Autor: Team A2-2
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTreeWidget, QTreeWidgetItem, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QListWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ..utils.pdf_functions import extract_zugferd_data
import xml.etree.ElementTree as ET

class EInvoiceReaderWidget(QWidget):
    """
    Widget zur Anzeige und Verarbeitung von PDF-Rechnungsdaten.
    
    Diese Klasse implementiert die Hauptfunktionalität zum Anzeigen und Verarbeiten
    von strukturierten Rechnungsdaten aus PDF-Dateien. Sie unterstützt verschiedene
    Versionen des Rechnungsformats und stellt die Daten sowohl in einer Baumstruktur
    als auch in aufbereiteter Form dar.
    
    Die Klasse bietet:
    - Automatische Versionserkennung
    - XML-Strukturansicht
    - Aufbereitete Datenanzeige
    - Fehlerbehandlung
    """
    
    def __init__(self, stacked_widget, parent=None):
        """
        Initialisiert das Widget und erstellt die Benutzeroberfläche.
        
        Erstellt ein zweigeteiltes Layout mit einer Baumansicht für die XML-Struktur
        und einer Liste für die aufbereiteten Daten. Beide Bereiche werden in einem
        grauen Container zusammengefasst.
        
        Args:
            stacked_widget: Übergeordnetes StackedWidget für die Navigation
            parent: Optionales Eltern-Widget
        """
        super().__init__(parent)                           # Initialisiere die Basisklasse
        self.stacked_widget = stacked_widget               # Speichere Referenz auf übergeordnetes Widget
        
        # Hauptlayout
        layout = QVBoxLayout()                            # Erstelle vertikales Layout für Hauptbereich
        layout.setContentsMargins(20, 0, 20, 20)          # Setze Außenabstände des Layouts
        layout.setSpacing(20)                             # Setze Abstand zwischen Layout-Elementen
        
        # Container für den grauen Bereich
        container = QWidget()                             # Erstelle Container für grauen Bereich
        container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)                                              # Setze grauen Hintergrund für Container
        container_layout = QVBoxLayout(container)         # Erstelle vertikales Layout für Container
        container_layout.setContentsMargins(20, 20, 20, 20)  # Setze Innenabstände des Containers
        container_layout.setSpacing(15)                   # Setze Abstand zwischen Container-Elementen
        
        # Label für XML-Struktur
        xml_label = QLabel("XML-Struktur der PDF-Rechnungsdaten:")  # Erstelle Überschrift für XML-Bereich
        xml_label.setStyleSheet("font-weight: bold;")     # Setze Schrift auf fett
        container_layout.addWidget(xml_label)             # Füge Label zum Container hinzu
        
        # XML-Baum
        self.xml_tree = QTreeWidget()                     # Erstelle Baumansicht für XML-Daten
        self.xml_tree.setHeaderLabels(["Element", "Wert"])  # Setze Spaltenüberschriften
        self.xml_tree.setColumnCount(2)                   # Lege zwei Spalten fest
        self.xml_tree.setAlternatingRowColors(True)       # Aktiviere abwechselnde Zeilenfarben
        self.xml_tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #cccccc;
            }
            QTreeWidget::item {
                padding: 2px;
            }
        """)                                              # Setze Styling für Baumansicht
        
        # Spaltenbreiten anpassen
        header = self.xml_tree.header()                   # Hole Referenz auf Tabellenkopf
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Erste Spalte interaktiv anpassbar
        header.setSectionResizeMode(1, QHeaderView.Interactive)  # Zweite Spalte interaktiv anpassbar
        self.xml_tree.setColumnWidth(0, self.width() // 2)  # Setze initiale Spaltenbreite auf 50%
        
        container_layout.addWidget(self.xml_tree)         # Füge Baumansicht zum Container hinzu

        # Label für ausgewertete Daten
        data_label = QLabel("Ausgewertete Rechnungsdaten:")  # Erstelle Überschrift für Datenbereich
        data_label.setStyleSheet("font-weight: bold;")    # Setze Schrift auf fett
        container_layout.addWidget(data_label)            # Füge Label zum Container hinzu
        
        # Daten-Liste
        self.data_list = QListWidget()                    # Erstelle Liste für aufbereitete Daten
        self.data_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #cccccc;
            }
        """)                                              # Setze Styling für Datenliste
        container_layout.addWidget(self.data_list)        # Füge Liste zum Container hinzu
        
        layout.addWidget(container)                       # Füge Container zum Hauptlayout hinzu
        self.setLayout(layout)                            # Setze Hauptlayout für Widget

    def resizeEvent(self, event):
        """
        Behandelt Größenänderungen des Widgets.
        
        Passt die Spaltenbreiten der Baumansicht dynamisch an die neue Größe an,
        um eine optimale Darstellung zu gewährleisten.
        
        Args:
            event: QResizeEvent mit den Details zur Größenänderung
        """
        super().resizeEvent(event)                        # Rufe Basis-Implementation auf
        if hasattr(self, 'xml_tree'):                     # Prüfe ob Baumansicht existiert
            self.xml_tree.setColumnWidth(0, self.xml_tree.width() // 2)  # Passe Spaltenbreite an

    def _add_xml_element(self, element, parent_item=None):
        """
        Fügt XML-Elemente rekursiv zur Baumstruktur hinzu.
        
        Verarbeitet ein XML-Element und seine Unterelemente, entfernt Namespaces
        für bessere Lesbarkeit und fügt Attribute als Unterelemente hinzu.
        
        Args:
            element: XML-Element das hinzugefügt werden soll
            parent_item: Optionales Elternelement in der Baumstruktur
            
        Returns:
            QTreeWidgetItem: Das erstellte Baumelement
        """
        tag = element.tag.split('}')[-1]                  # Entferne Namespace aus Element-Name
        text = element.text.strip() if element.text and element.text.strip() else ""  # Bereinige Text
        
        if parent_item is None:                           # Wenn kein Elternelement vorhanden
            item = QTreeWidgetItem(self.xml_tree)         # Erstelle Wurzelelement
        else:                                             # Wenn Elternelement vorhanden
            item = QTreeWidgetItem(parent_item)           # Erstelle Kind-Element
            
        item.setText(0, tag)                              # Setze Element-Name
        if text:                                          # Wenn Text vorhanden
            item.setText(1, text)                         # Setze Element-Text
        
        for name, value in element.attrib.items():        # Für jedes Attribut
            attr_item = QTreeWidgetItem(item)             # Erstelle neues Element für Attribut
            attr_item.setText(0, f"@{name}")              # Setze Attribut-Name
            attr_item.setText(1, value)                   # Setze Attribut-Wert
        
        for child in element:                             # Für jedes Kind-Element
            self._add_xml_element(child, item)            # Füge Kind-Element rekursiv hinzu
            
        return item                                       # Gebe erstelltes Element zurück

    def showEvent(self, event):
        """
        Wird beim Anzeigen des Widgets aufgerufen.
        
        Lädt die aktuelle PDF-Datei, extrahiert die Rechnungsdaten und zeigt diese
        in der Baumstruktur und der Datenliste an. Behandelt verschiedene Fehlerfälle
        und zeigt entsprechende Meldungen an.
        
        Args:
            event: QShowEvent mit Details zum Anzeigeereignis
        """
        super().showEvent(event)                          # Rufe Basis-Implementation auf
        main_window = self.window()                       # Hole Referenz auf Hauptfenster
        pdf_path = main_window.get_current_pdf()          # Hole Pfad der aktuellen PDF
        
        self.xml_tree.clear()                            # Lösche alte XML-Daten
        self.data_list.clear()                           # Lösche alte Listendaten
        
        if not pdf_path:                                 # Wenn keine PDF geöffnet
            root_item = QTreeWidgetItem(self.xml_tree)   # Erstelle Wurzelelement
            root_item.setText(0, "Keine PDF-Datei geöffnet")  # Setze Hinweistext
            self.data_list.addItem("Keine PDF-Datei geöffnet")  # Füge Hinweis zur Liste hinzu
            return
            
        try:
            result = extract_zugferd_data(pdf_path)      # Extrahiere Rechnungsdaten aus PDF
            if not result or len(result) != 2:           # Prüfe ob Daten gefunden wurden
                root_item = QTreeWidgetItem(self.xml_tree)  # Erstelle Wurzelelement
                root_item.setText(0, "Keine PDF-Rechnungsdaten gefunden")  # Setze Fehlertext
                self.data_list.addItem("Keine PDF-Rechnungsdaten gefunden")  # Füge Fehler zur Liste hinzu
                return
                
            xml_data, parsed_data = result               # Extrahiere XML und geparste Daten
            if not xml_data or not parsed_data:          # Prüfe ob Daten gültig sind
                root_item = QTreeWidgetItem(self.xml_tree)  # Erstelle Wurzelelement
                root_item.setText(0, "Keine gültigen PDF-Rechnungsdaten gefunden")  # Setze Fehlertext
                self.data_list.addItem("Keine gültigen PDF-Rechnungsdaten gefunden")  # Füge Fehler zur Liste hinzu
                return
                
            root = ET.fromstring(xml_data)              # Parse XML-Daten
            self._add_xml_element(root)                 # Füge XML-Struktur zum Baum hinzu
            self.xml_tree.expandAll()                   # Expandiere alle Baumeinträge
            self._add_invoice_data(root)                # Füge aufbereitete Daten zur Liste hinzu
            
        except Exception as e:                          # Bei Fehlern während der Verarbeitung
            root_item = QTreeWidgetItem(self.xml_tree)  # Erstelle Wurzelelement
            error_msg = f"Fehler beim Lesen der PDF-Rechnungsdaten: {str(e)}"  # Erstelle Fehlermeldung
            root_item.setText(0, error_msg)             # Setze Fehlermeldung im Baum
            self.data_list.addItem(error_msg)           # Füge Fehlermeldung zur Liste hinzu

    def _add_invoice_data(self, root):
        """
        Extrahiert und verarbeitet die Rechnungsdaten.
        
        Diese zentrale Methode verarbeitet die XML-Daten einer PDF-Rechnung.
        Sie unterstützt verschiedene Versionen des Rechnungsformats durch
        eine einheitliche Verarbeitungslogik mit versionsspezifischen
        Konfigurationen.
        
        Die Methode extrahiert folgende Daten:
        - Allgemeine Rechnungsinformationen (Nummer, Datum, Typ)
        - Verkäuferinformationen inkl. Adresse und Kontakt
        - Käuferinformationen inkl. Adresse
        - Zahlungsinformationen (IBAN, BIC)
        - Betragsangaben (Netto, Steuer, Gesamt)
        
        Args:
            root: XML-Root-Element mit den Rechnungsdaten
        """
        version = self._detect_zugferd_version(root)    # Ermittle die Version der Rechnungsdaten
        
        # Definiere die Namespace-Konfigurationen für beide Versionen
        NAMESPACES = {
            "2.0": {                                    # Namespaces für Version 2.0
                'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
                'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
                'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100'
            },
            "1.0": {                                    # Namespaces für Version 1.0
                'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:12',
                'rsm': 'urn:ferd:CrossIndustryDocument:invoice:1p0:comfort',
                'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:15'
            }
        }                                               # Ende der Namespace-Definitionen
        
        # Definiere die XPath-Ausdrücke für beide Versionen
        XPATH_PATHS = {
            "2.0": {                                    # XPath-Definitionen für Version 2.0
                # Pfade für allgemeine Informationen
                "invoice_number": './/rsm:ExchangedDocument/ram:ID',  # Pfad zur Rechnungsnummer
                "issue_date": './/rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString',  # Pfad zum Rechnungsdatum
                "invoice_type": './/rsm:ExchangedDocument/ram:TypeCode',  # Pfad zum Rechnungstyp
                # Pfade für Verkäuferinformationen
                "seller": './/ram:SellerTradeParty',    # Pfad zum Verkäufer-Element
                "seller_address": './/ram:PostalTradeAddress',  # Pfad zur Verkäufer-Adresse
                "seller_contact": './/ram:URIUniversalCommunication',  # Pfad zu Verkäufer-Kontaktdaten
                "seller_tax": './/ram:SpecifiedTaxRegistration/ram:ID',  # Pfad zur Steuernummer
                # Pfade für Käuferinformationen
                "buyer": './/ram:BuyerTradeParty',      # Pfad zum Käufer-Element
                "buyer_address": './/ram:PostalTradeAddress',  # Pfad zur Käufer-Adresse
                # Pfade für Zahlungsinformationen
                "payment": './/ram:SpecifiedTradeSettlementPaymentMeans',  # Pfad zu Zahlungsinformationen
                "payment_account": './/ram:PayeePartyCreditorFinancialAccount',  # Pfad zu Kontodaten
                # Pfade für Betragsangaben
                "monetary": './/ram:SpecifiedTradeSettlementMonetarySummation',  # Pfad zu Beträgen
                "amount_net": 'ram:LineTotalAmount',    # Pfad zum Nettobetrag
                "amount_tax": 'ram:TaxTotalAmount',     # Pfad zum Steuerbetrag
                "amount_total": 'ram:GrandTotalAmount'  # Pfad zum Gesamtbetrag
            },
            "1.0": {                                    # XPath-Definitionen für Version 1.0
                # Pfade für allgemeine Informationen
                "invoice_number": './/rsm:HeaderExchangedDocument/ram:ID',  # Pfad zur Rechnungsnummer
                "issue_date": './/ram:IssueDateTime/udt:DateTimeString',  # Pfad zum Rechnungsdatum
                "invoice_type": './/ram:TypeCode',      # Pfad zum Rechnungstyp
                # Pfade für Verkäuferinformationen
                "seller": './/ram:SellerTradeParty',    # Pfad zum Verkäufer-Element
                "seller_address": './/ram:PostalTradeAddress',  # Pfad zur Verkäufer-Adresse
                "seller_contact": './/ram:EmailURIUniversalCommunication',  # Pfad zu Verkäufer-Kontaktdaten
                "seller_tax": './/ram:SpecifiedTaxRegistration/ram:ID',  # Pfad zur Steuernummer
                # Pfade für Käuferinformationen
                "buyer": './/ram:BuyerTradeParty',      # Pfad zum Käufer-Element
                "buyer_address": './/ram:PostalTradeAddress',  # Pfad zur Käufer-Adresse
                # Pfade für Zahlungsinformationen
                "payment": './/ram:SpecifiedTradeSettlementPaymentMeans',  # Pfad zu Zahlungsinformationen
                "payment_account": './/ram:PayeePartyCreditorFinancialAccount',  # Pfad zu Kontodaten
                # Pfade für Betragsangaben
                "monetary": './/ram:SpecifiedTradeSettlementHeaderMonetarySummation',  # Pfad zu Beträgen
                "amount_net": 'ram:LineTotalAmount',    # Pfad zum Nettobetrag
                "amount_tax": 'ram:TaxBasisTotalAmount',  # Pfad zum Steuerbetrag
                "amount_total": 'ram:GrandTotalAmount'  # Pfad zum Gesamtbetrag
            }
        }                                               # Ende der XPath-Definitionen
        
        try:
            nsmap = NAMESPACES.get(version, NAMESPACES["1.0"])  # Wähle die passenden Namespaces für die Version
            paths = XPATH_PATHS.get(version, XPATH_PATHS["1.0"])  # Wähle die passenden XPath-Pfade für die Version
            
            self.data_list.addItem(f"=== PDF-Rechnungsversion {version} ===\n")  # Zeige die erkannte Version an
            
            # Extrahiere und zeige allgemeine Informationen
            self.data_list.addItem("=== Allgemeine Informationen ===")  # Überschrift für allgemeine Daten
            self._extract_element(root, paths["invoice_number"], nsmap, "Rechnungsnummer")  # Extrahiere Rechnungsnummer
            self._extract_element(root, paths["issue_date"], nsmap, "Rechnungsdatum")  # Extrahiere Rechnungsdatum
            self._extract_element(root, paths["invoice_type"], nsmap, "Rechnungstyp")  # Extrahiere Rechnungstyp
            
            # Extrahiere und zeige Verkäuferinformationen
            self.data_list.addItem("\n=== Verkäufer ===")  # Überschrift für Verkäuferdaten
            seller = root.find(paths["seller"], nsmap)    # Finde das Verkäufer-Element
            if seller is not None:                        # Wenn Verkäufer gefunden wurde
                self._extract_element(seller, 'ram:Name', nsmap, "Name")  # Extrahiere Verkäufername
                
                # Verarbeite Verkäufer-Adresse
                address = seller.find(paths["seller_address"], nsmap)  # Finde Adress-Element
                if address is not None:                   # Wenn Adresse gefunden wurde
                    self._extract_element(address, 'ram:LineOne', nsmap, "Straße")  # Extrahiere Straße
                    self._extract_address(address, nsmap)  # Extrahiere und formatiere PLZ/Ort
                    self._extract_element(address, 'ram:CountryID', nsmap, "Land")  # Extrahiere Land
                
                # Verarbeite Kontaktinformationen
                contact = seller.find(paths["seller_contact"], nsmap)  # Finde Kontakt-Element
                if contact is not None:                   # Wenn Kontakt gefunden wurde
                    self._extract_element(contact, 'ram:URIID', nsmap, "E-Mail")  # Extrahiere E-Mail
                
                # Extrahiere Steuernummer/USt-ID
                self._extract_element(seller, paths["seller_tax"], nsmap, "USt-ID")  # Extrahiere Steuer-ID
            
            # Extrahiere und zeige Käuferinformationen
            self.data_list.addItem("\n=== Käufer ===")   # Überschrift für Käuferdaten
            buyer = root.find(paths["buyer"], nsmap)     # Finde das Käufer-Element
            if buyer is not None:                        # Wenn Käufer gefunden wurde
                self._extract_element(buyer, 'ram:Name', nsmap, "Name")  # Extrahiere Käufername
                
                # Verarbeite Käufer-Adresse
                address = buyer.find(paths["buyer_address"], nsmap)  # Finde Adress-Element
                if address is not None:                   # Wenn Adresse gefunden wurde
                    self._extract_element(address, 'ram:LineOne', nsmap, "Straße")  # Extrahiere Straße
                    self._extract_address(address, nsmap)  # Extrahiere und formatiere PLZ/Ort
                    self._extract_element(address, 'ram:CountryID', nsmap, "Land")  # Extrahiere Land
            
            # Extrahiere und zeige Zahlungsinformationen
            self.data_list.addItem("\n=== Zahlungsinformationen ===")  # Überschrift für Zahlungsdaten
            payment = root.find(paths["payment"], nsmap)  # Finde das Zahlungs-Element
            if payment is not None:                      # Wenn Zahlungsinformationen gefunden wurden
                self._extract_element(payment, 'ram:TypeCode', nsmap, "Zahlungsart")  # Extrahiere Zahlungsart
                
                # Verarbeite Kontodaten
                account = payment.find(paths["payment_account"], nsmap)  # Finde Konto-Element
                if account is not None:                   # Wenn Kontodaten gefunden wurden
                    self._extract_element(account, 'ram:IBANID', nsmap, "IBAN")  # Extrahiere IBAN
                    self._extract_element(payment, './/ram:PayeeSpecifiedCreditorFinancialInstitution/ram:BICID', nsmap, "BIC")  # Extrahiere BIC
            
            # Extrahiere und zeige Betragsangaben
            self.data_list.addItem("\n=== Beträge ===")  # Überschrift für Beträge
            monetary = root.find(paths["monetary"], nsmap)  # Finde das Beträge-Element
            if monetary is not None:                     # Wenn Beträge gefunden wurden
                self._extract_amount(monetary, paths["amount_net"], nsmap, "Nettobetrag")  # Extrahiere Nettobetrag
                self._extract_amount(monetary, paths["amount_tax"], nsmap, "Steuerbetrag")  # Extrahiere Steuerbetrag
                self._extract_amount(monetary, paths["amount_total"], nsmap, "Gesamtbetrag")  # Extrahiere Gesamtbetrag
                
        except Exception as e:                          # Fehlerbehandlung
            self.data_list.addItem(f"Fehler beim Extrahieren der Daten: {str(e)}")  # Zeige Fehlermeldung an

    def _extract_element(self, root, path, nsmap, label):
        """
        Extrahiert ein einzelnes Element und fügt es zur Liste hinzu.
        
        Hilfsmethode zum einheitlichen Extrahieren und Formatieren von
        XML-Elementen.
        
        Args:
            root: XML-Element in dem gesucht wird
            path: XPath-Ausdruck zum Finden des Elements
            nsmap: Namespace-Mapping für die XPath-Suche
            label: Beschriftung für die Anzeige
        """
        element = root.find(path, nsmap)               # Finde Element
        if element is not None:                        # Wenn Element gefunden
            self.data_list.addItem(f"{label}: {element.text}")  # Füge zur Liste hinzu

    def _extract_address(self, address, nsmap):
        """
        Extrahiert und formatiert eine Adresse.
        
        Spezielle Methode zur Verarbeitung von Adressdaten. Kombiniert
        PLZ und Ort zu einer formatierten Zeile.
        
        Args:
            address: XML-Element mit den Adressdaten
            nsmap: Namespace-Mapping für die XML-Verarbeitung
        """
        city = address.find('ram:CityName', nsmap)     # Finde Stadt
        postal = address.find('ram:PostcodeCode', nsmap)  # Finde PLZ
        if postal is not None or city is not None:     # Wenn PLZ oder Stadt vorhanden
            address_line = "PLZ/Ort: "                 # Erstelle Adresszeile
            if postal is not None:                     # Wenn PLZ vorhanden
                address_line += postal.text            # Füge PLZ hinzu
            if city is not None:                       # Wenn Stadt vorhanden
                address_line += f" {city.text}"        # Füge Stadt hinzu
            self.data_list.addItem(address_line)       # Füge zur Liste hinzu

    def _extract_amount(self, monetary, path, nsmap, label):
        """
        Extrahiert und formatiert einen Geldbetrag.
        
        Spezielle Methode zur Verarbeitung von Geldbeträgen. Berücksichtigt
        den Betrag und die Währung.
        
        Args:
            monetary: XML-Element mit den Betragsdaten
            path: XPath zum Betragselement
            nsmap: Namespace-Mapping für die XML-Verarbeitung
            label: Beschriftung für die Anzeige
        """
        amount = monetary.find(path, nsmap)            # Finde Betrag
        if amount is not None:                         # Wenn Betrag gefunden
            self.data_list.addItem(                    # Füge zur Liste hinzu
                f"{label}: {amount.text} {amount.get('currencyID', '')}"
            )

    def _detect_zugferd_version(self, root):
        """
        Erkennt die Version der PDF-Rechnung.
        
        Analysiert den Namespace des Root-Elements um die Version zu bestimmen.
        Unterstützt die Versionen 1.0 und 2.0.
        
        Args:
            root: XML-Root-Element der Rechnungsdaten
            
        Returns:
            str: Erkannte Version ("1.0", "2.0" oder "unbekannt")
        """
        if root.tag.startswith('{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100'):  # Prüfe auf Version 2.0
            return "2.0"                                  # Gebe Version 2.0 zurück
        elif root.tag.startswith('{urn:ferd:CrossIndustryDocument:invoice:1p0'):  # Prüfe auf Version 1.0
            return "1.0"                                  # Gebe Version 1.0 zurück
        else:
            return "unbekannt"                           # Gebe "unbekannt" zurück wenn Version nicht erkannt

    def clear_display(self):
        """
        Leert alle Anzeigeelemente.
        
        Setzt die Tabelle und die Baumstruktur zurück, wird bei Fehlern
        oder beim Laden neuer Daten verwendet.
        """
        self.table.setRowCount(0)                        # Lösche alle Tabellenzeilen
        self.tree.clear()                                # Lösche Baumstruktur

    def load_zugferd(self, pdf_path):
        """
        Lädt und analysiert eine PDF-Rechnung.
        
        Hauptmethode zum Laden einer PDF-Datei. Extrahiert die Rechnungsdaten
        und zeigt diese an. Behandelt verschiedene Fehlerfälle und zeigt
        entsprechende Dialoge.
        
        Args:
            pdf_path: Pfad zur PDF-Datei
        """
        try:
            result = extract_zugferd_data(pdf_path)      # Extrahiere Daten aus PDF
            if result is None or len(result) != 2:       # Prüfe ob Daten gefunden wurden
                QMessageBox.warning(
                    self,
                    "Keine PDF-Rechnungsdaten",
                    "Diese PDF enthält keine PDF-Rechnungsdaten."
                )                                        # Zeige Warnung an
                self.clear_display()                     # Leere die Anzeige
                return
                
            xml_data, parsed_data = result              # Extrahiere XML und geparste Daten
            if not xml_data or not parsed_data:         # Prüfe ob Daten gültig sind
                QMessageBox.warning(
                    self,
                    "Keine PDF-Rechnungsdaten",
                    "Diese PDF enthält keine gültigen PDF-Rechnungsdaten."
                )                                       # Zeige Warnung an
                self.clear_display()                    # Leere die Anzeige
                return
                
            self.display_data(xml_data, parsed_data)   # Zeige die Daten an
            
        except ValueError as e:                        # Bei Wertefehlern
            QMessageBox.warning(
                self,
                "Keine PDF-Rechnungsdaten",
                f"Diese PDF enthält keine PDF-Rechnungsdaten.\nDetails: {str(e)}"
            )                                          # Zeige detaillierte Warnung an
            self.clear_display()                       # Leere die Anzeige
        except Exception as e:                         # Bei anderen Fehlern
            QMessageBox.critical(
                self,
                "Fehler beim Laden",
                f"Die PDF-Rechnungsdaten konnten nicht geladen werden:\n{str(e)}"
            )                                          # Zeige kritischen Fehler an
            self.clear_display()                       # Leere die Anzeige

    def create_tree_item(self, element):
        """
        Erstellt ein TreeWidgetItem aus einem XML-Element.
        
        Konvertiert ein XML-Element in ein QTreeWidgetItem für die Baumansicht.
        Verarbeitet den Element-Namen, Text und Attribute.
        
        Args:
            element: XML-Element das konvertiert werden soll
            
        Returns:
            QTreeWidgetItem: Das erstellte Baumelement
        """
        item = QTreeWidgetItem()                      # Erstelle neues Baumelement
        
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag  # Entferne Namespace
        item.setText(0, tag)                          # Setze Element-Name
        
        if element.text and element.text.strip():     # Wenn Element Text enthält
            item.setText(1, element.text.strip())     # Setze Element-Text
        
        for key, value in element.attrib.items():     # Für jedes Attribut
            attr_item = QTreeWidgetItem()             # Erstelle neues Element
            attr_item.setText(0, f"@{key}")           # Setze Attribut-Name
            attr_item.setText(1, value)               # Setze Attribut-Wert
            item.addChild(attr_item)                  # Füge als Kind hinzu
        
        for child in element:                         # Für jedes Kind-Element
            item.addChild(self.create_tree_item(child))  # Füge rekursiv hinzu
        
        return item                                   # Gebe erstelltes Element zurück

    def display_data(self, xml_data, parsed_data):
        """
        Zeigt die verarbeiteten Daten an.
        
        Aktualisiert die Tabelle und die Baumstruktur mit den neuen Daten.
        Passt die Darstellung automatisch an und behandelt mögliche Fehler.
        
        Args:
            xml_data: XML-Rohdaten als String
            parsed_data: Bereits verarbeitete Daten als Dictionary
        """
        try:
            self.table.setRowCount(0)                 # Lösche alte Tabelleneinträge
            self.table.setRowCount(len(parsed_data))  # Setze neue Anzahl Zeilen
            
            for row, (key, value) in enumerate(parsed_data.items()):  # Für jeden Datensatz
                self.table.setItem(row, 0, QTableWidgetItem(key))     # Setze Schlüssel
                self.table.setItem(row, 1, QTableWidgetItem(str(value)))  # Setze Wert
            
            self.table.resizeColumnsToContents()      # Passe Spaltenbreiten an
            self.table.resizeRowsToContents()         # Passe Zeilenhöhen an
            
            self.tree.clear()                         # Lösche alte Baumstruktur
            root = ET.fromstring(xml_data)            # Parse XML-Daten
            self.tree.addTopLevelItem(self.create_tree_item(root))  # Erstelle Baumstruktur
            self.tree.expandToDepth(1)                # Expandiere erste Ebene
            
        except Exception as e:                        # Bei Fehlern
            QMessageBox.critical(
                self,
                "Fehler bei der Anzeige",
                f"Die PDF-Rechnungsdaten konnten nicht angezeigt werden:\n{str(e)}"
            )                                         # Zeige kritischen Fehler an
            self.clear_display()                      # Leere die Anzeige 