import datetime
import os
import json
from flask import Flask, request
import numpy as np
import cv2
from PIL import Image
import io
import base64


app = Flask(__name__)

@app.route("/helloworld")
def hello_world():
    return 'hello, world'

@app.route("/upload_image", methods=['POST'])
def upload_image():
   try:
       # Get JSON data from request
       data = request.data
       json_data = json.loads(data)
       print(json_data)
       
       # Extract filename and base64 image
       filename = data['filename']
       base64_image = data['base64']
       timestamp = data['timestamp']
       
       if not filename or not base64_image:
           return {
               "error": "Missing filename or image data"
           }, 400
           
       # Decode base64 to bytes
       image_bytes = base64.b64decode(base64_image)
       
       # Convert bytes to PIL Image
       image = Image.open(io.BytesIO(image_bytes))
       
       # Create uploads directory if it doesn't exist 
       if not os.path.exists('uploads'):
           os.makedirs('uploads')
           
       # Generate path with timestamp and original filename
       timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
       save_path = f"uploads/{timestamp}_{filename}"
       
       # Save the image
       image.save(save_path, 'JPEG')
       
       return {
           "message": "Image saved successfully",
           "filename": save_path
       }, 200
       
   except Exception as e:
       return {
           "error": str(e)
       }, 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)