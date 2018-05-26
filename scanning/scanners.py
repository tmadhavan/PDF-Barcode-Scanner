import os
from urllib.parse import urlparse
from scanning.barcode_extractor import scan_images


class Scanner:

    def __init__(self, scan_target, output_folder, barcode_file_prefix, job_label):
        self.scan_target = scan_target
        self.output_folder = output_folder
        self.barcode_file = barcode_file_prefix + "-barcodes.txt"
        self.job_label = job_label

    def scan(self):
        raise NotImplementedError


class ImageScanner(Scanner):

    def __init__(self, scan_folder, barcode_file_prefix, job_label):
        """
        Create a Scanner that will look for images (default PNG) in a folder, scan them for barcodes, and output the
        detected barcodes to a text file.

        :param scan_folder: The folder to scan for images
        :param barcode_file_prefix: The filename prefix for the output file (e.g. "myfile" will produce an output file
        called "myfile-barcodes.txt"
        """
        # Always output to the input folder
        output_folder = scan_folder
        super().__init__(scan_folder, output_folder, barcode_file_prefix, job_label)

    def scan(self):
        # scan_target is a folder of images
        scan_images(self.scan_target, os.path.join(self.output_folder, self.barcode_file))


class UrlScanner(Scanner):

    def __init__(self, scan_url, output_folder, barcode_file_prefix, job_label=None):
        job_label = job_label or urlparse(scan_url)[1]
        super().__init__(scan_url, output_folder, barcode_file_prefix, job_label)

    def scan(self):
        print ("Scanning some URL")

