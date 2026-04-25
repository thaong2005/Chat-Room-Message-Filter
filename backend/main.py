from pathlib import Path
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from typing import Dict, List, Set
from datetime import datetime
from db import get_connection, init_db 

import json
import uuid

from models import (
    User, Message, ChatRoom, BadWord, 
    JoinRoomRequest, SendMessageRequest
)
from bad_word_filter import BadWordFilter, load_bad_words_from_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"


app = FastAPI(title="Chatroom Messenger Filter Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
# rooms: Dict[str, ChatRoom] = {}
# users: Dict[str, User] = {}

# Load bad words from file
bad_words_list = load_bad_words_from_file()
bad_words: List[BadWord] = [
    BadWord(word=word, replacement="***")
    for word in bad_words_list
]

# banned_users: Set[str] = set()

# Initialize ANTLR-based bad word filter
bad_word_filter = BadWordFilter(bad_words_list=bad_words_list)

# Initialize default rooms
def init_default_rooms():
    conn = get_connection()
    cursor = conn.cursor() 
    
    default_rooms = [
        ("room1", "Gaming Central", "Everything from RPGs to FPS", 100, "admin"),
        ("room2", "Developers Den", "React, Python, and more", 50, "admin"),
        ("room3", "Music Theory", "Sharing beats and vibes", 20, "admin"),
        ("room4", "Art & Design", "Showcase your latest work", 60, "admin"),
        ("room5", "Study Group", "Focused work only", 15, "admin"),
        ("room6", "Cinema Talk", "Reviewing the latest hits", 40, "admin"),
    ]
    
    cursor.executemany("""
        INSERT OR IGNORE INTO rooms (id, name, description, max_users, created_by)
        VALUES (?, ?, ?, ?, ?)
    """, default_rooms)

    conn.commit()
    conn.close()

# Initialize default rooms on startup
init_db()
init_default_rooms()

# WebSocket manager for real-time chat
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_json(message)

manager = ConnectionManager()

# Utility function to filter bad words using ANTLR or fallback method
def filter_message(text: str) -> tuple[str, bool]:
    """
    Filter bad words from message using ANTLR or fallback method
    
    Args:
        text: The message text to filter
    
    Returns:
        tuple: (filtered_text, is_filtered)
    """
    filtered, is_filtered, _ = bad_word_filter.filter_message(text)
    return filtered, is_filtered

# ========== LOGIN & REGISTER ENDPOINTS ============

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", tags=["Auth"])
async def login() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "loginPage.html")

@app.get("/register", tags=["Auth"])
async def register() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "registerPage.html")

@app.post("/login", tags=["Auth"])
async def Login(username: str, password: str):
    """Login with username and password"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", (username, password)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if user["is_banned"]:
        raise HTTPException(status_code=403, detail="Your account is banned")

    return {"message": "Login successful!", "user_id": user["id"], "username": user["username"]}    

@app.post("/register", tags=["Auth"])
async def Register(username: str, password: str):
    """ Register new user """
    conn = get_connection()
    cursor = conn.cursor()
   
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Account already exists. Pick another")

    user_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO users (id, username, password, role) VALUES (?, ?, ?, ?)",
        (user_id, username, password, "user")
    )
    conn.commit()
    conn.close()
    return {"message": "Registered successfully!", "username": username}



# ========== ROOM ENDPOINTS ==========

@app.get("/rooms", tags=["Rooms"])
async def get_all_rooms():
    """Get all chat rooms"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms")
    rooms = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rooms

@app.post("/rooms", tags=["Rooms"])
async def create_room(room: ChatRoom):
    """Create a new chat room"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room.id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Room already exists")
    cursor.execute(
        "INSERT INTO rooms (id, name, description, max_users, created_by) VALUES (?, ?, ?, ?, ?)",
        (room.id, room.name, room.description, room.max_users, room.created_by)
    )
    conn.commit()
    conn.close()
    return {"message": "Room created", "room": room}

@app.get("/rooms/{room_id}", tags=["Rooms"])
async def get_room(room_id: str):
    """Get a specific chat room"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
    room = cursor.fetchone()
    conn.close()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return dict(room)

