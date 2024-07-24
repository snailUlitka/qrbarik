from typing import Any
from PIL import Image
import io
import base64
import numpy as np
import cv2

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

@app.route('/read', methods=['POST'])
def read_qr_code():
    if 'file' not in request.files:
        return jsonify({'error': 'Требуется файл изображения'}), 400
    
    file = request.files['file']
    image = Image.open(file.stream)
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR) # Bytes array from the image
    det = cv2.QRCodeDetector()
    retval, decoded_info, _, _ = det.detectAndDecodeMulti(image_cv) # Detects qr-code on image

    results = []
    if retval:
        for info in decoded_info:
            results.append(info)
    
    return jsonify({"text": results}), 200
    