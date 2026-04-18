from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Set
from datetime import datetime
import json
import uuid

from models import (
    User, Message, ChatRoom, BadWord, 
    JoinRoomRequest, SendMessageRequest
)

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
rooms: Dict[str, ChatRoom] = {}
users: Dict[str, User] = {}
bad_words: List[BadWord] = [
    BadWord(word="badword1", replacement="***"),
    BadWord(word="badword2", replacement="***"),
    BadWord(word="hate", replacement="***"),
    BadWord(word="spam", replacement="***"),
]
banned_users: Set[str] = set()

# Initialize default rooms
def init_default_rooms():
    default_rooms = [
        ChatRoom(
            id="room1",
            name="Gaming Central",
            description="Everything from RPGs to FPS",
            max_users=100,
            current_users=0,
            created_by="admin"
        ),
        ChatRoom(
            id="room2",
            name="Developers Den",
            description="React, Python, and more",
            max_users=50,
            current_users=0,
            created_by="admin"
        ),
        ChatRoom(
            id="room3",
            name="Music Theory",
            description="Sharing beats and vibes",
            max_users=20,
            current_users=0,
            created_by="admin"
        ),
        ChatRoom(
            id="room4",
            name="Art & Design",
            description="Showcase your latest work",
            max_users=60,
            current_users=0,
            created_by="admin"
        ),
        ChatRoom(
            id="room5",
            name="Study Group",
            description="Focused work only",
            max_users=15,
            current_users=0,
            created_by="admin"
        ),
        ChatRoom(
            id="room6",
            name="Cinema Talk",
            description="Reviewing the latest hits",
            max_users=40,
            current_users=0,
            created_by="admin"
        ),
    ]
    for room in default_rooms:
        rooms[room.id] = room

# Initialize default rooms on startup
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

# Utility function to filter bad words
def filter_message(text: str) -> tuple[str, bool]:
    filtered = text
    is_filtered = False
    for bad_word in bad_words:
        if bad_word.word.lower() in text.lower():
            is_filtered = True
            filtered = filtered.replace(bad_word.word, bad_word.replacement)
            filtered = filtered.replace(bad_word.word.upper(), bad_word.replacement)
            filtered = filtered.replace(bad_word.word.capitalize(), bad_word.replacement)
    return filtered, is_filtered

# ========== ROOM ENDPOINTS ==========

@app.get("/rooms", tags=["Rooms"])
async def get_all_rooms():
    """Get all chat rooms"""
    return list(rooms.values())

@app.post("/rooms", tags=["Rooms"])
async def create_room(room: ChatRoom):
    """Create a new chat room"""
    if room.id in rooms:
        raise HTTPException(status_code=400, detail="Room already exists")
    rooms[room.id] = room
    return {"message": "Room created", "room": room}

@app.get("/rooms/{room_id}", tags=["Rooms"])
async def get_room(room_id: str):
    """Get a specific chat room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return rooms[room_id]

@app.delete("/rooms/{room_id}", tags=["Rooms"])
async def delete_room(room_id: str):
    """Delete a chat room (Admin only)"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    del rooms[room_id]
    return {"message": "Room deleted"}

# ========== USER ENDPOINTS ==========

@app.post("/users", tags=["Users"])
async def create_user(user: User):
    """Create a new user"""
    if user.id in users:
        raise HTTPException(status_code=400, detail="User already exists")
    users[user.id] = user
    return {"message": "User created", "user": user}

@app.post("/users/{user_id}/join-room", tags=["Users"])
async def join_room(user_id: str, request: JoinRoomRequest):
    """Join a chat room"""
    # Auto-create user if not exists
    if user_id not in users:
        user = User(id=user_id, username=request.username, role="user")
        users[user_id] = user
    
    if request.room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    user = users[user_id]
    room = rooms[request.room_id]
    
    if user.is_banned or user_id in banned_users:
        raise HTTPException(status_code=403, detail="User is banned from this room")
    
    if room.current_users >= room.max_users:
        raise HTTPException(status_code=400, detail="Room is full")
    
    if user_id not in room.users:
        room.users.append(user_id)
        room.current_users += 1
    
    return {"message": "Joined room", "room": room}

@app.post("/users/{user_id}/leave-room/{room_id}", tags=["Users"])
async def leave_room(user_id: str, room_id: str):
    """Leave a chat room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    if user_id in room.users:
        room.users.remove(user_id)
        room.current_users -= 1
    
    return {"message": "Left room"}

@app.get("/rooms/{room_id}/users", tags=["Users"])
async def get_room_users(room_id: str):
    """Get list of users in a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    room_users = [users[uid] for uid in room.users if uid in users]
    return room_users

