import shutil
from smtplib import SMTP as smtp
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.mime.text import MIMEText
from email import encoders
import threading
import os
from queue import Queue

from scanning.scanners import Scanner


class EmailManager:

    MAX_THREADS = 3

    def __init__(self, email_queue: Queue, email_config, max_threads=MAX_THREADS):

        self.email_queue: Queue = email_queue

        for t in range(max_threads):
            email_thread = EmailThread(self.email_queue, email_config)
            email_thread.setDaemon(True)
            email_thread.start()

        self.email_queue.join()


class EmailDetails:
    def __init__(self, scanner: Scanner, email_address: str):
        self.scanner = scanner
        self.email_address = email_address


class EmailThread(threading.Thread):

    def __init__(self, email_work_queue, email_config):
        self.email_queue = email_work_queue
        self.email_config = email_config
        self.smtp_server = smtp(email_config['smtp_server'], email_config['smtp_port'])
        super().__init__()

    def run(self):
        while True:
            email_details: EmailDetails = self.email_queue.get()
            scanner = email_details.scanner
            email_address = email_details.email_address

            self.send_email(os.path.join(scanner.output_folder, scanner.barcode_file),
                            scanner.job_label, email_address)

            # Remove the output folder and its contents
            print (f"Deleting {scanner.output_folder}")
            shutil.rmtree(scanner.output_folder)
            self.email_queue.task_done()

    def send_email(self, barcode_file, subject_job_name, email_address):

        filename = os.path.basename(barcode_file)

        # Create the email
        msg = MIMEMultipart()
        msg['From'] = self.email_config['user']
        msg['To'] = email_address
        msg['Subject'] = f'Your barcodes'

        # Attach the message body
        message = f'Your barcodes for {subject_job_name} are attached'
        msg.attach(MIMEText(message, 'plain'))

        # Attach the output file
        try:

            with open(barcode_file) as attachment:
                message_attachment = MIMEBase('multipart', 'plain')
                message_attachment.set_payload(attachment.read())
                encoders.encode_base64(message_attachment)
                message_attachment.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(message_attachment)

            self.smtp_server.starttls()

            # Login Credentials for sending the mail
            self.smtp_server.login(self.email_config['user'], self.email_config['password'])

            # send the message via the server.
            print(f'Sending email to: {email_address}')
            self.smtp_server.sendmail(msg['From'], msg['To'], msg.as_string())

        except OSError:
            print("There was an error reading the barcode output file while attaching it to the email")

        finally:
            self.smtp_server.quit()


