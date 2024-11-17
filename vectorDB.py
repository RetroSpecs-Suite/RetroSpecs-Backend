import base64
import os
from datetime import datetime
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import json

class VectorDB:
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="photo_memory_db"
        ))
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="photo_memories",
            metadata={"hnsw:space": "cosine"}
        )