@app.post("/users/{user_id}/kick/{target_user_id}/room/{room_id}", tags=["Users"])
async def kick_user(user_id: str, target_user_id: str, room_id: str):
    """Kick a user from a room (Admin only)"""
    if user_id not in users or users[user_id].role != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    if target_user_id in room.users:
        room.users.remove(target_user_id)
        room.current_users -= 1
    
    return {"message": f"User {target_user_id} kicked from room"}

@app.post("/users/{user_id}/ban/{target_user_id}", tags=["Users"])
async def ban_user(user_id: str, target_user_id: str):
    """Ban a user (Admin only)"""
    if user_id not in users or users[user_id].role != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    
    banned_users.add(target_user_id)
    if target_user_id in users:
        users[target_user_id].is_banned = True
    
    return {"message": f"User {target_user_id} banned"}

@app.post("/users/{user_id}/unban/{target_user_id}", tags=["Users"])
async def unban_user(user_id: str, target_user_id: str):
    """Unban a user (Admin only)"""
    if user_id not in users or users[user_id].role != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    
    if target_user_id in banned_users:
        banned_users.remove(target_user_id)
    if target_user_id in users:
        users[target_user_id].is_banned = False
    
    return {"message": f"User {target_user_id} unbanned"}

# ========== MESSAGE ENDPOINTS ==========

@app.post("/rooms/{room_id}/messages", tags=["Messages"])
async def send_message(room_id: str, request: SendMessageRequest):
    """Send a message to a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if request.user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users[request.user_id]
    if user.is_banned:
        raise HTTPException(status_code=403, detail="User is banned")
    
    room = rooms[room_id]
    
    # Filter message
    filtered_text, is_filtered = filter_message(request.text)
    
    # Create message
    message = Message(
        id=str(uuid.uuid4()),
        room_id=room_id,
        user_id=request.user_id,
        username=request.username,
        text=filtered_text,
        timestamp=datetime.now(),
        is_filtered=is_filtered
    )
    
    room.messages.append(message)
    
    return {"message": "Message sent", "data": message, "was_filtered": is_filtered}

@app.get("/rooms/{room_id}/messages", tags=["Messages"])
async def get_messages(room_id: str, limit: int = 50):
    """Get messages from a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room = rooms[room_id]
    return room.messages[-limit:]

# ========== BAD WORDS ENDPOINTS ==========

@app.get("/bad-words", tags=["BadWords"])
async def get_bad_words(user_id: str):
    """Get list of bad words (Admin only)"""
    if user_id not in users or users[user_id].role != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    return bad_words

@app.post("/bad-words", tags=["BadWords"])
async def add_bad_word(user_id: str, bad_word: BadWord):
    """Add a bad word (Admin only)"""
    if user_id not in users or users[user_id].role != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    
    bad_words.append(bad_word)
    return {"message": "Bad word added", "word": bad_word}

@app.delete("/bad-words/{word}", tags=["BadWords"])
async def remove_bad_word(user_id: str, word: str):
    """Remove a bad word (Admin only)"""
    if user_id not in users or users[user_id].role != "admin":
        raise HTTPException(status_code=403, detail="Admin privilege required")
    
    global bad_words
    bad_words = [bw for bw in bad_words if bw.word.lower() != word.lower()]
    return {"message": "Bad word removed"}

# ========== WEBSOCKET (Real-time Chat) ==========

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    """WebSocket endpoint for real-time chat"""
    if room_id not in rooms:
        await websocket.close(code=1008, reason="Room not found")
        return
    
    # Auto-create user if not exists
    if user_id not in users:
        username = f"User_{user_id[:8]}"
        users[user_id] = User(id=user_id, username=username, role="user")
    
    user = users[user_id]
    
    if user.is_banned:
        await websocket.close(code=1008, reason="User is banned")
        return
    
    await manager.connect(room_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user = users[user_id]
            if user.is_banned:
                await websocket.send_json({"error": "You are banned"})
                continue
            
            # Filter message
            filtered_text, is_filtered = filter_message(message_data.get("text", ""))
            
            # Create and store message
            message = Message(
                id=str(uuid.uuid4()),
                room_id=room_id,
                user_id=user_id,
                username=users[user_id].username,
                text=filtered_text,
                timestamp=datetime.now(),
                is_filtered=is_filtered
            )
            
            rooms[room_id].messages.append(message)
            
            # Broadcast to all users in room
            await manager.broadcast(room_id, {
                "type": "message",
                "message": {
                    "id": message.id,
                    "username": message.username,
                    "text": message.text,
                    "timestamp": message.timestamp.isoformat(),
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
            "username": users[user_id].username
        })

# ========== HEALTH CHECK ==========

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "rooms_count": len(rooms),
        "users_count": len(users),
        "banned_users_count": len(banned_users)
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Chatroom Messenger Filter Backend API",
        "docs": "/docs",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
