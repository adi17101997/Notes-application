from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import os
import traceback
from dotenv import load_dotenv
from database.mongo_client import get_database
import bcrypt
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
jwt = JWTManager(app)
CORS(app)

# Get MongoDB database
try:
    db = get_database()
    print("✅ Database connection established")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    db = None

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Flask backend is running'})

# Authentication routes
@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    try:
        if not db:
            return jsonify({'message': 'Database not available'}), 500
            
        data = request.get_json()
        print(f"Registration attempt with data: {data}")
        
        # Validate required fields
        if not all(key in data for key in ['user_name', 'user_email', 'password']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Check if user already exists
        existing_user = db.users.find_one({'user_email': data['user_email']})
        if existing_user:
            return jsonify({'message': 'User with this email already exists'}), 409
        
        # Hash password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        user = {
            'user_id': user_id,
            'user_name': data['user_name'],
            'user_email': data['user_email'],
            'password': hashed_password.decode('utf-8'),
            'created_on': current_time,
            'last_update': current_time
        }
        
        print(f"Inserting user: {user_id}")
        result = db.users.insert_one(user)
        print(f"User inserted with ID: {result.inserted_id}")
        
        # Create access token BEFORE removing password
        try:
            access_token = create_access_token(identity=user_id)
            print(f"JWT token created successfully")
        except Exception as jwt_error:
            print(f"❌ JWT token creation failed: {jwt_error}")
            # Even if JWT fails, user was created successfully
            return jsonify({
                'message': 'User created but token generation failed',
                'user_id': user_id,
                'user_name': user['user_name'],
                'user_email': user['user_email']
            }), 201
        
        # Create response user object with serializable datetimes
        response_user = {
            'user_id': user_id,
            'user_name': user['user_name'],
            'user_email': user['user_email'],
            'created_on': current_time.isoformat(),
            'last_update': current_time.isoformat()
        }
        
        print(f"Registration successful for user: {user_id}")
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'token_type': 'bearer',
            'user': response_user
        }), 201
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    try:
        if not db:
            return jsonify({'message': 'Database not available'}), 500
            
        data = request.get_json()
        print(f"Login attempt for email: {data.get('user_email', 'unknown')}")
        
        # Validate required fields
        if not all(key in data for key in ['user_email', 'password']):
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Find user by email
        user = db.users.find_one({'user_email': data['user_email']})
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Check password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Create access token
        try:
            access_token = create_access_token(identity=user['user_id'])
            print(f"JWT token created successfully for login")
        except Exception as jwt_error:
            print(f"❌ JWT token creation failed during login: {jwt_error}")
            return jsonify({'message': 'Login failed due to token generation error'}), 500
        
        # Create response user object with serializable datetimes
        response_user = {
            'user_id': user['user_id'],
            'user_name': user['user_name'],
            'user_email': user['user_email'],
            'created_on': user['created_on'].isoformat() if hasattr(user['created_on'], 'isoformat') else str(user['created_on']),
            'last_update': user['last_update'].isoformat() if hasattr(user['last_update'], 'isoformat') else str(user['last_update'])
        }
        
        print(f"Login successful for user: {user['user_id']}")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'token_type': 'bearer',
            'user': response_user
        }), 200
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask debug server...")
    print(f"JWT Secret: {app.config['JWT_SECRET_KEY']}")
    print(f"Database: {db}")
    app.run(debug=True, host='0.0.0.0', port=5000)