@app.delete("/rooms/{room_id}", tags=["Rooms"])
async def delete_room(room_id: str):
    """Delete a chat room (Admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
    cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
    conn.commit()
    conn.close()
    return {"message": "Room deleted"}

# ========== USER ENDPOINTS ==========

@app.post("/users", tags=["Users"])
async def create_user(user: User):
    """Create a new user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = ?", (user.id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")
    cursor.execute(
        "INSERT INTO users (id, username, password, role) VALUES (?, ?, ?, ?)",
        (user.id, user.username, user.password, user.role)
    )
    conn.commit()
    conn.close()
    return {"message": "User created", "user": user}

@app.post("/users/{user_id}/join-room", tags=["Users"])
async def join_room(user_id: str, request: JoinRoomRequest):
    """Join a chat room"""
    conn = get_connection()
    cursor = conn.cursor()
 
    # Auto-create user if not exists
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (id, username, password, role) VALUES (?, ?, ?, ?)",
            (user_id, request.username, "", "user")
        )
 
    # Check room exists
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (request.room_id,))
    room = cursor.fetchone()
    if not room:
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
 
    # Check if banned
    cursor.execute("SELECT user_id FROM banned_users WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=403, detail="User is banned from this room")
 
    # Check if room is full
    if room["current_users"] >= room["max_users"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Room is full")
 
    # Add user to room if not already in it
    cursor.execute(
        "INSERT OR IGNORE INTO room_users (room_id, user_id) VALUES (?, ?)",
        (request.room_id, user_id)
    )
    # update current_users count from actual rows
    cursor.execute(
        "UPDATE rooms SET current_users = (SELECT COUNT(*) FROM room_users WHERE room_id = ?) WHERE id = ?",
        (request.room_id, request.room_id)
    )
    conn.commit()
 
    cursor.execute("SELECT * FROM rooms WHERE id = ?", (request.room_id,))
    updated_room = dict(cursor.fetchone())
    conn.close()
    return {"message": "Joined room", "room": updated_room}

@app.post("/users/{user_id}/leave-room/{room_id}", tags=["Users"])
async def leave_room(user_id: str, room_id: str):
    """Leave a chat room"""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
 
    cursor.execute("DELETE FROM room_users WHERE room_id = ? AND user_id = ?", (room_id, user_id))
    cursor.execute(
        "UPDATE rooms SET current_users = (SELECT COUNT(*) FROM room_users WHERE room_id = ?) WHERE id = ?",
        (room_id, room_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Left room"}

@app.get("/rooms/{room_id}/users", tags=["Users"])
async def get_room_users(room_id: str):
    """Get list of users in a room"""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
 
    cursor.execute("""
        SELECT u.id, u.username, u.role, u.is_banned
        FROM users u
        JOIN room_users ru ON u.id = ru.user_id
        WHERE ru.room_id = ?
    """, (room_id,))
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

@app.get("/users", tags=["Users"])
async def get_all_users():
    """Get list of all users"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, role, is_banned FROM users ORDER BY username")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {"users": users, "count": len(users)}

@app.post("/users/{user_id}/kick/{target_user_id}/room/{room_id}", tags=["Users"])
async def kick_user(user_id: str, target_user_id: str, room_id: str):
    """Kick a user from a room (Admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "admin":
        conn.close()
        raise HTTPException(status_code=403, detail="Admin privilege required")
 
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
 
    cursor.execute("DELETE FROM room_users WHERE room_id = ? AND user_id = ?", (room_id, target_user_id))
    cursor.execute(
        "UPDATE rooms SET current_users = (SELECT COUNT(*) FROM room_users WHERE room_id = ?) WHERE id = ?",
        (room_id, room_id)
    )
    conn.commit()
    conn.close()
    return {"message": f"User {target_user_id} kicked from room"}

@app.post("/users/{user_id}/ban/{target_user_id}", tags=["Users"])
async def ban_user(user_id: str, target_user_id: str):
    """Ban a user (Admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "admin":
        conn.close()
        raise HTTPException(status_code=403, detail="Admin privilege required")
 
    cursor.execute("INSERT OR IGNORE INTO banned_users (user_id) VALUES (?)", (target_user_id,))
    cursor.execute("UPDATE users SET is_banned = 1 WHERE id = ?", (target_user_id,))
    conn.commit()
    conn.close()
    return {"message": f"User {target_user_id} banned"}

@app.post("/users/{user_id}/unban/{target_user_id}", tags=["Users"])
async def unban_user(user_id: str, target_user_id: str):
    """Unban a user (Admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user or user["role"] != "admin":
        conn.close()
        raise HTTPException(status_code=403, detail="Admin privilege required")
 
    cursor.execute("DELETE FROM banned_users WHERE user_id = ?", (target_user_id,))
    cursor.execute("UPDATE users SET is_banned = 0 WHERE id = ?", (target_user_id,))
    conn.commit()
    conn.close()
    return {"message": f"User {target_user_id} unbanned"}

# ========== MESSAGE ENDPOINTS ==========

@app.post("/rooms/{room_id}/messages", tags=["Messages"])
async def send_message(room_id: str, request: SendMessageRequest):
    """Send a message to a room"""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
 
    cursor.execute("SELECT * FROM users WHERE id = ?", (request.user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    if user["is_banned"]:
        conn.close()
        raise HTTPException(status_code=403, detail="User is banned")
 
    filtered_text, is_filtered = filter_message(request.text)
    message_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
 
    cursor.execute("""
        INSERT INTO messages (id, room_id, user_id, username, text, timestamp, is_filtered)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (message_id, room_id, request.user_id, request.username, filtered_text, timestamp, int(is_filtered)))
    conn.commit()
    conn.close()
    return {"message": "Message sent", "was_filtered": is_filtered}

@app.get("/rooms/{room_id}/messages", tags=["Messages"])
async def get_messages(room_id: str, limit: int = 50):
    """Get messages from a room"""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Room not found")
 
    cursor.execute("""
        SELECT * FROM messages WHERE room_id = ?
        ORDER BY timestamp ASC
        LIMIT ?
    """, (room_id, limit))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

# ========== BAD WORDS ENDPOINTS ==========

@app.get("/bad-words", tags=["BadWords"])
async def get_bad_words(user_id: str):
    """Get list of bad words (Admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    return bad_words

@app.post("/bad-words", tags=["BadWords"])
async def add_bad_word(user_id: str, bad_word: BadWord):
    """Add a bad word (Admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    bad_words.append(bad_word)
    return {"message": "Bad word added", "word": bad_word}

@app.delete("/bad-words/{word}", tags=["BadWords"])
async def remove_bad_word(user_id: str, word: str):
    """Remove a bad word (Admin only)"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    global bad_words
    bad_words = [bw for bw in bad_words if bw.word.lower() != word.lower()]
    return {"message": "Bad word removed"}

# ========== WEBSOCKET (Real-time Chat) ==========

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time chat"""
    conn = get_connection()
    cursor = conn.cursor()
 
    cursor.execute("SELECT id FROM rooms WHERE id = ?", (room_id,))
    if not cursor.fetchone():
        conn.close()
        await websocket.close(code=1008, reason="Room not found")
        return
 
    # Auto-create guest user if not in DB
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        username = f"User_{user_id[:8]}"
        cursor.execute(
            "INSERT INTO users (id, username, password, role) VALUES (?, ?, ?, ?)",
            (user_id, username, "", "user")
        )
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
 
    if user_row["is_banned"]:
        conn.close()
        await websocket.close(code=1008, reason="User is banned")
        return
 
    username = user_row["username"]
    conn.close()
 
    await manager.connect(room_id, websocket)
 
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
 
            # Re-check ban status on every message
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT is_banned FROM users WHERE id = ?", (user_id,))
            current_user = cursor.fetchone()
            conn.close()
 
            if current_user and current_user["is_banned"]:
                await websocket.send_json({"error": "You are banned"})
                continue
 
            filtered_text, is_filtered = filter_message(message_data.get("text", ""))
            message_id = str(uuid.uuid4())
            timestamp = datetime.now()
 
            # Save message to DB
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (id, room_id, user_id, username, text, timestamp, is_filtered)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (message_id, room_id, user_id, username, filtered_text, timestamp.isoformat(), int(is_filtered)))
            conn.commit()
            conn.close()
 
            await manager.broadcast(room_id, {
                "type": "message",
                "message": {
                    "id": message_id,
                    "username": username,
                    "text": filtered_text,
                    "timestamp": timestamp.isoformat(),
                    "is_filtered": is_filtered
                }
            })
 
    except Exception as e:
        print(f"WebSocket error: {e}")
 
    finally:
        manager.disconnect(room_id, websocket)
        await manager.broadcast(room_id, {
            "type": "user_left",
            "user_id": user_id,
            "username": username
        })

# ========== BAD WORDS MANAGEMENT ==========

def get_bad_words_file_path():
    """Get the path to bad_words.txt file"""
    return Path(__file__).resolve().parent / "bad_words.txt"

@app.get("/badwords", tags=["BadWords"])
async def get_bad_words():
    """Get all bad words"""
    try:
        file_path = get_bad_words_file_path()
        bad_words_list = []
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('#'):
                        bad_words_list.append(word)
        
        return {"bad_words": bad_words_list, "count": len(bad_words_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading bad words: {str(e)}")

@app.post("/badwords", tags=["BadWords"])
async def add_bad_word(word: str):
    """Add a new bad word"""
    try:
        if not word or len(word.strip()) == 0:
            raise HTTPException(status_code=400, detail="Word cannot be empty")
        
        word = word.strip().lower()
        file_path = get_bad_words_file_path()
        
        # Read existing words
        existing_words = set()
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    existing_word = line.strip()
                    if existing_word and not existing_word.startswith('#'):
                        existing_words.add(existing_word.lower())
        
        # Check if word already exists
        if word in existing_words:
            raise HTTPException(status_code=400, detail="Word already exists in bad words list")
        
        # Add new word
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"{word}\n")
        
        # Reload filter
        global bad_word_filter, bad_words_list
        bad_words_list = load_bad_words_from_file(str(file_path))
        bad_word_filter = BadWordFilter(bad_words_list=bad_words_list)
        
        return {"message": f"Bad word '{word}' added successfully", "word": word}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding bad word: {str(e)}")

@app.delete("/badwords", tags=["BadWords"])
async def delete_bad_word(word: str):
    """Delete a bad word"""
    try:
        if not word or len(word.strip()) == 0:
            raise HTTPException(status_code=400, detail="Word cannot be empty")
        
        word = word.strip().lower()
        file_path = get_bad_words_file_path()
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Bad words file not found")
        
        # Read existing words
        lines = []
        found = False
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                existing_word = line.strip()
                if existing_word.lower() == word:
                    found = True
                else:
                    lines.append(line)
        
        if not found:
            raise HTTPException(status_code=404, detail=f"Word '{word}' not found in bad words list")
        
        # Write back without the deleted word
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Reload filter
        global bad_word_filter, bad_words_list
        bad_words_list = load_bad_words_from_file(str(file_path))
        bad_word_filter = BadWordFilter(bad_words_list=bad_words_list)
        
        return {"message": f"Bad word '{word}' deleted successfully", "word": word}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting bad word: {str(e)}")

@app.get("/badwords/manage", tags=["BadWords"])
async def manage_badwords_page() -> FileResponse:
    """Serve the bad words management page"""
    return FileResponse(FRONTEND_DIR / "badwords.html")

# ========== HEALTH CHECK ==========

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rooms")
    rooms_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM banned_users")
    banned_count = cursor.fetchone()[0]
    conn.close()
    return {
        "status": "ok",
        "rooms_count": rooms_count,
        "users_count": users_count,
        "banned_users_count": banned_count
    }


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
