# Chat Room Message Filter - Backend API

FastAPI backend server for real-time chat room application with automatic profanity filtering using ANTLR and SQLite persistence.

## Requirements

- Python 3.8+
- pip
- Virtual environment (recommended)

## Installation

### From Root Project Directory
```bash
# Using npm
npm install
```

### Manual Setup
```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run server
python main.py
```

Server runs on `http://localhost:8000`

## Database

- **Type**: SQLite
- **Default**: Creates `chat.db` in backend directory on first run
- **Tables**: users, rooms, messages, banned_users
- **Persistence**: All data persists across server restarts
- **Initialization**: Runs `init_db()` on startup to create tables
- **Default Rooms**: 6 sample rooms created automatically

## API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Main Endpoints

### Authentication
- `GET /login` - Login page
- `GET /register` - Registration page
- `POST /login` - Login with username/password
- `POST /register` - Create new account

### Chat Rooms
- `GET /rooms` - Get all rooms
- `POST /rooms` - Create new room
- `GET /rooms/{room_id}` - Get room details
- `DELETE /rooms/{room_id}` - Delete room (admin only)
- `GET /rooms/{room_id}/users` - List users in room
- `GET /rooms/{room_id}/messages` - Get message history (limit param available)

### Users
- `POST /users` - Create user
- `POST /users/{user_id}/join-room` - Join room
- `POST /users/{user_id}/leave-room/{room_id}` - Leave room
- `GET /rooms/{room_id}/users` - List room users
- `POST /users/{user_id}/kick/{target_user_id}/room/{room_id}` - Kick user (admin)
- `POST /users/{user_id}/ban/{target_user_id}` - Ban user (admin)
- `POST /users/{user_id}/unban/{target_user_id}` - Unban user (admin)

### Messages
- `POST /rooms/{room_id}/messages` - Send message
- `GET /rooms/{room_id}/messages?limit=50` - Get message history
- `WebSocket /ws/{room_id}/{user_id}` - Real-time WebSocket chat

### Bad Words Management
- `GET /bad-words` - Get bad words list (admin only)
- `POST /bad-words` - Add bad word (admin only)
- `DELETE /bad-words/{word}` - Delete bad word (admin only)

### System
- `GET /health` - Health check
- `GET /` - Root (redirects to login)
- `GET /docs` - API documentation (Swagger)
- `GET /redoc` - API documentation (ReDoc)

## Usage Examples

### 1. Register User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "secure_password"
  }'
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "secure_password"
  }'
```

### 3. Get All Rooms
```bash
curl "http://localhost:8000/rooms"
```

### 4. Get Room Messages
```bash
curl "http://localhost:8000/rooms/room1/messages?limit=10"
```

### 5. Send Message (HTTP)
```bash
curl -X POST "http://localhost:8000/rooms/room1/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "room1",
    "user_id": "user1",
    "username": "alice",
    "text": "Hello everyone! This is fun!"
  }'
```

### 6. WebSocket Real-time Chat
```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8000/ws/room1/user1");

// Receive messages
ws.onmessage = function(event) {
  const message = JSON.parse(event.data);
  console.log(`${message.username}: ${message.text}`);
};

// Send message
ws.send(JSON.stringify({
  text: "Hello from WebSocket! Bad words like damn will be filtered."
}));

// Handle connection close
ws.onclose = function() {
  console.log("WebSocket connection closed");
};
```

### 7. Join Room
```bash
curl -X POST "http://localhost:8000/users/user1/join-room" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "room1",
    "user_id": "user1",
    "username": "alice"
  }'
```

### 8. Leave Room
```bash
curl -X POST "http://localhost:8000/users/user1/leave-room/room1"
```

## Features

✅ **Room Management** - Create, browse, delete rooms
✅ **User Management** - Register, login, join/leave rooms, ban/unban
✅ **Messages** - HTTP REST API and WebSocket real-time chat
✅ **Profanity Filtering** - ANTLR-based with automatic word replacement
✅ **Role-based Access** - User vs Admin roles
✅ **SQLite Persistence** - All data stored persistently
✅ **Authentication** - SHA256 password hashing with JWT tokens
✅ **User Presence** - Real-time user list in each room
✅ **Default Rooms** - 6 sample rooms created on startup

## Project Structure

```
backend/
├── main.py                 # FastAPI main server & WebSocket manager
├── bad_word_filter.py      # ANTLR filter + fallback list-based
├── db.py                   # SQLite database operations
├── auth.py                 # JWT & role validation
├── models.py               # Pydantic data models
├── create_admin.py         # Script to create admin user
├── bad_words.txt           # Bad words list (one per line)
├── requirements.txt        # Python dependencies
├── chat.db                 # SQLite database (created at runtime)
└── antlr/                  # ANTLR grammar files
    ├── BadWords.g4         # Grammar definition
    ├── run.py              # Grammar compilation script
    └── CompiledFiles/      # Generated lexer/parser
```

## Message Filtering

Bad words are loaded from `bad_words.txt` at startup:
- **Format**: One word per line, comments start with `#`
- **Processing**: ANTLR tokenization (primary) + fallback list matching
- **Replacement**: All matched bad words replaced with `***`
- **Case-insensitive**: Filtering ignores case
- **Dynamic**: Update `bad_words.txt` anytime; restart server to reload

Example `bad_words.txt`:
```
# Sample bad words
idiot
stupid
damn
offensive_phrase
```

## Running the Application

### Option 1: Using npm (Recommended)
```bash
# From root project directory
npm start
```
This starts both backend (port 8000) and frontend (port 3000) concurrently.

### Option 2: Manual - Backend Only
```bash
cd backend
python main.py
```

## Notes

- Backend uses **SQLite** for persistent data storage
- Data survives server restarts
- Default rooms are created on first startup
- WebSocket connections require frontend connection
- Admin role needed for: ban/unban, kick users, manage bad words
- Password is hashed using SHA256 (consider bcrypt for production)
- For production deployment, consider:
  - Switching to PostgreSQL
  - Using bcrypt for password hashing
  - Implementing rate limiting
  - Adding HTTPS/WSS
  - Adding request validation & sanitization
