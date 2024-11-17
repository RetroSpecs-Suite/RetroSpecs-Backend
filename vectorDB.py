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

    def demo_init(self):
        desc1='The image shows a person holding a fried chicken sandwich, likely from Popeyes, in one hand. The sandwich appears golden-brown, with visible crispy breading, suggesting freshly fried chicken. In the background, there is a large white paper bag featuring the Popeyes logo and the text "Popeyes Rewards" in bright orange, accompanied by the tagline "Download. Join. Earn. Enjoy." Additional branding includes small orange graphics, including a squirrel. The setting is a modern kitchen with a granite countertop, a stainless steel sink, and various items such as a jar of PB Fit powdered peanut butter, a bottle of alcohol, and other household objects visible. On the counter near the bag lies an opened sandwich wrapper, also featuring orange branding. A laptop, displaying text or code on its screen, is placed on the counter in the foreground, suggesting the person might be working or programming while eating. The scene feels casual and lived-in, combining work with a meal break.'
        image1='eating.jpg'
        desc2='The image shows a person seated at a table with a laptop in the background while another hand prominently holds a white bottle labeled "Allergy Aller-Tec" from Kirkland Signature. The label includes additional text, such as "Antihistamine / Cetirizine Hydrochloride" and "24 Hour Relief," with further details like "Indoor & Outdoor Allergies" and "365 Tablets." The bottle has a green cap and is designed for easy recognition as an over-the-counter allergy medication. The setting appears to be a casual, indoor environment, possibly a shared workspace or a dining area, given the presence of laptops, a white water bottle, and miscellaneous items like cleaning supplies and electronics in the background. The countertop is granite, suggesting a kitchen or multipurpose area. The person behind the laptop wears a dark T-shirt with visible text, though the main focus remains on the interaction with the allergy medication in the foreground.'
        image2='medicine.jpg'
        desc3='The image depicts an open dishwasher filled with various kitchen items and utensils. In the lower rack, there is a mix of dishes, including a large white plate, a plastic food storage container with blue handles, and a metal colander. The upper rack contains a black utensil basket holding several kitchen tools such as orange and yellow-handled tongs, a ladle, and other utensils. The background features dark-colored cabinets and a granite countertop, with part of the kitchen floor visible, consisting of light wood or laminate material. The scene conveys a typical domestic environment, specifically a kitchen, where dishes and utensils are being cleaned or put away.'
        image3='dishes.jpg'
        desc4='The image shows the interior of an open freezer, stocked with various frozen food items. On the top shelf, there is a bag of Tyson frozen chicken breast tenderloins on the right, alongside a package labeled "Organic Mixed Vegetables" from an iO brand. A small carton of Cedar Crest ice cream in the "Caramel Collision" flavor is prominently placed near the front. Additional items include a blue bag labeled "Tru," possibly frozen fruit or dessert, and what appears to be a loaf of bread stored in a transparent bag. The bottom shelf contains individually wrapped frozen meats or seafood, with a visible clear plastic wrap encasing a large piece of meat. The freezer door interior shows white plastic shelves, and the surrounding environment features stainless steel appliances and dark cabinetry, typical of a modern kitchen. A roll of paper towels is partially visible on a granite countertop adjacent to the freezer, further grounding the scene in a domestic setting.'
        image4='freezer.jpg'
        desc5='The image shows a workspace on a granite kitchen countertop. In the foreground, a set of keys with a Wisconsin Badgers lanyard lies next to a black key fob and a brass-colored keychain with text in another language. A large white water bottle is prominently placed in the center, partially obstructing the view of an open laptop on the right. The laptop screen displays a Discord server with multiple channels, and a graphic is visible featuring a stylized leaf or feather logo with text that is not fully readable but seems to include "Tea House." The left edge of the image shows part of another laptop screen with a software window open, possibly for video editing. The environment appears to be casual, likely a kitchen or dining area, given the setting on a stone countertop.'
        image5='keys.jpg'

        self.add_photo(desc1, 20241116_195713, image1)
        self.add_photo(desc2, 20241116_195714, image2)
        self.add_photo(desc3, 20241116_195715, image3)
        self.add_photo(desc4, 20241116_195716, image4)
        self.add_photo(desc5, 20241116_195717, image5)

        print('Vector DB is loaded...')

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
            n_results=3
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

    desc1='The image shows a person holding a fried chicken sandwich, likely from Popeyes, in one hand. The sandwich appears golden-brown, with visible crispy breading, suggesting freshly fried chicken. In the background, there is a large white paper bag featuring the Popeyes logo and the text "Popeyes Rewards" in bright orange, accompanied by the tagline "Download. Join. Earn. Enjoy." Additional branding includes small orange graphics, including a squirrel. The setting is a modern kitchen with a granite countertop, a stainless steel sink, and various items such as a jar of PB Fit powdered peanut butter, a bottle of alcohol, and other household objects visible. On the counter near the bag lies an opened sandwich wrapper, also featuring orange branding. A laptop, displaying text or code on its screen, is placed on the counter in the foreground, suggesting the person might be working or programming while eating. The scene feels casual and lived-in, combining work with a meal break.'
    desc2='This image depicts a casual indoor scene. Here’s a description: A person in an orange shirt is sitting on a black armchair, seemingly focused on something while wearing glasses and possibly headphones. The room appears to be a residential or dormitory setting, with minimal decorations. A side table next to the armchair has several items, including: Cardboard boxes (possibly snack or food packaging). A smartphone lying flat. In the foreground, two individuals are partially visible, wearing dark shirts. Their torsos frame the sides of the image. A white wall and doorway are in the background, along with a window reflecting indoor lighting. The overall environment suggests a relaxed, informal atmosphere. No visible business names, branding, or location-identifying features are present.'
    app.add_photo(desc1, 20241116_195713, 'eating.jpg')
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