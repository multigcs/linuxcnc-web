from api.api import api_bp
from client.client import client_bp
from flask import Flask

app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix="/api_v1")
app.register_blueprint(client_bp)
