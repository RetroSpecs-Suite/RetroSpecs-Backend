import base64
import os
from datetime import datetime
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()

class VectorDB:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Use in-memory ChromaDB client
        self.chroma_client = chromadb.Client()
        
        # Create collection
        self.collection = self.chroma_client.create_collection(
            name="photo_memories"
        )

    def add_photo(self, description: str, timestamp: str, filename: str):
        """Add a photo to the database with its analysis"""
                
        # Create embeddings for the analysis
        embedding_response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=description
        )
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=[embedding_response.data[0].embedding],
            documents=[description],
            metadatas=[{
                "timestamp": timestamp,
                "filename": filename
            }],
            ids=[f"photo_{timestamp}"]
        )

    def query_photos(self, question: str) -> List[Dict]:
        """Query photos based on a natural language question"""
        
        # Create embedding for the question
        query_embedding_response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=question
        )
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding_response.data[0].embedding],
            n_results=1
        )
        
        # Process results
        processed_results = []
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            metadata = results['metadatas'][0][i]
            timestamp = metadata['timestamp']
                
            processed_results.append({
                'timestamp': timestamp,
                'filename': metadata['filename'],
                'description': doc
            })
            
        return processed_results

    def save_database(self):
        """Save the current state of the database"""
        self.chroma_client.persist()

if __name__ == "__main__":
    app = VectorDB()

    desc1='The image depicts a young man enthusiastically eating a large hamburger. The man has a neatly trimmed beard, short dark hair, and is wearing a green plaid shirt. His hands are gripping the burger, which is layered with multiple patties, cheese, and condiments, creating a visibly messy but appetizing look, with some sauce spilling out between the layers. The background is slightly blurred, suggesting an outdoor setting, possibly near a casual eatery, with soft, neutral tones that do not detract from the focus on the man and his meal. No visible text is present in the scene.'
    desc2='This image depicts a casual indoor scene. Here’s a description: A person in an orange shirt is sitting on a black armchair, seemingly focused on something while wearing glasses and possibly headphones. The room appears to be a residential or dormitory setting, with minimal decorations. A side table next to the armchair has several items, including: Cardboard boxes (possibly snack or food packaging). A smartphone lying flat. In the foreground, two individuals are partially visible, wearing dark shirts. Their torsos frame the sides of the image. A white wall and doorway are in the background, along with a window reflecting indoor lighting. The overall environment suggests a relaxed, informal atmosphere. No visible business names, branding, or location-identifying features are present.'
    app.add_photo(desc1, 20241116_195713, 'image_20241116_195713.jpg')
    app.add_photo(desc2, 20241116_195730, 'image_20241116_195730.jpg')

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    results = app.query_photos(
        question="what was i eating earlier?",
    )
    
    # Print results
    for result in results:
        print(f"Time: {result['timestamp']}")
        print(f"File: {result['filename']}")
        print(f"Description: {result['description']}\n")