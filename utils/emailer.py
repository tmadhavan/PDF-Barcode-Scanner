import shutil
from smtplib import SMTP_SSL as smtp, SMTPHeloError, SMTPNotSupportedError
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
        # self.smtp_server = smtp(email_config['smtp_server'], email_config['smtp_port'])
        self.smtp_server = smtp(email_config['smtp_server'], 465)
        super().__init__()

    def run(self):
        while True:
            email_details: EmailDetails = self.email_queue.get()
            print(f'EmailThread {threading.current_thread().getName()} got new email job: {email_details.email_address}')
            scanner = email_details.scanner
            email_address = email_details.email_address

            try:
                self.send_email(os.path.join(scanner.output_folder, scanner.barcode_file),
                                scanner.job_label, email_address)

            except SMTPHeloError:
                print("Sending email failed")

            except SMTPNotSupportedError:
                print("Sending email failed")

            except RuntimeError:
                print("Sending email failed")

            finally:
                # Remove the output folder and its contents
                print (f"Deleting {scanner.output_folder}", flush=True)
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

        except OSError as e:
            print(f'There was an error reading the barcode output file ({barcode_file}) while attaching it to the email'
                  f' for {email_address}')
            raise e

        # If the attachment was successful, send the email
        else:

            smtp_server = smtp(self.email_config['smtp_server'], self.email_config['smtp_port'])

            # Login Credentials for sending the mail
            smtp_server.login(self.email_config['user'], self.email_config['password'])
            print(f'Sending email to: {email_address}')
            smtp_server.sendmail(msg['From'], msg['To'], msg.as_string())
            smtp_server.quit()
