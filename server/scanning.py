import threading
from queue import Queue
from server.emailer import EmailManager


class ScannerThread(threading.Thread):

    def __init__(self, scan_queue: Queue, email_queue: Queue):
        self.scan_queue = scan_queue
        self.email_queue = email_queue
        super().__init__()

    def run(self):

        while True:
            scanner, email_address = self.scan_queue.get()
            print(f'ScannerThread got new target to scan: {scanner.scan_target}')

            scanner.scan()

            self.email_queue.put((scanner.get_file_attachment_path(), scanner.scan_job_name, email_address))
            self.scan_queue.task_done()


class ScanManager:

    MAX_THREADS = 3

    def __init__(self, scan_queue: Queue, email_manager: EmailManager, max_threads=MAX_THREADS):

        self.scan_queue = scan_queue

        for i in range(max_threads):
            scan_worker = ScannerThread(self.scan_queue, email_manager.email_queue)
            scan_worker.setDaemon(True)
            scan_worker.start()

        self.scan_queue.join()

