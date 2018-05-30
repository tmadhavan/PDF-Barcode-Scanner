import os
import shutil
import uuid
from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename

from scanning.scanners import PdfScanner
from server.app_manager import AppManager
from validate_email import validate_email


class UploadController(Resource):

    ALLOWED_FILETYPES = ['pdf']
    HTML_INPUT_NAME = 'pdfToConvert'
    EMAIL_FORM_INPUT_NAME = 'emailAddress'
    URL_SCAN_INPUT_NAME = "urlToScan"

    def __init__(self,  upload_config, app_manager: AppManager):
        self.upload_config = upload_config
        self.converter = app_manager

    def allowed_file(self, filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_FILETYPES
    
    def get(self) -> dict:
        return {'Message': 'POST to this endpoint'}

    # TODO At the moment we're just dealing with PDF scanning. Add a req parameter to differentiate between URL and
    # PDF scanning
    def post(self) -> tuple:

        # get() rather than ['key'] returns a default of None rather than raising KeyError
        uploaded_file = request.files.get(self.HTML_INPUT_NAME)
        email_address = request.form[self.EMAIL_FORM_INPUT_NAME]
        url_to_scan = request.form[self.URL_SCAN_INPUT_NAME]

        print(email_address)

        if not uploaded_file:
            return {'Error': 'No file provided'}, 400
        
        if not self.allowed_file(uploaded_file.filename):
            return {'Error': 'This is not a PDF file'}, 400

        if not email_address or not validate_email(email_address):
            return {'Error': 'Invalid email address provided'}, 400

        # IF PDF

        # Save the PDF in its own folder, and pass on the file location to the PDF converter
        safe_filename = secure_filename(uploaded_file.filename)
        save_folder = os.path.join(self.upload_config['upload_folder'], str(uuid.uuid4()))
        pdf_save_path = os.path.join(save_folder, safe_filename)

        try:
            os.mkdir(save_folder)
            print(f'Saving file to {pdf_save_path}')
            uploaded_file.save(pdf_save_path)
            self.converter.scan_queue.put((PdfScanner(pdf_save_path), email_address))

        except OSError as e:
            if os.path.exists(save_folder):
                shutil.rmtree(save_folder)
            return {'Error': 'Could not save file: ' + str(e)}, 500

        return {'Message': uploaded_file.filename}, 200

        # TODO OTHERWISE, DO SOME URL SCANNING STUFF
