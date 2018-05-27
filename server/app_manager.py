from queue import Queue
from scanning.manager import ScanManager
from utils.emailer import EmailManager


class AppManager:
    """
    Takes care of the creation of various work queues and manager objects for emails, PDF conversion, and barcode
    scanning.
    """

    MAX_THREADS = 3 

    def __init__(self, email_config, max_threads=MAX_THREADS):
        self.scan_queue = Queue()
        self.email_queue = Queue()

        self.email_manager = EmailManager(self.email_queue, email_config)
        self.scan_manager = ScanManager(self.scan_queue, self.email_queue)




