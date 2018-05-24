from server.barcode_extractor import scan_images
import os


class Scanner:

    def __init__(self, scan_target, output_folder, barcode_file_prefix):
        self.scan_target = scan_target
        self.output_folder = output_folder
        self.barcode_output_filename = barcode_file_prefix + "-barcodes.txt"

    def get_file_attachment_path(self):
        return os.path.join(self.output_folder, self.barcode_output_filename)

    def scan(self):
        raise NotImplementedError


class ImageScanner(Scanner):

    def __init__(self, scan_folder, barcode_file_prefix):
        """
        Create a Scanner that will look for images (default PNG) in a folder, scan them for barcodes, and output the
        detected barcodes to a text file.

        :param scan_folder: The folder to scan for images
        :param barcode_file_prefix: The filename prefix for the output file (e.g. "myfile" will produce an output file
        called "myfile-barcodes.txt"
        """
        # Always output to the input folder
        output_folder = scan_folder
        super().__init__(scan_folder, output_folder, barcode_file_prefix)

    def scan(self):
        # scan_target is a folder of images
        scan_images(self.scan_target, os.path.join(self.output_folder, self.barcode_output_filename))


class UrlScanner(Scanner):

    def __init__(self, scan_url, output_folder, barcode_file_prefix):
        super().__init__(scan_url, output_folder, barcode_file_prefix)

    def scan(self):
        print ("Scanning some URL")

