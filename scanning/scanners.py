import os
from urllib.parse import urlparse
from scanning.pdf_scanner import scan_pdf


class Scanner:

    def __init__(self, scan_target, output_folder, barcode_file_prefix, job_label):
        self.scan_target = scan_target
        self.output_folder = output_folder
        self.barcode_file = barcode_file_prefix + "-barcodes.txt"
        self.job_label = job_label

    def scan(self):
        raise NotImplementedError


class PdfScanner(Scanner):

    def __init__(self, path_to_scan_pdf, barcode_file_prefix=None, job_label=None):
        """
        Create a Scanner that will look for images (default PNG) in a folder, scan them for barcodes, and output the
        detected barcodes to a text file.

        :param path_to_scan_pdf: The folder to scan for images
        :param barcode_file_prefix: The filename prefix for the output file (e.g. "myfile" will produce an output file
        called "myfile-barcodes.txt"
        """
        # Always output to the input folder
        output_folder = os.path.dirname(path_to_scan_pdf)
        filename = os.path.basename(path_to_scan_pdf)

        # The job label (used for email subject) and the barcode file prefix default to the filename (with extension)
        job_label = job_label or filename
        barcode_file_prefix = barcode_file_prefix or filename
        super().__init__(path_to_scan_pdf, output_folder, barcode_file_prefix, job_label)

    def scan(self):
        scan_pdf(self.scan_target, self.barcode_file)


class UrlScanner(Scanner):

    def __init__(self, scan_url, output_folder, barcode_file_prefix=None, job_label=None):

        # The job label (used for email subject) and the barcode file prefix default to the domain portion of the
        # scanned URL ('http://www.somedomain.com/thing/to/scan' -> 'www.somedomain.com')
        url_domain = urlparse(scan_url)[1]
        job_label = job_label or url_domain
        barcode_file_prefix = barcode_file_prefix or url_domain
        super().__init__(scan_url, output_folder, barcode_file_prefix, job_label)

    def scan(self):
        print ("Scanning some URL")

