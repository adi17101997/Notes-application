from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection string
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'notes_app')

# Global client variable
_client = None
_database = None

def get_client():
    """Get MongoDB client instance"""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client

def get_database():
    """Get database instance"""
    global _database
    if _database is None:
        client = get_client()
        _database = client[DATABASE_NAME]
    return _database

def close_connection():
    """Close MongoDB connection"""
    global _client
    if _client:
        _client.close()
        _client = None
        _database = None

def init_database():
    """Initialize database with required collections and indexes"""
    db = get_database()
    
    # Create collections if they don't exist
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
    
    if 'notes' not in db.list_collection_names():
        db.create_collection('notes')
    
    # Create indexes for better performance
    db.users.create_index('user_email', unique=True)
    db.users.create_index('user_id')
    db.notes.create_index('user_id')
    db.notes.create_index('note_id')
    db.notes.create_index([('user_id', 1), ('last_update', -1)])
    
    print("Database initialized successfully")

if __name__ == '__main__':
    # Test database connection
    try:
        init_database()
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
    finally:
        close_connection()
