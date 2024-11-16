import datetime
import os
import json
from flask import Flask, request
import numpy as np
import cv2
from PIL import Image
import io

app = Flask(__name__)

@app.route("/helloworld")
def hello_world():
    return 'hello, world'

@app.route("/upload_image", methods=['POST'])
def upload_image():
    try:
        # Get the byte array from the request
        image_bytes = request.data
        
        # Convert bytes to numpy array using PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Create uploads directory if it doesn't exist
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        
        # Generate unique filename using timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"uploads/image_{timestamp}.jpg"
        
        # Save the image
        image.save(filename, 'JPEG')
        
        return {
            "message": "Image saved successfully",
            "filename": filename
        }, 200
        
    except Exception as e:
        return {
            "error": str(e)
        }, 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)