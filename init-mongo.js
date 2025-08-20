// MongoDB initialization script
db = db.getSiblingDB('notes_app');

// Create collections
db.createCollection('users');
db.createCollection('notes');

// Create indexes for better performance
db.users.createIndex({ "user_email": 1 }, { unique: true });
db.users.createIndex({ "user_id": 1 });
db.notes.createIndex({ "user_id": 1 });
db.notes.createIndex({ "note_id": 1 });
db.notes.createIndex({ "user_id": 1, "last_update": -1 });

print("Database 'notes_app' initialized successfully!");
print("Collections 'users' and 'notes' created with indexes.");
