from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
from io import BytesIO
import requests
import os
import time

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr():
    try:
        data = request.get_json()
        image_url = data.get('image_url')
        if not image_url:
            return jsonify({"error": "Missing image_url"}), 400

        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        text = pytesseract.image_to_string(img)
        # ✅ Save log
        log_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {image_url} | {text[:100]}\n"
        with open("/data/ocr_logs.txt", "a") as f:
            f.write(log_line)

        # ✅ Save image (optional for debug)
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        filename = f"/data/image_{timestamp}.jpg"
        img.save(filename)

        return jsonify({"text": text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logs', methods=['GET'])
def view_logs():
    try:
        with open("/data/ocr_logs.txt", "r") as f:
            return "<pre>" + f.read() + "</pre>"
    except FileNotFoundError:
        return "No logs yet."        

@app.route('/')
def home():
    return "OCR Server is running."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
