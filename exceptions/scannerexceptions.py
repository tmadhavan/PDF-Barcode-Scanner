class ScanError(Exception):
    def __init__(self, scanned_file):
        self.scanned_file = scanned_file