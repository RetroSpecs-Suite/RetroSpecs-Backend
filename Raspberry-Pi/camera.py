import cv2
import time
#import requests
from datetime import datetime
import os
import logging
import hashlib
from pathlib import Path

def compute_dhash(frame, hash_size=8):
    """
    Compute the difference hash  of an image
    """
    # Convert to grayscale and resize
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (hash_size + 1, hash_size))
    
    # Compute differences between adjacent pixels
    diff = resized[:, 1:] > resized[:, :-1]
    
    # Convert binary array to hash
    return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

def calculate_hash_similarity(hash1, hash2):
    """
    Calculate similarity between two hashes using Hamming distance
    Returns a value between 0 (identical) and 64 (completely different)
    """
    return bin(hash1 ^ hash2).count('1')

class CameraUploader:
    def __init__(self, api_endpoint, camera_id=0, save_local=False, local_path="./captures", cache_size=25, similarity_threshold=5):
        """
        Initialize the camera and uploader
        api_endpoint: URL where images will be sent
        camera_id: Camera device ID (usually 0 for first USB camera)
        save_local: Whether to save images locally
        local_path: Directory to save images if save_local is True
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.camera = cv2.VideoCapture(camera_id)
        
        if not self.camera.isOpened():
            raise RuntimeError("Failed to open camera. Check if it's connected properly.")
            
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) 
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
        self.api_endpoint = api_endpoint
        self.save_local = save_local
        self.local_path = Path(local_path)

        self.recent_hashes = []
        self.cache_size = cache_size
        self.similarity_threshold = similarity_threshold
        
        if save_local:
            self.local_path.mkdir(exist_ok=True)
    
    def capture_image(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            # Capture frame
            ret, frame = self.camera.read()
            
            if not ret:
                self.logger.error("Failed to capture image from camera")
                return None, None
            
            # Check for duplicate
            if not self.is_image_unique(frame):
                self.logger.info(f"Non-unique image: {timestamp}")
                return None, None
            
            # Convert frame to bytes
            _, img_encoded = cv2.imencode('.jpg', frame)
            img_bytes = img_encoded.tobytes()
            
            # Save locally
            if self.save_local:
                img_path = self.local_path / f"image_{timestamp}.jpg"
                with open(img_path, 'wb') as f:
                    f.write(img_bytes)
                
            return img_bytes, timestamp
            
        except Exception as e:
            self.logger.error(f"Error capturing image: {str(e)}")
            return None, None
    
    def is_image_unique(self, frame):
        current_hash = compute_dhash(frame)
        
        # Compare with recent hashes
        for recent_hash in self.recent_hashes:
            difference = calculate_hash_similarity(current_hash, recent_hash)
            self.logger.info(f"Threshold: {difference}")
            if difference <= self.similarity_threshold:
                return False
        
        # Update recent hashes list
        self.recent_hashes.append(current_hash)
        if len(self.recent_hashes) > self.cache_size:
            self.recent_hashes.pop(0)  # Remove oldest hash
            
        return True
    
    def run(self, interval=5.0):
        """
        Main loop to capture and upload images
        interval: Time between captures in seconds
        """
        self.logger.info("Starting capture and upload loop...")
        
        try:
            while True:
                start_time = time.time()
                
                # Capture and upload image
                img_bytes, timestamp = self.capture_image()
                if img_bytes:
                    self.upload_image(img_bytes, timestamp)
                
                # Wait for remainder of interval
                elapsed_time = time.time() - start_time
                sleep_time = max(0, interval - elapsed_time)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("Stopping capture and upload loop...")
            self.camera.release()

if __name__ == "__main__":
    API_ENDPOINT = "https://your-api-endpoint.com/upload"
    uploader = CameraUploader(
        api_endpoint=API_ENDPOINT,
        camera_id=0,  # Usually 0 for first USB camera
        save_local=True,  
        local_path="./captures",
        similarity_threshold=25
    )

    img_bytes, timestamp = uploader.capture_image()
    print(timestamp)
    time.sleep(3)
    img_bytes, timestamp = uploader.capture_image()
    if img_bytes:
        print("nooo")
    print(timestamp)