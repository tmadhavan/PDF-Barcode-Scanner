import shutil
import threading
from queue import Queue

from exceptions.scannerexceptions import ScanError
from utils.emailer import EmailManager, EmailDetails


class ScannerThread(threading.Thread):

    def __init__(self, scan_queue: Queue, email_manager: EmailManager):
        self.scan_queue = scan_queue
        self.email_manager = email_manager
        super().__init__()

    def run(self):

        while True:
            scanner, email_address = self.scan_queue.get()
            print(f'ScannerThread {threading.current_thread().getName()} got new target to scan: {scanner.scan_target}')

            try:
                scanner.scan()
                self.email_manager.email_queue.put(EmailDetails(scanner, email_address))

            # TODO centralise the cleanup code instead of littering shutil.rmtree all over the place
            except ScanError as se:
                shutil.rmtree(scanner.output_folder)
                print("ERROR SCANNING FILE: " + se.scanned_file)

            except OSError:
                shutil.rmtree(scanner.output_folder)
                print("Unknown error (OSError) scanning file")

            self.scan_queue.task_done()


class ScanManager:

    MAX_THREADS = 3

    def __init__(self, scan_queue: Queue, email_manager: EmailManager, max_threads=MAX_THREADS):

        self.scan_queue = scan_queue

        for i in range(max_threads):
            scan_worker = ScannerThread(self.scan_queue, email_manager)
            scan_worker.setDaemon(True)
            scan_worker.start()

        self.scan_queue.join()

