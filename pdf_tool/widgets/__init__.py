"""
Widget-Klassen für das PDF Tool
"""

from .home_widget import HomeWidget
from .pdf_preview_widget import PDFPreviewWidget
from .pdf_split_widget import PDFSplitWidget
from .pdf_merge_widget import PDFMergeWidget
from .pdf_to_word_widget import PDFToWordWidget
from .pdf_image_extractor_widget import PDFImageExtractorWidget
from .zugferd_reader_widget import EInvoiceReaderWidget

__all__ = [
    'HomeWidget',
    'PDFPreviewWidget',
    'PDFSplitWidget',
    'PDFMergeWidget',
    'PDFToWordWidget',
    'PDFImageExtractorWidget',
    'EInvoiceReaderWidget'
]
