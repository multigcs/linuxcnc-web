import os
from api.api import api_bp
from client.client import client_bp
from flask import Flask

UPLOAD_FOLDER = f"{os.path.expanduser('~')}/nc_files/"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.register_blueprint(api_bp, url_prefix="/api_v1")
app.register_blueprint(client_bp)
