import os
import sys
import configparser
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from server.app_manager import AppManager
from server.controllers.upload_controller import UploadController

app = Flask(__name__)

api = Api(app, prefix="/api/v1")

# Allow Cross-Origin requests to the API
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Read local.properties for the email auth info
parser = configparser.ConfigParser()
parser.read('local.properties')

upload_config = parser['UPLOAD']
upload_folder = upload_config['upload_folder']
email_config = parser['EMAIL']

if not os.path.exists(upload_folder):
    print(f"Upload location {upload_folder} does not exist! Exiting...", file=sys.stderr)
    sys.exit(1)

print(f"Using upload folder: {upload_folder}")
app.config['UPLOAD_FOLDER'] = upload_folder

app_manager = AppManager(email_config)

api.add_resource(UploadController, '/upload',
                 resource_class_kwargs={'upload_config': upload_config, 'app_manager': app_manager})

if __name__ == "__main__":
    app.run(debug=False)