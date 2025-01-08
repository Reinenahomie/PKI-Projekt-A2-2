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
    """Widget zum Lesen und Anzeigen von E-Rechnungsdaten."""
    
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        
        # Hauptlayout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 0, 20, 20)
        layout.setSpacing(20)
        
        # Container für den grauen Bereich
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        
        # Label für XML-Struktur
        xml_label = QLabel("XML-Struktur der ZUGFeRD-Daten:")
        xml_label.setStyleSheet("font-weight: bold;")
        container_layout.addWidget(xml_label)
        
        # XML-Baum
        self.xml_tree = QTreeWidget()
        self.xml_tree.setHeaderLabels(["Element", "Wert"])
        self.xml_tree.setColumnCount(2)
        self.xml_tree.setAlternatingRowColors(True)
        self.xml_tree.setStyleSheet("""
            QTreeWidget {
                background-color: white;
                border: 1px solid #cccccc;
            }
            QTreeWidget::item {
                padding: 2px;
            }
        """)
        
        # Spaltenbreiten anpassen (50/50)
        header = self.xml_tree.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        self.xml_tree.setColumnWidth(0, self.width() // 2)  # 50% der Breite
        
        container_layout.addWidget(self.xml_tree)
        
        # Label für ausgewertete Daten
        data_label = QLabel("Ausgewertete Rechnungsdaten:")
        data_label.setStyleSheet("font-weight: bold;")
        container_layout.addWidget(data_label)
        
        # Daten-Liste
        self.data_list = QListWidget()
        self.data_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #cccccc;
            }
        """)
        container_layout.addWidget(self.data_list)
        
        # Füge den Container zum Hauptlayout hinzu
        layout.addWidget(container)
        
        self.setLayout(layout)

    def resizeEvent(self, event):
        """Wird aufgerufen, wenn das Widget seine Größe ändert."""
        super().resizeEvent(event)
        # Aktualisiere die Spaltenbreiten
        if hasattr(self, 'xml_tree'):
            self.xml_tree.setColumnWidth(0, self.xml_tree.width() // 2)

    def _add_xml_element(self, element, parent_item=None):
        """Fügt ein XML-Element zum Baum hinzu."""
        # Element-Name ohne Namespace
        tag = element.tag.split('}')[-1]
        text = element.text.strip() if element.text and element.text.strip() else ""
        
        # Erstelle neues TreeItem
        if parent_item is None:
            item = QTreeWidgetItem(self.xml_tree)
        else:
            item = QTreeWidgetItem(parent_item)
            
        # Setze Element-Name und Text
        item.setText(0, tag)
        if text:
            item.setText(1, text)
        
        # Füge Attribute als Kinder hinzu
        for name, value in element.attrib.items():
            attr_item = QTreeWidgetItem(item)
            attr_item.setText(0, f"@{name}")
            attr_item.setText(1, value)
        
        # Rekursiv für alle Kinder
        for child in element:
            self._add_xml_element(child, item)
            
        return item

    def showEvent(self, event):
        """Wird aufgerufen, wenn das Widget angezeigt wird."""
        super().showEvent(event)
        # Hole die aktuelle PDF vom Hauptfenster
        main_window = self.window()
        pdf_path = main_window.get_current_pdf()
        
        # Lösche alte Einträge
        self.xml_tree.clear()
        self.data_list.clear()
        
        if not pdf_path:
            root_item = QTreeWidgetItem(self.xml_tree)
            root_item.setText(0, "Keine PDF-Datei geöffnet")
            self.data_list.addItem("Keine PDF-Datei geöffnet")
            return
            
        try:
            # Extrahiere die ZUGFeRD-Daten
            result = extract_zugferd_data(pdf_path)
            if not result or len(result) != 2:
                root_item = QTreeWidgetItem(self.xml_tree)
                root_item.setText(0, "Keine ZUGFeRD-Daten gefunden")
                self.data_list.addItem("Keine ZUGFeRD-Daten gefunden")
                return
                
            xml_data, parsed_data = result
            if not xml_data or not parsed_data:
                root_item = QTreeWidgetItem(self.xml_tree)
                root_item.setText(0, "Keine gültigen ZUGFeRD-Daten gefunden")
                self.data_list.addItem("Keine gültigen ZUGFeRD-Daten gefunden")
                return
                
            # Parse die XML-Daten
            root = ET.fromstring(xml_data)
            
            # Fülle den XML-Baum
            self._add_xml_element(root)
            
            # Expandiere alle Elemente
            self.xml_tree.expandAll()
            
            # Fülle die Daten-Liste
            self._add_invoice_data(root)
            
        except Exception as e:
            root_item = QTreeWidgetItem(self.xml_tree)
            root_item.setText(0, f"Fehler beim Lesen der ZUGFeRD-Daten: {str(e)}")
            self.data_list.addItem(f"Fehler beim Lesen der ZUGFeRD-Daten: {str(e)}")

    def _add_invoice_data(self, root):
        """Extrahiert und fügt die Rechnungsdaten zur Daten-Liste hinzu."""
        # Erkenne die ZUGFeRD-Version anhand des Namespaces
        zugferd_version = self._detect_zugferd_version(root)
        if zugferd_version == "2.0":
            nsmap = {
                'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100',
                'rsm': 'urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100',
                'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100'
            }
        else:  # ZUGFeRD 1.0
            nsmap = {
                'ram': 'urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:12',
                'rsm': 'urn:ferd:CrossIndustryDocument:invoice:1p0:comfort',
                'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:15'
            }
        
        try:
            # Version anzeigen
            self.data_list.addItem(f"=== ZUGFeRD Version {zugferd_version} ===\n")
            
            # Allgemeine Rechnungsinformationen
            self.data_list.addItem("=== Allgemeine Informationen ===")
            
            if zugferd_version == "2.0":
                invoice_number = root.find('.//rsm:ExchangedDocument/ram:ID', nsmap)
                issue_date = root.find('.//rsm:ExchangedDocument/ram:IssueDateTime/udt:DateTimeString', nsmap)
                invoice_type = root.find('.//rsm:ExchangedDocument/ram:TypeCode', nsmap)
            else:
                invoice_number = root.find('.//rsm:HeaderExchangedDocument/ram:ID', nsmap)
                issue_date = root.find('.//ram:IssueDateTime/udt:DateTimeString', nsmap)
                invoice_type = root.find('.//ram:TypeCode', nsmap)
            
            if invoice_number is not None:
                self.data_list.addItem(f"Rechnungsnummer: {invoice_number.text}")
            if issue_date is not None:
                self.data_list.addItem(f"Rechnungsdatum: {issue_date.text}")
            if invoice_type is not None:
                self.data_list.addItem(f"Rechnungstyp: {invoice_type.text}")
            
            # Verkäufer-Informationen
            self.data_list.addItem("\n=== Verkäufer ===")
            
            if zugferd_version == "2.0":
                seller = root.find('.//ram:SellerTradeParty', nsmap)
            else:
                seller = root.find('.//ram:SellerTradeParty', nsmap)
            
            if seller is not None:
                name = seller.find('ram:Name', nsmap)
                if name is not None:
                    self.data_list.addItem(f"Name: {name.text}")
                
                # Adresse
                if zugferd_version == "2.0":
                    address = seller.find('.//ram:PostalTradeAddress', nsmap)
                else:
                    address = seller.find('.//ram:PostalTradeAddress', nsmap)
                
                if address is not None:
                    street = address.find('ram:LineOne', nsmap)
                    if street is not None:
                        self.data_list.addItem(f"Straße: {street.text}")
                    
                    city = address.find('ram:CityName', nsmap)
                    postal = address.find('ram:PostcodeCode', nsmap)
                    if postal is not None or city is not None:
                        address_line = "PLZ/Ort: "
                        if postal is not None:
                            address_line += postal.text
                        if city is not None:
                            address_line += f" {city.text}"
                        self.data_list.addItem(address_line)
                    
                    country = address.find('ram:CountryID', nsmap)
                    if country is not None:
                        self.data_list.addItem(f"Land: {country.text}")
                
                # Kontaktinformationen
                if zugferd_version == "2.0":
                    contact = seller.find('.//ram:URIUniversalCommunication', nsmap)
                    if contact is not None:
                        email = contact.find('ram:URIID', nsmap)
                        if email is not None:
                            self.data_list.addItem(f"E-Mail: {email.text}")
                else:
                    contact = seller.find('.//ram:EmailURIUniversalCommunication', nsmap)
                    if contact is not None:
                        email = contact.find('ram:URIID', nsmap)
                        if email is not None:
                            self.data_list.addItem(f"E-Mail: {email.text}")
                
                # Steuernummer/USt-ID
                if zugferd_version == "2.0":
                    tax_reg = seller.find('.//ram:SpecifiedTaxRegistration/ram:ID', nsmap)
                else:
                    tax_reg = seller.find('.//ram:SpecifiedTaxRegistration/ram:ID', nsmap)
                if tax_reg is not None:
                    self.data_list.addItem(f"USt-ID: {tax_reg.text}")
            
            # Käufer-Informationen
            self.data_list.addItem("\n=== Käufer ===")
            
            if zugferd_version == "2.0":
                buyer = root.find('.//ram:BuyerTradeParty', nsmap)
            else:
                buyer = root.find('.//ram:BuyerTradeParty', nsmap)
            
            if buyer is not None:
                name = buyer.find('ram:Name', nsmap)
                if name is not None:
                    self.data_list.addItem(f"Name: {name.text}")
                
                # Adresse
                if zugferd_version == "2.0":
                    address = buyer.find('.//ram:PostalTradeAddress', nsmap)
                else:
                    address = buyer.find('.//ram:PostalTradeAddress', nsmap)
                
                if address is not None:
                    street = address.find('ram:LineOne', nsmap)
                    if street is not None:
                        self.data_list.addItem(f"Straße: {street.text}")
                    
                    city = address.find('ram:CityName', nsmap)
                    postal = address.find('ram:PostcodeCode', nsmap)
                    if postal is not None or city is not None:
                        address_line = "PLZ/Ort: "
                        if postal is not None:
                            address_line += postal.text
                        if city is not None:
                            address_line += f" {city.text}"
                        self.data_list.addItem(address_line)
                    
                    country = address.find('ram:CountryID', nsmap)
                    if country is not None:
                        self.data_list.addItem(f"Land: {country.text}")
            
            # Zahlungsinformationen
            self.data_list.addItem("\n=== Zahlungsinformationen ===")
            
            if zugferd_version == "2.0":
                payment = root.find('.//ram:SpecifiedTradeSettlementPaymentMeans', nsmap)
            else:
                payment = root.find('.//ram:SpecifiedTradeSettlementPaymentMeans', nsmap)
            
            if payment is not None:
                payment_type = payment.find('ram:TypeCode', nsmap)
                if payment_type is not None:
                    self.data_list.addItem(f"Zahlungsart: {payment_type.text}")
                
                if zugferd_version == "2.0":
                    account = payment.find('.//ram:PayeePartyCreditorFinancialAccount', nsmap)
                    if account is not None:
                        iban = account.find('ram:IBANID', nsmap)
                        if iban is not None:
                            self.data_list.addItem(f"IBAN: {iban.text}")
                        
                        bank = payment.find('.//ram:PayeeSpecifiedCreditorFinancialInstitution/ram:BICID', nsmap)
                        if bank is not None:
                            self.data_list.addItem(f"BIC: {bank.text}")
                else:
                    account = payment.find('.//ram:PayeePartyCreditorFinancialAccount', nsmap)
                    if account is not None:
                        iban = account.find('ram:IBANID', nsmap)
                        if iban is not None:
                            self.data_list.addItem(f"IBAN: {iban.text}")
                        
                        bank = payment.find('.//ram:PayeeSpecifiedCreditorFinancialInstitution/ram:BICID', nsmap)
                        if bank is not None:
                            self.data_list.addItem(f"BIC: {bank.text}")
            
            # Beträge
            self.data_list.addItem("\n=== Beträge ===")
            
            if zugferd_version == "2.0":
                monetary = root.find('.//ram:SpecifiedTradeSettlementMonetarySummation', nsmap)
            else:
                monetary = root.find('.//ram:SpecifiedTradeSettlementHeaderMonetarySummation', nsmap)
            
            if monetary is not None:
                if zugferd_version == "2.0":
                    net = monetary.find('ram:LineTotalAmount', nsmap)
                    tax = monetary.find('ram:TaxTotalAmount', nsmap)
                    total = monetary.find('ram:GrandTotalAmount', nsmap)
                else:
                    net = monetary.find('ram:LineTotalAmount', nsmap)
                    tax = monetary.find('ram:TaxBasisTotalAmount', nsmap)
                    total = monetary.find('ram:GrandTotalAmount', nsmap)
                
                if net is not None:
                    self.data_list.addItem(f"Nettobetrag: {net.text} {net.get('currencyID', '')}")
                if tax is not None:
                    self.data_list.addItem(f"Steuerbetrag: {tax.text} {tax.get('currencyID', '')}")
                if total is not None:
                    self.data_list.addItem(f"Gesamtbetrag: {total.text} {total.get('currencyID', '')}")
                
        except Exception as e:
            self.data_list.addItem(f"Fehler beim Extrahieren der Daten: {str(e)}")

    def _detect_zugferd_version(self, root):
        """Erkennt die ZUGFeRD-Version anhand des Namespaces."""
        if root.tag.startswith('{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100'):
            return "2.0"
        elif root.tag.startswith('{urn:ferd:CrossIndustryDocument:invoice:1p0'):
            return "1.0"
        else:
            return "unbekannt"

    def clear_display(self):
        """Leert die Anzeige."""
        self.table.setRowCount(0)
        self.tree.clear()

    def load_zugferd(self, pdf_path):
        """Lädt und analysiert eine ZUGFeRD-Rechnung."""
        try:
            result = extract_zugferd_data(pdf_path)
            if result is None or len(result) != 2:
                QMessageBox.warning(
                    self,
                    "Keine ZUGFeRD-Daten",
                    "Diese PDF enthält keine ZUGFeRD-Rechnungsdaten."
                )
                self.clear_display()
                return
                
            xml_data, parsed_data = result
            if not xml_data or not parsed_data:
                QMessageBox.warning(
                    self,
                    "Keine ZUGFeRD-Daten",
                    "Diese PDF enthält keine gültigen ZUGFeRD-Rechnungsdaten."
                )
                self.clear_display()
                return
                
            self.display_data(xml_data, parsed_data)
            
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Keine ZUGFeRD-Daten",
                f"Diese PDF enthält keine ZUGFeRD-Rechnungsdaten.\nDetails: {str(e)}"
            )
            self.clear_display()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler beim Laden",
                f"Die ZUGFeRD-Daten konnten nicht geladen werden:\n{str(e)}"
            )
            self.clear_display()

    def create_tree_item(self, element):
        """Erstellt ein TreeWidgetItem aus einem XML-Element."""
        item = QTreeWidgetItem()
        
        # Namespace aus Tag entfernen für bessere Lesbarkeit
        tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
        item.setText(0, tag)
        
        # Text und Attribute anzeigen
        if element.text and element.text.strip():
            item.setText(1, element.text.strip())
        
        # Attribute als Kinder hinzufügen
        for key, value in element.attrib.items():
            attr_item = QTreeWidgetItem()
            attr_item.setText(0, f"@{key}")
            attr_item.setText(1, value)
            item.addChild(attr_item)
        
        # Rekursiv für alle Kindelemente
        for child in element:
            item.addChild(self.create_tree_item(child))
        
        return item

    def display_data(self, xml_data, parsed_data):
        """Zeigt die geparsten Daten in der Tabelle und dem Tree-Widget an."""
        try:
            # Tabelle leeren und Größe anpassen
            self.table.setRowCount(0)
            self.table.setRowCount(len(parsed_data))
            
            # Daten in Tabelle einfügen
            for row, (key, value) in enumerate(parsed_data.items()):
                self.table.setItem(row, 0, QTableWidgetItem(key))
                self.table.setItem(row, 1, QTableWidgetItem(str(value)))
            
            # Tabellengröße anpassen
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()
            
            # XML-Baum erstellen
            self.tree.clear()
            root = ET.fromstring(xml_data)
            self.tree.addTopLevelItem(self.create_tree_item(root))
            self.tree.expandToDepth(1)  # Erste Ebene ausklappen
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler bei der Anzeige",
                f"Die ZUGFeRD-Daten konnten nicht angezeigt werden:\n{str(e)}"
            )
            self.clear_display() 