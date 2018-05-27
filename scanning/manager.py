import threading
from queue import Queue

from exceptions.scannerexceptions import ScanError
from utils.emailer import EmailManager, EmailDetails


class ScannerThread(threading.Thread):

    def __init__(self, scan_queue: Queue, email_queue: Queue):
        self.scan_queue = scan_queue
        self.email_queue = email_queue
        super().__init__()

    def run(self):

        while True:
            scanner, email_address = self.scan_queue.get()
            print(f'ScannerThread {threading.current_thread().getName()} got new target to scan: {scanner.scan_target}')

            try:
                scanner.scan()
                self.email_queue.put(EmailDetails(scanner, email_address))

            except ScanError as se:
                print("ERROR SCANNING FILE: " + se.scanned_file)

            self.scan_queue.task_done()


class ScanManager:

    MAX_THREADS = 2

    def __init__(self, scan_queue: Queue, email_queue: Queue, max_threads=MAX_THREADS):

        self.scan_queue = scan_queue

        for i in range(max_threads):
            scan_worker = ScannerThread(self.scan_queue, email_queue)
            scan_worker.setDaemon(True)
            scan_worker.start()

        self.scan_queue.join()

