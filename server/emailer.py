from smtplib import SMTP as smtp
from email.mime.multipart import MIMEMultipart, MIMEBase
from email.mime.text import MIMEText
from email import encoders
import threading
import os
from queue import Queue

class EmailWorkItem:

    def __init__(self, file_to_attach_path, email_address):
        self.barcodes_file = file_to_attach_path
        self.email = email_address


class EmailManager:

    MAX_THREADS = 1

    def __init__(self, email_work_queue, email_config, max_threads=MAX_THREADS):

        self.email_work_queue = email_work_queue

        for t in range(max_threads):
            email_thread = EmailWorker(self.email_work_queue, email_config)
            email_thread.setDaemon(True)
            email_thread.start()


class EmailWorker(threading.Thread):

    def __init__(self, email_work_queue, email_config):
        super().__init__()
        self.work_queue = email_work_queue
        self.email_config = email_config
        self.smtp_server = smtp(email_config['smtp_server'], email_config['smtp_port'])

    def send_email(self, work_item: EmailWorkItem):
        print(f'Sending email to: {work_item.email}')

        msg = MIMEMultipart()
        filename = os.path.basename(work_item.barcodes_file)

        msg['From'] = self.email_config['user']
        msg['To'] = work_item.email
        msg['Subject'] = f'Barcodes: {filename}'

        # Attach the message body
        message = f'Your barcodes for {filename} are attached'
        msg.attach(MIMEText(message, 'plain'))

        # Attach the output file
        try:

            with open(work_item.barcodes_file) as attachment:
                message_attachment = MIMEBase('multipart', 'plain')
                message_attachment.set_payload(attachment.read())
                encoders.encode_base64(message_attachment)
                message_attachment.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(message_attachment)

        except OSError:
            print("There was an error reading the barcode output file while attaching it to the email")


        self.smtp_server.starttls()

        # Login Credentials for sending the mail
        self.smtp_server.login(self.email_config['user'], self.email_config['password'])

        # send the message via the server.
        self.smtp_server.sendmail(msg['From'], msg['To'], msg.as_string())

        self.smtp_server.quit()

    def run(self):
        while True:
            email_work_item: EmailWorkItem = self.work_queue.get()
            self.send_email(email_work_item)
            self.work_queue.task_done()