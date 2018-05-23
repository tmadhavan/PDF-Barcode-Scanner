from server.barcode_extractor import scan_images
import os


class Scanner:

    # TODO Email has to somewhere else! It's not the scanner's responsibility
    def __init__(self, scan_target, output_folder, barcode_file_prefix, email):
        self.scan_target = scan_target
        self.output_folder = output_folder
        self.barcode_output_filename = barcode_file_prefix + "-barcodes.txt"
        self.email = email

    def get_file_attachment_path(self):
        return os.path.join(self.output_folder, self.barcode_output_filename)

    def scan(self):
        raise NotImplementedError


class ImageScanner(Scanner):

    def __init__(self, scan_folder, barcode_file_prefix, email):
        # Always output to the input folder
        output_folder = scan_folder
        super().__init__(scan_folder, output_folder, barcode_file_prefix, email)

    def scan(self):
        # scan_target is a folder of images
        scan_images(self.scan_target, os.path.join(self.output_folder, self.barcode_output_filename))


class UrlScanner(Scanner):

    def __init__(self, scan_url, output_folder, barcode_file_prefix, email):
        super().__init__(scan_url, output_folder, barcode_file_prefix, email)

    def scan(self):
        print ("Scanning some URL")

