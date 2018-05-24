import os
import threading
from server.barcode_scanners import Scanner, ImageScanner, UrlScanner
from queue import Queue
from subprocess import run, CompletedProcess
from server.pdf import PdfManager
from server.scanning import ScanManager
from server.emailer import EmailManager


class ConversionManager:

    MAX_THREADS = 3 

    def __init__(self, email_config, max_threads=MAX_THREADS):
        self.pdf_convert_queue = Queue()
        self.scan_queue = Queue()
        self.email_queue = Queue()

        self.email_manager = EmailManager(self.email_queue, email_config)
        self.scan_manager = ScanManager(self.scan_queue, self.email_manager)
        self.pdf_conversion_manager = PdfManager(self.pdf_convert_queue, self.scan_manager)


