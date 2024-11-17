import datetime
import os
import json
from flask import Flask, request
import numpy as np
import cv2
from PIL import Image
import io
import base64
from pathlib import Path

app = Flask(__name__)

@app.route("/helloworld")
def hello_world():
    return 'hello, world'

@app.route("/upload_image", methods=['POST'])
def upload_image():
    
    try:
        # Get JSON data from request
        data = request.json

        json_data = request.get_json()
        
        # Extract filename and base64 image
        filename = json_data['filename']
        base64_image = json_data['base64']
        timestamp = json_data['timestamp']

        try:
        # Test if it's valid base64
            base64.b64decode(base64_image)
        except Exception as e:
            print(f"Invalid base64: {str(e)}")
            
        return {
            "message": "Image received successfully",
        }, 200
       
    except Exception as e:
        return {
            "error": str(e)
        }, 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)