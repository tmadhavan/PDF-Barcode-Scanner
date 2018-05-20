import os
import threading
from queue import Queue
from subprocess import run, CompletedProcess
from server.extractor import scan_images
from server.emailer import EmailWorkItem, EmailManager


class ScannerThread(threading.Thread):

    def __init__(self, scanner_queue: Queue, email_queue: Queue):
        self.work_queue = scanner_queue
        self.email_queue = email_queue
        super().__init__()

    def run(self):

        while True:
            work_item: ScannerWorkItem = self.work_queue.get()
            print(f'ScannerThread got new folder to scan: {work_item.folder_to_scan}')
            scan_images(work_item.folder_to_scan, work_item.barcode_output_filename)


            # TODO This has to change - EmailWorkItem just has the same info as scanner item. (BUT, the scanner could be
            # for a URL scanner (and thus not have a folder, but an address, in which case the output file location won't
            # be the scan location argh)
            self.email_queue.put(EmailWorkItem(os.path.join(work_item.folder_to_scan,
                                                            work_item.barcode_output_filename), work_item.email))
            self.work_queue.task_done()


class ScannerWorkItem:

    def __init__(self, folder_to_scan, barcode_file_prefix, email):
        self.folder_to_scan = folder_to_scan
        self.barcode_output_filename = barcode_file_prefix + "-barcodes.txt"
        self.email = email


class PdfConverterThread(threading.Thread):

    pdf_convert_result = None

    def __init__(self, pdf_queue: Queue, scan_queue: Queue):
        self.work_queue = pdf_queue
        self.scan_queue = scan_queue
        super().__init__()

    def run(self):
        # Keep running until the main() method has finished
        while True:

            client_data = self.work_queue.get()
            pdf_to_convert_path = client_data['file_path']
            email_address = client_data['email']

            parent_directory = os.path.dirname(pdf_to_convert_path)
            pdf_file = os.path.basename(pdf_to_convert_path)
            output_file_prefix = os.path.splitext(pdf_file)[0]

            pdf_conversion_command = ['pdftoppm', pdf_file, output_file_prefix, '-png', '-r', '300']

            print(f'{threading.currentThread().getName()} processing {pdf_to_convert_path}')
            self.pdf_convert_result: CompletedProcess = run(pdf_conversion_command, cwd=parent_directory)

            if self.pdf_convert_result.returncode == 0:
                print(f'{threading.currentThread().getName()} finished converting {pdf_to_convert_path}')
                self.scan_queue.put(ScannerWorkItem(parent_directory, output_file_prefix, email_address))
            else:
                print(f'{threading.currentThread().getName()} error converting {pdf_to_convert_path}')

            self.work_queue.task_done()


class ConversionManager:

    MAX_THREADS = 3 

    def __init__(self, email_config, max_threads=MAX_THREADS):
        self.convert_queue = Queue()
        self.scan_queue = Queue()
        self.email_queue = Queue()
        self.email_manager = EmailManager(self.email_queue, email_config)

        for i in range(max_threads):
            pdf_worker = PdfConverterThread(self.convert_queue, self.scan_queue)
            pdf_worker.setDaemon(True)
            pdf_worker.start()

            scan_worker = ScannerThread(self.scan_queue, self.email_queue)
            scan_worker.setDaemon(True)
            scan_worker.start()

        self.convert_queue.join()
        self.scan_queue.join()

    def add_pdf(self, client_data: dict):
        self.convert_queue.put(client_data)
        
