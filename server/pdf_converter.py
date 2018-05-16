import os
import threading
from queue import Queue
from subprocess import run, CompletedProcess
from server.extractor import scan_images


class ScannerThread(threading.Thread):

    def __init__(self, scanner_queue: Queue):
        self.work_queue = scanner_queue
        super().__init__()

    def run(self):

        while True:
            work_item: ScannerWorkItem = self.work_queue.get()
            print(f'ScannerThread got new folder to scan: {work_item.folder_to_scan}')
            scan_images(work_item.folder_to_scan, work_item.barcode_output_file)
            self.work_queue.task_done()


class ScannerWorkItem:

    def __init__(self, folder_to_scan, barcode_file_prefix):
        self.folder_to_scan = folder_to_scan
        self.barcode_output_file = barcode_file_prefix + "-barcodes.txt"


class ConverterThread(threading.Thread):

    pdf_convert_result = None

    def __init__(self, pdf_queue: Queue, scan_queue: Queue):
        self.work_queue = pdf_queue
        self.scan_queue = scan_queue
        super().__init__()

    def run(self):
        # Keep running until the main() method has finished
        while True:
            # Get the next file path from the queue
            pdf_to_convert_path = self.work_queue.get()

            # Start the new file conversion (this bit should perhaps be async)
            parent_directory = os.path.dirname(pdf_to_convert_path)
            file_name = os.path.basename(pdf_to_convert_path)
            pdf_conversion_command = ['pdftoppm', pdf_to_convert_path, file_name, '-png', '-r', '300']

            print(f'{threading.currentThread().getName()} processing {pdf_to_convert_path}')
            self.pdf_convert_result: CompletedProcess = run(pdf_conversion_command, cwd=parent_directory)
            print(f'{threading.currentThread().getName()} finished converting {pdf_to_convert_path}')

            if self.pdf_convert_result.returncode == 0:
                self.scan_queue.put(ScannerWorkItem(parent_directory, file_name))

            self.work_queue.task_done()


class PdfConverter:

    MAX_THREADS = 3 

    def __init__(self, max_threads=MAX_THREADS):
        self.convert_queue = Queue()
        self.scan_queue = Queue()
        for i in range(max_threads):
            pdf_worker = ConverterThread(self.convert_queue, self.scan_queue)
            pdf_worker.setDaemon(True)
            pdf_worker.start()

            scan_worker = ScannerThread(self.scan_queue)
            scan_worker.setDaemon(True)
            scan_worker.start()

        self.convert_queue.join()

    def add_pdf(self, file_path: str):
        self.convert_queue.put(file_path)
        
