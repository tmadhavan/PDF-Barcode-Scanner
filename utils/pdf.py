import os
import threading
from queue import Queue
from subprocess import CompletedProcess, run

from scanning.scanners import ImageScanner
from scanning.manager import ScanManager


class PdfManager:

    MAX_THREADS = 3

    def __init__(self, work_queue: Queue, scan_manager: ScanManager, max_threads=MAX_THREADS):

        self.work_queue = work_queue

        for i in range(max_threads):
            pdf_worker = PdfConverterThread(self.work_queue, scan_manager.scan_queue)
            pdf_worker.setDaemon(True)
            pdf_worker.start()

        self.work_queue.join()


class PdfConverterThread(threading.Thread):

    def __init__(self, pdf_queue: Queue, scan_queue: Queue):
        self.pdf_queue = pdf_queue
        self.scan_queue = scan_queue
        self.pdf_convert_result = None
        super().__init__()

    def run(self):

        while True:
            pdf_path, email_address = self.pdf_queue.get()

            # Output the converted images in the PDF folder, named with the PDF filename as a prefix
            pdf_file = os.path.basename(pdf_path)
            pdf_folder = os.path.dirname(pdf_path)
            output_file_prefix = os.path.splitext(pdf_file)[0]

            pdf_conversion_command = ['pdftoppm', pdf_file, output_file_prefix, '-png', '-r', '300']

            print(f'{threading.currentThread().getName()} processing {pdf_path}')
            self.pdf_convert_result: CompletedProcess = run(pdf_conversion_command, cwd=pdf_folder)

            if self.pdf_convert_result.returncode == 0:
                print(f'{threading.currentThread().getName()} finished converting {pdf_path}')
                self.scan_queue.put((ImageScanner(pdf_folder, output_file_prefix, pdf_file), email_address))
            else:
                print(f'{threading.currentThread().getName()} error converting {pdf_path}')

            self.pdf_queue.task_done()
