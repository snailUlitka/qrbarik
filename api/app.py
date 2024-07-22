from typing import Any

from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)

CORS(app)

@app.route('/generate', methods=['POST'])
def generate_qr_code():
    info: dict[str, Any] = request.json
    text_to_generate = info.get('text')

    if isinstance(text_to_generate, str):
        # TODO: Invoke func for QR-code generating
        return jsonify("result"), 200
    return "Await for a 'text' key in JSON request", 400