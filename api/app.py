from typing import Any
from PIL import Image
import numpy as np
import cv2

from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from


app = Flask(__name__)
CORS(app)
app.config['SWAGGER'] = {
    'title': 'QR Code API',
    'uiversion': 3
}
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'swagger',
            "route": '/swagger.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger"
}

swagger = Swagger(app, config=swagger_config)

@app.route('/generate', methods=['POST'])  
@swag_from('documentation/generate.yml')
def generate_qr_code():
    info: dict[str, Any] = request.get_json()
    text_to_generate = info.get('text')

    if isinstance(text_to_generate, str):
        # TODO: Invoke func for QR-code generating
        return jsonify("result"), 200

    return "Await for a 'text' key in JSON request", 400

@app.route('/read', methods=['POST'])
@swag_from('documentation/read.yml')
def read_qr_code():
    if 'file' not in request.files:
        return jsonify({'error': 'Await for image file'}), 400

    file = request.files['file']
    image = Image.open(file.stream)
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR) # Bytes array from the image

    # TODO: Write your own solution for read QR codes
    det = cv2.QRCodeDetector()
    retval, decoded_info, _, _ = det.detectAndDecodeMulti(image_cv) # Detects qr-code on image

    results = []
    if retval:
        for info in decoded_info:
            results.append(info)

    return jsonify({"text": results}), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7845)

