import threading
from queue import Queue

from server.barcode_scanners import Scanner


class ScannerThread(threading.Thread):

    def __init__(self, work_queue: Queue, email_queue: Queue):
        self.work_queue = work_queue
        self.email_queue = email_queue
        super().__init__()

    def run(self):

        while True:
            work_item: Scanner = self.work_queue.get()
            print(f'ScannerThread got new target to scan: {work_item.scan_target}')

            work_item.scan()

            self.email_queue.put((work_item.get_file_attachment_path(), work_item.email))
            self.work_queue.task_done()


class ScanManager:

    MAX_THREADS = 3

    def __init__(self, scan_queue: Queue, email_queue: Queue, max_threads=MAX_THREADS):

        self.scan_queue = scan_queue
        self.email_queue = email_queue

        for i in range(max_threads):
            scan_worker = ScannerThread(self.scan_queue, self.email_queue)
            scan_worker.setDaemon(True)
            scan_worker.start()

        self.scan_queue.join()
        self.email_queue.join()

