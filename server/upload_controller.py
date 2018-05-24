import os
import uuid
from flask import request
from flask_restful import Resource
from werkzeug.utils import secure_filename
from server.conversion_manager import ConversionManager


class UploadController(Resource):

    ALLOWED_FILETYPES = ['pdf']
    HTML_INPUT_NAME = 'pdfToConvert'
    EMAIL_FORM_INPUT_NAME = 'emailAddress'
    URL_SCAN_INPUT_NAME = "urlToScan"

    def __init__(self,  upload_folder, email_config):
        self.upload_folder = upload_folder
        self.converter = ConversionManager(email_config)

    def allowed_file(self, filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_FILETYPES
    
    def get(self) -> dict:
        return {'Message': 'POST to this endpoint'}

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

        # Save the PDF in its own folder, and pass on the file location to the PDF converter
        safe_filename = secure_filename(uploaded_file.filename)
        save_folder = os.path.join(self.upload_folder, str(uuid.uuid4()))
        pdf_save_path = os.path.join(save_folder, safe_filename)

        try:
            os.mkdir(save_folder)
            print(f'Saving file to {pdf_save_path}')
            uploaded_file.save(pdf_save_path)
            self.converter.pdf_convert_queue.put((pdf_save_path, email_address))

        except OSError as e:
            if os.path.exists(pdf_save_path):
                os.remove(pdf_save_path)
            if os.path.exists(save_folder):
                os.rmdir(save_folder)
            return {'Error': 'Could not save file: ' + e}, 500

        return {'Message': uploaded_file.filename}, 200
