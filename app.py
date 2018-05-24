import os
import sys
import configparser
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from server.upload_controller import UploadController

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "../uploads"

api = Api(app, prefix="/api/v1")

# Allow Cross-Origin requests to the API
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

UPLOAD_FOLDER = os.path.join(os.path.dirname(sys.argv[0]), "uploads")

# Read local.properties for the email auth info
parser = configparser.ConfigParser()
parser.read('local.properties')

api.add_resource(UploadController, '/upload',
                 resource_class_kwargs={'upload_folder': UPLOAD_FOLDER, 'email_config': parser['EMAIL']})


if __name__ == "__main__":
    app.run(debug=False)