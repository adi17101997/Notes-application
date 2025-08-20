#!/usr/bin/env python3
"""
Simple MongoDB connection test script
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        # Get MongoDB connection string
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        database_name = os.getenv('DATABASE_NAME', 'notes_app')
        
        print(f"Attempting to connect to MongoDB...")
        print(f"URI: {mongo_uri}")
        print(f"Database: {database_name}")
        
        # Create client
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get database
        db = client[database_name]
        print(f"✅ Database '{database_name}' accessible")
        
        # List collections
        collections = db.list_collection_names()
        print(f"✅ Collections: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("Testing MongoDB connection...")
    success = test_mongodb_connection()
    
    if not success:
        print("\n🔧 Troubleshooting tips:")
        print("1. Install MongoDB Community Server")
        print("2. Start MongoDB service")
        print("3. Check if MongoDB is running on port 27017")
        print("4. Use MongoDB Atlas (free cloud service)")
