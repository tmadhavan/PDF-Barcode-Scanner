import os
import sys
import uuid
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from werkzeug.utils import secure_filename
from flask_cors import CORS
from server.pdf_converter import PdfConverter

UPLOAD_FOLDER = os.path.join(os.path.dirname(sys.argv[0]), "uploads")
ALLOWED_FILETYPES = ['pdf']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "../uploads"

api = Api(app, prefix="/api/v1")

# Allow Cross-Origin requests to the API
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


class UploadController(Resource):

    HTML_INPUT_NAME = 'pdfToConvert'

    def __init__(self):
        self.converter = PdfConverter()

    def allowed_file(self, filename: str) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_FILETYPES
    
    def get(self) -> dict:
        return {'Message': 'POST to this endpoint'}

    def post(self) -> tuple:
        # get() rather than ['key'] returns a default of None rather than raising KeyError
        uploaded_file = request.files.get(self.HTML_INPUT_NAME)
        if not uploaded_file:
            return {'Error': 'No file provided'}, 400
        
        if not self.allowed_file(uploaded_file.filename):
            return {'Error': 'This is not a PDF file'}, 400

        # Save the PDF in its own folder, and pass on the file location to the PDF converter
        safe_filename = secure_filename(uploaded_file.filename)
        save_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
        absolute_save_path = os.path.join(save_folder, safe_filename)

        try:
            os.mkdir(save_folder)
            print(f'Saving file to {absolute_save_path}')
            uploaded_file.save(absolute_save_path)
            self.converter.add_pdf(absolute_save_path)

        except OSError:
            if os.path.exists(absolute_save_path):
                os.remove(absolute_save_path)
            if os.path.exists(save_folder):
                os.rmdir(save_folder)
            return {'Error': 'Could not save file'}, 500

        return {'Message': uploaded_file.filename}, 200


api.add_resource(UploadController, '/upload')

if __name__ == "__main__":
    app.run(debug=False)