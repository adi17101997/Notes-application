from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
import traceback
import json
from dotenv import load_dotenv
import bcrypt
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# MongoDB connection - simplified approach
try:
    from pymongo import MongoClient
    from bson import ObjectId
    
    # Get MongoDB connection string
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'notes_app')
    
    # Create client and get database
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DATABASE_NAME]
    
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connection established successfully")
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    db = None

def convert_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None
    
    if isinstance(doc, dict):
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = convert_mongo_doc(value)
            elif isinstance(value, list):
                result[key] = [convert_mongo_doc(item) for item in value]
            else:
                result[key] = value
        return result
    elif isinstance(doc, list):
        return [convert_mongo_doc(item) for item in doc]
    else:
        return doc

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'})

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    try:
        print("=== REGISTRATION START ===")
        
        if db is None:
            print("❌ Database not available")
            return jsonify({'message': 'Database not available'}), 500
            
        # Get request data
        if not request.is_json:
            print("❌ Request is not JSON")
            return jsonify({'message': 'Request must be JSON'}), 400
            
        data = request.get_json()
        print(f"📝 Registration data received: {data}")
        
        # Validate required fields
        required_fields = ['user_name', 'user_email', 'password']
        if not all(field in data for field in required_fields):
            missing = [field for field in required_fields if field not in data]
            print(f"❌ Missing fields: {missing}")
            return jsonify({'message': f'Missing required fields: {missing}'}), 400
        
        # Check if user already exists
        print(f"🔍 Checking if user exists: {data['user_email']}")
        existing_user = db.users.find_one({'user_email': data['user_email']})
        if existing_user:
            print(f"❌ User already exists: {data['user_email']}")
            return jsonify({'message': 'User with this email already exists'}), 409
        
        # Hash password
        print("🔐 Hashing password...")
        try:
            hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
            hashed_password_str = hashed_password.decode('utf-8')
            print("✅ Password hashed successfully")
        except Exception as hash_error:
            print(f"❌ Password hashing failed: {hash_error}")
            return jsonify({'message': 'Password processing failed'}), 500
        
        # Create user document
        user_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        user_doc = {
            'user_id': user_id,
            'user_name': data['user_name'],
            'user_email': data['user_email'],
            'password': hashed_password_str,
            'created_on': current_time,
            'last_update': current_time
        }
        
        print(f"👤 User document prepared: {user_id}")
        
        # Insert user into database
        print("💾 Inserting user into database...")
        try:
            result = db.users.insert_one(user_doc)
            print(f"✅ User inserted with MongoDB ID: {result.inserted_id}")
        except Exception as db_error:
            print(f"❌ Database insert failed: {db_error}")
            return jsonify({'message': 'Failed to save user to database'}), 500
        
        # Create JWT token
        print("🎫 Creating JWT token...")
        try:
            access_token = create_access_token(identity=user_id)
            print("✅ JWT token created successfully")
        except Exception as jwt_error:
            print(f"❌ JWT token creation failed: {jwt_error}")
            # User was created but token failed - return partial success
            return jsonify({
                'message': 'User created successfully but token generation failed',
                'user_id': user_id,
                'user_name': data['user_name'],
                'user_email': data['user_email'],
                'warning': 'Please contact support for token generation'
            }), 201
        
        # Prepare response
        response_user = {
            'user_id': user_id,
            'user_name': data['user_name'],
            'user_email': data['user_email'],
            'created_on': current_time.isoformat(),
            'last_update': current_time.isoformat()
        }
        
        print("✅ Registration completed successfully")
        print("=== REGISTRATION END ===")
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'token_type': 'bearer',
            'user': response_user
        }), 201
        
    except Exception as e:
        print(f"❌ REGISTRATION CRITICAL ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'message': 'Internal server error during registration'}), 500

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    try:
        print("=== LOGIN START ===")
        
        if db is None:
            print("❌ Database not available")
            return jsonify({'message': 'Database not available'}), 500
            
        # Get request data
        if not request.is_json:
            print("❌ Request is not JSON")
            return jsonify({'message': 'Request must be JSON'}), 400
            
        data = request.get_json()
        print(f"🔑 Login attempt for email: {data.get('user_email', 'unknown')}")
        
        # Validate required fields
        required_fields = ['user_email', 'password']
        if not all(field in data for field in required_fields):
            missing = [field for field in required_fields if field not in data]
            print(f"❌ Missing fields: {missing}")
            return jsonify({'message': f'Missing required fields: {missing}'}), 400
        
        # Find user by email
        print(f"🔍 Looking up user: {data['user_email']}")
        user = db.users.find_one({'user_email': data['user_email']})
        if not user:
            print(f"❌ User not found: {data['user_email']}")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        print(f"✅ User found: {user.get('user_name', 'Unknown')}")
        
        # Check password
        print("🔐 Verifying password...")
        try:
            stored_password = user.get('password', '')
            if not stored_password:
                print("❌ No password stored for user")
                return jsonify({'message': 'Invalid credentials'}), 401
                
            if not bcrypt.checkpw(data['password'].encode('utf-8'), stored_password.encode('utf-8')):
                print("❌ Password verification failed")
                return jsonify({'message': 'Invalid credentials'}), 401
                
            print("✅ Password verified successfully")
        except Exception as pwd_error:
            print(f"❌ Password verification error: {pwd_error}")
            return jsonify({'message': 'Password verification failed'}), 500
        
        # Create JWT token
        print("🎫 Creating JWT token...")
        try:
            access_token = create_access_token(identity=user['user_id'])
            print("✅ JWT token created successfully")
        except Exception as jwt_error:
            print(f"❌ JWT token creation failed: {jwt_error}")
            return jsonify({'message': 'Login failed due to token generation error'}), 500
        
        # Prepare response
        response_user = {
            'user_id': user['user_id'],
            'user_name': user['user_name'],
            'user_email': user['user_email'],
            'created_on': user['created_on'].isoformat() if hasattr(user['created_on'], 'isoformat') else str(user['created_on']),
            'last_update': user['last_update'].isoformat() if hasattr(user['last_update'], 'isoformat') else str(user['last_update'])
        }
        
        print(f"✅ Login successful for user: {user['user_id']}")
        print("=== LOGIN END ===")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'token_type': 'bearer',
            'user': response_user
        }), 200
        
    except Exception as e:
        print(f"❌ LOGIN CRITICAL ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'message': 'Internal server error during login'}), 500

@app.route('/api/v1/notes', methods=['GET'])
@jwt_required()
def get_notes():
    try:
        print("=== GET NOTES START ===")
        
        if db is None:
            print("❌ Database not available")
            return jsonify({'message': 'Database not available'}), 500
        
        # Get user ID from JWT token
        current_user_id = get_jwt_identity()
        print(f"🔍 Getting notes for user: {current_user_id}")
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').strip()
        
        print(f"📄 Page: {page}, Per page: {per_page}, Search: '{search}'")
        
        # Build query
        query = {'user_id': current_user_id}
        if search:
            query['$or'] = [
                {'note_title': {'$regex': search, '$options': 'i'}},
                {'note_content': {'$regex': search, '$options': 'i'}}
            ]
        
        # Calculate skip value
        skip = (page - 1) * per_page
        
        # Get total count
        total_notes = db.notes.count_documents(query)
        print(f"📊 Total notes found: {total_notes}")
        
        # Get notes with pagination
        notes_cursor = db.notes.find(query).sort('last_update', -1).skip(skip).limit(per_page)
        notes = list(notes_cursor)
        
        # Convert MongoDB objects to JSON-serializable format
        serializable_notes = []
        for note in notes:
            # Convert MongoDB document to JSON-serializable format
            clean_note = convert_mongo_doc(note)
            
            # Ensure note has the correct field names for frontend compatibility
            if 'title' in clean_note and 'note_title' not in clean_note:
                clean_note['note_title'] = clean_note.pop('title')
            if 'content' in clean_note and 'note_content' not in clean_note:
                clean_note['note_content'] = clean_note.pop('content')
            
            serializable_notes.append(clean_note)
        
        print(f"✅ Retrieved {len(serializable_notes)} notes")
        print("=== GET NOTES END ===")
        
        return jsonify({
            'notes': serializable_notes,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_notes,
                'pages': (total_notes + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        print(f"❌ GET NOTES CRITICAL ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'message': 'Internal server error while fetching notes'}), 500

@app.route('/api/v1/notes', methods=['POST'])
@jwt_required()
def create_note():
    try:
        print("=== CREATE NOTE START ===")
        
        if db is None:
            print("❌ Database not available")
            return jsonify({'message': 'Database not available'}), 500
        
        # Get user ID from JWT token
        current_user_id = get_jwt_identity()
        print(f"👤 Creating note for user: {current_user_id}")
        
        # Get request data
        if not request.is_json:
            print("❌ Request is not JSON")
            return jsonify({'message': 'Request must be JSON'}), 400
        
        data = request.get_json()
        print(f"📝 Note data received: {data}")
        
        # Handle both old and new field names for backward compatibility
        title = data.get('note_title') or data.get('title')
        content = data.get('note_content') or data.get('content')
        
        # Validate required fields
        if not title or not content:
            missing = []
            if not title:
                missing.append('note_title (or title)')
            if not content:
                missing.append('note_content (or content)')
            print(f"❌ Missing fields: {missing}")
            return jsonify({'message': f'Missing required fields: {missing}'}), 400
        
        # Create note document
        note_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        note_doc = {
            'note_id': note_id,
            'user_id': current_user_id,
            'note_title': title,
            'note_content': content,
            'created_on': current_time,
            'last_update': current_time
        }
        
        print(f"📝 Note document prepared: {note_id}")
        
        # Insert note into database
        print("💾 Inserting note into database...")
        try:
            result = db.notes.insert_one(note_doc)
            print(f"✅ Note inserted with MongoDB ID: {result.inserted_id}")
        except Exception as db_error:
            print(f"❌ Database insert failed: {db_error}")
            return jsonify({'message': 'Failed to save note to database'}), 500
        
        # Prepare response
        response_note = {
            'note_id': note_id,
            'user_id': current_user_id,
            'note_title': title,
            'note_content': content,
            'created_on': current_time.isoformat(),
            'last_update': current_time.isoformat()
        }
        
        print("✅ Note created successfully")
        print("=== CREATE NOTE END ===")
        
        return jsonify({
            'message': 'Note created successfully',
            'note': response_note
        }), 201
        
    except Exception as e:
        print(f"❌ CREATE NOTE CRITICAL ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'message': 'Internal server error while creating note'}), 500

@app.route('/api/v1/notes/<note_id>', methods=['PUT'])
@jwt_required()
def update_note(note_id):
    try:
        print(f"=== UPDATE NOTE START: {note_id} ===")
        
        # Validate note_id
        if not note_id or note_id == 'undefined' or note_id == 'null':
            print(f"❌ Invalid note_id: {note_id}")
            return jsonify({'message': 'Invalid note ID'}), 400
        
        if db is None:
            print("❌ Database not available")
            return jsonify({'message': 'Database not available'}), 500
        
        # Get user ID from JWT token
        current_user_id = get_jwt_identity()
        print(f"👤 Updating note for user: {current_user_id}")
        
        # Get request data
        if not request.is_json:
            print("❌ Request is not JSON")
            return jsonify({'message': 'Request must be JSON'}), 400
        
        data = request.get_json()
        print(f"📝 Update data received: {data}")
        
        # Handle both old and new field names for backward compatibility
        title = data.get('note_title') or data.get('title')
        content = data.get('note_content') or data.get('content')
        
        # Validate required fields
        if not title or not content:
            missing = []
            if not title:
                missing.append('note_title (or title)')
            if not content:
                missing.append('note_content (or content)')
            print(f"❌ Missing fields: {missing}")
            return jsonify({'message': f'Missing required fields: {missing}'}), 400
        
        # Find and update note
        print(f"🔍 Looking for note: {note_id}")
        note = db.notes.find_one({'note_id': note_id, 'user_id': current_user_id})
        
        if not note:
            print(f"❌ Note not found or access denied: {note_id}")
            return jsonify({'message': 'Note not found or access denied'}), 404
        
        print(f"✅ Note found: {note.get('note_title', 'Unknown')}")
        
        # Update note
        current_time = datetime.utcnow()
        update_data = {
            'note_title': title,
            'note_content': content,
            'last_update': current_time
        }
        
        print("💾 Updating note in database...")
        try:
            result = db.notes.update_one(
                {'note_id': note_id, 'user_id': current_user_id},
                {'$set': update_data}
            )
            
            if result.modified_count == 0:
                print("❌ Note update failed")
                return jsonify({'message': 'Failed to update note'}), 500
            
            print("✅ Note updated successfully")
        except Exception as db_error:
            print(f"❌ Database update failed: {db_error}")
            return jsonify({'message': 'Failed to update note in database'}), 500
        
        # Prepare response
        response_note = {
            'note_id': note_id,
            'user_id': current_user_id,
            'note_title': title,
            'note_content': content,
            'created_on': convert_mongo_doc(note['created_on']),
            'last_update': current_time.isoformat()
        }
        
        print("✅ Note update completed successfully")
        print("=== UPDATE NOTE END ===")
        
        return jsonify({
            'message': 'Note updated successfully',
            'note': response_note
        }), 200
        
    except Exception as e:
        print(f"❌ UPDATE NOTE CRITICAL ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'message': 'Internal server error while updating note'}), 500

@app.route('/api/v1/notes/<note_id>', methods=['DELETE'])
@jwt_required()
def delete_note(note_id):
    try:
        print(f"=== DELETE NOTE START: {note_id} ===")
        
        # Validate note_id
        if not note_id or note_id == 'undefined' or note_id == 'null':
            print(f"❌ Invalid note_id: {note_id}")
            return jsonify({'message': 'Invalid note ID'}), 400
        
        if db is None:
            print("❌ Database not available")
            return jsonify({'message': 'Database not available'}), 500
        
        # Get user ID from JWT token
        current_user_id = get_jwt_identity()
        print(f"👤 Deleting note for user: {current_user_id}")
        
        # Find note first
        print(f"🔍 Looking for note: {note_id}")
        note = db.notes.find_one({'note_id': note_id, 'user_id': current_user_id})
        
        if not note:
            print(f"❌ Note not found or access denied: {note_id}")
            return jsonify({'message': 'Note not found or access denied'}), 404
        
        print(f"✅ Note found: {note.get('note_title', 'Unknown')}")
        
        # Delete note
        print("🗑️ Deleting note from database...")
        try:
            result = db.notes.delete_one({'note_id': note_id, 'user_id': current_user_id})
            
            if result.deleted_count == 0:
                print("❌ Note deletion failed")
                return jsonify({'message': 'Failed to delete note'}), 500
            
            print("✅ Note deleted successfully")
        except Exception as db_error:
            print(f"❌ Database deletion failed: {db_error}")
            return jsonify({'message': 'Failed to delete note from database'}), 500
        
        print("✅ Note deletion completed successfully")
        print("=== DELETE NOTE END ===")
        
        return jsonify({
            'message': 'Note deleted successfully'
        }), 200
        
    except Exception as e:
        print(f"❌ DELETE NOTE CRITICAL ERROR: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'message': 'Internal server error while deleting note'}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask FIXED server...")
    print(f"JWT Secret: {app.config['JWT_SECRET_KEY']}")
    print(f"Database: {db}")
    print(f"MongoDB URI: {os.getenv('MONGO_URI', 'mongodb://localhost:27017/')}")
    print(f"Database Name: {os.getenv('DATABASE_NAME', 'notes_app')}")
    app.run(debug=True, host='0.0.0.0', port=5000)
