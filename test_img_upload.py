import requests
import base64

# Read image file and convert to base64
with open('chicago_picture.jpeg', 'rb') as f:
    image_bytes = f.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

# Prepare data
data = {
    'filename': 'chicago_picture.jpg',
    'image': base64_image
}

# Send POST request
response = requests.post(
    'http://localhost:4000/upload_image',
    data=data,
    headers={'Content-Type': 'application/json'}
)

print(response.json())