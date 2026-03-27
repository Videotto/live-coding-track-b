import sys
import os

# Add project root to path so we can import src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, jsonify, request
from flask_cors import CORS

from src.tracker import track_face_crop

app = Flask(__name__)
CORS(app)

# ─── Build your API endpoints below ───


if __name__ == "__main__":
    app.run(debug=True, port=5000)
