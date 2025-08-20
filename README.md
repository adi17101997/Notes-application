# NotesApp Backend

A FastAPI-based backend for the NotesApp, featuring user authentication, note management, and SQLite database.

## Features

- 🔐 JWT-based authentication
- 📝 Full CRUD operations for notes
- 🗄️ SQLite database (no external setup required)
- 📚 Auto-generated API documentation
- 🚀 Fast and lightweight

## Quick Start

### Option 1: Automatic Setup (Recommended)

```bash
# Run the setup script
python setup.py

# Start the application
python run.py
```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Environment File**
   ```bash
   cp env.example .env
   # Edit .env if needed
   ```

3. **Start the Application**
   ```bash
   python run.py
   ```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user info

### Notes
- `GET /api/v1/notes` - Get user notes (with pagination)
- `POST /api/v1/notes` - Create new note
- `GET /api/v1/notes/{id}` - Get specific note
- `PUT /api/v1/notes/{id}` - Update note
- `DELETE /api/v1/notes/{id}` - Delete note
- `GET /api/v1/notes/stats/count` - Get notes count

## Database

The app uses SQLite by default, which creates a `notesapp.db` file in the backend directory. No external database setup is required.

### Database Schema

**Users Table:**
- `user_id` (UUID, Primary Key)
- `user_name` (VARCHAR 100)
- `user_email` (VARCHAR 255, Unique)
- `password` (VARCHAR 255, Hashed)
- `created_on` (DateTime)
- `last_update` (DateTime)

**Notes Table:**
- `note_id` (UUID, Primary Key)
- `note_title` (VARCHAR 255)
- `note_content` (TEXT)
- `user_id` (UUID, Foreign Key)
- `created_on` (DateTime)
- `last_update` (DateTime)

## Environment Variables

Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./notesapp.db
SECRET_KEY=your-secret-key-change-in-production
FRONTEND_URL=http://localhost:5173
```

## Docker Support

When Docker is available, you can run:

```bash
docker-compose up --build
```

## Development

### Running with Auto-reload
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Health Check
- Health endpoint: http://localhost:8000/health

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   └── notes.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── database/
│   │   └── connection.py
│   ├── models/
│   │   ├── user.py
│   │   └── note.py
│   ├── schemas/
│   │   ├── user.py
│   │   └── note.py
│   ├── services/
│   │   ├── user_service.py
│   │   └── note_service.py
│   └── main.py
├── requirements.txt
├── run.py
├── setup.py
└── docker-compose.yml
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change the port in `run.py` or use a different port
   - Kill the process using the port: `lsof -ti:8000 | xargs kill -9`

2. **Database Issues**
   - Delete `notesapp.db` file and restart (will recreate tables)
   - Check file permissions in the backend directory

3. **Import Errors**
   - Ensure you're in the backend directory
   - Check that all dependencies are installed

### Logs

The application logs to the console. For production, consider using a proper logging configuration.

## Security Notes

- Change the `SECRET_KEY` in production
- Use HTTPS in production
- Consider rate limiting for production use
- The current setup is for development purposes

## License

This project is part of a full-stack development assignment.