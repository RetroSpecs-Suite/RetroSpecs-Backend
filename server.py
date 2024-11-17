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
from openai import OpenAI
from dotenv import load_dotenv
import chromadb
from vectorDB import VectorDB

db = VectorDB()

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

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
            image_data = base64.b64decode(base64_image)
            #image = Image.open(io.BytesIO(image_data))
            #print(f"Image size: {image.size}")
        except Exception as e:
            print(f"Invalid base64: {str(e)}")
        
        desc = get_image_description(base64_image)

        db.add_photo(desc, timestamp, filename)

        return {
            "message": "Image received successfully",
        }, 200
       
    except Exception as e:
        print(str(e))
        return {
            "error": str(e)
        }, 400


def get_image_description(base64_string):

    prompt = """I'm looking at an image. Please provide a very detailed description in 3-4 sentences that captures:
        1. The main subject or subjects
        2. Important visual details and context
        3. Any text that might be visible
        4. The overall setting or environment
        
        Make the description detailed enough that someone could recognize this specific scene or object if they encountered it."""
    

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":  f"data:image/jpeg;base64,{base64_string}"
                        },
                    },
                ],
            }
        ]
    )

    return response.choices[0]


@app.route("/response", methods=['POST'])
def process_query():
    data = request.get_json()

    query = data['query']

    try:
       results = db.query_photos(query)
    except Exception as e:
        print(str(e))
        return {
            "errorMessage": "error occurred during db query",
        }, 400

    filename = results['filename']

    file_path = os.path.join("Raspberry-Pi", "captures", filename)

    with open(file_path, 'rb') as f:
        image_bytes = f.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')


    timestamp = results['timestamp']

    json_res = json.dumps(results)


    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Process the prompt with the following context (images with descriptions): " + str(json_res)
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query,
                        },
                    ],
                }
            ]
        )
    except Exception as e:
        print(str(e))
        return {
            "errorMessage": "OpenAI error: " + str(e)
        }, 400
    

    # image, timestamp, content
    
    return {
        "image": base64_image,
        "timestamp": timestamp,
        "content": response.choices[0].message
    }

    

        


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000)