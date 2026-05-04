from pathlib import Path
from fastapi import FastAPI, WebSocket, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from typing import Dict, List, Set, Optional
from datetime import datetime
from db import get_db, init_db 

import json
import uuid

from models import (
    User, Message, ChatRoom, BadWord, 
    JoinRoomRequest, SendMessageRequest
)
from bad_word_filter import BadWordFilter, load_bad_words_from_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(title="Chatroom Messenger Filter Backend (Firebase)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bad_words_list = load_bad_words_from_file()
bad_words: List[BadWord] = [
    BadWord(word=word, replacement="***")
    for word in bad_words_list
]

bad_word_filter = BadWordFilter(bad_words_list=bad_words_list)

def init_default_rooms():
    db = get_db()
    if not db: return
    
    default_rooms = [
        {"id": "room1", "name": "Gaming Central", "description": "Everything from RPGs to FPS", "max_users": 100, "created_by": "admin", "current_users": 0},
        {"id": "room2", "name": "Developers Den", "description": "React, Python, and more", "max_users": 50, "created_by": "admin", "current_users": 0},
    ]
    
    rooms_ref = db.collection('rooms')
    for room in default_rooms:
        doc = rooms_ref.document(room['id']).get()
        if not doc.exists:
            rooms_ref.document(room['id']).set(room)

init_db()
init_default_rooms()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.active_connections and websocket in self.active_connections[room_id]:
            self.active_connections[room_id].remove(websocket)

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_json(message)

manager = ConnectionManager()

def filter_message(text: str) -> tuple[str, bool]:
    filtered, is_filtered, _ = bad_word_filter.filter_message(text)
    return filtered, is_filtered

@app.get("/", tags=["Root"])
async def root():
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", tags=["Auth"])
async def login() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "loginPage.html")

@app.get("/register", tags=["Auth"])
async def register() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "registerPage.html")

@app.post("/login", tags=["Auth"])
async def Login(username: str, password: str):
    db = get_db()
    if not db: raise HTTPException(status_code=500, detail="Database not configured")
    
    admins_ref = db.collection('admins').where('adminname', '==', username).where('password', '==', password).stream()
    for a in admins_ref:
        admin_data = a.to_dict()
        return {"message": "Login successful!", "user_id": admin_data["id"], "username": admin_data["adminname"], "is_admin": True}

    users_ref = db.collection('users').where('username', '==', username).where('password', '==', password).stream()
    user = None
    for u in users_ref:
        user = u.to_dict()
        break
        
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if user.get("is_banned", 0) == 1:
        raise HTTPException(status_code=403, detail="Your account is banned")

    return {"message": "Login successful!", "user_id": user["id"], "username": user["username"], "is_admin": False}    

@app.post("/register", tags=["Auth"])
async def Register(username: str, password: str):
    db = get_db()
    if not db: raise HTTPException(status_code=500, detail="Database not configured")
    
    admins_ref = db.collection('admins').where('adminname', '==', username).stream()
    for _ in admins_ref:
        raise HTTPException(status_code=400, detail="Username reserved. Pick another")
        
    users_ref = db.collection('users').where('username', '==', username).stream()
    for _ in users_ref:
        raise HTTPException(status_code=400, detail="Account already exists. Pick another")

    user_id = str(uuid.uuid4())
    db.collection('users').document(user_id).set({
        "id": user_id,
        "username": username,
        "password": password,
        "is_banned": 0
    })
    return {"message": "Registered successfully!", "username": username}

@app.get("/rooms", tags=["Rooms"])
async def get_all_rooms():
    db = get_db()
    if not db: return []
    rooms = []
    for doc in db.collection('rooms').stream():
        rooms.append(doc.to_dict())
    return rooms

@app.post("/rooms", tags=["Rooms"])
async def create_room(room: ChatRoom):
    db = get_db()
    if not db: raise HTTPException(status_code=500, detail="Database not configured")
    doc = db.collection('rooms').document(room.id).get()
    if doc.exists:
        raise HTTPException(status_code=400, detail="Room already exists")
    
    room_dict = {
        "id": room.id,
        "name": room.name,
        "description": room.description,
        "max_users": room.max_users,
        "created_by": room.created_by,
        "current_users": 0
    }
    db.collection('rooms').document(room.id).set(room_dict)
    return {"message": "Room created", "room": room_dict}

@app.post("/users/{user_id}/join-room", tags=["Users"])
async def join_room(user_id: str, request: JoinRoomRequest):
    db = get_db()
    if not db: raise HTTPException(status_code=500, detail="Database not configured")
    
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    if not user_doc.exists:
        user_ref.set({
            "id": user_id,
            "username": request.username,
            "password": "",
            "is_banned": 0
        })
    elif user_doc.to_dict().get("is_banned") == 1:
         raise HTTPException(status_code=403, detail="User is banned")
         
    room_ref = db.collection('rooms').document(request.room_id)
    room_doc = room_ref.get()
    if not room_doc.exists:
        raise HTTPException(status_code=404, detail="Room not found")
        
    room_data = room_doc.to_dict()
    if room_data.get("current_users", 0) >= room_data.get("max_users", 50):
        raise HTTPException(status_code=400, detail="Room is full")
        
    # Room user logical link
    room_user_id = f"{request.room_id}_{user_id}"
    db.collection('room_users').document(room_user_id).set({
        "room_id": request.room_id,
        "user_id": user_id
    })
    
    # Recalculate room users
    count = len(list(db.collection('room_users').where('room_id', '==', request.room_id).stream()))
    room_ref.update({"current_users": count})
    room_data["current_users"] = count
    
    return {"message": "Joined room", "room": room_data}

@app.post("/users/{user_id}/leave-room/{room_id}", tags=["Users"])
async def leave_room(user_id: str, room_id: str):
    db = get_db()
    if not db: return {"message": "Left room"}
    room_user_id = f"{room_id}_{user_id}"
    db.collection('room_users').document(room_user_id).delete()
    
    count = len(list(db.collection('room_users').where('room_id', '==', room_id).stream()))
    db.collection('rooms').document(room_id).update({"current_users": count})
    return {"message": "Left room"}

@app.get("/rooms/{room_id}/messages", tags=["Messages"])
async def get_messages(room_id: str, limit: int = 50):
    db = get_db()
    if not db: return []
    messages = []
    # Firestore query
    query = db.collection('messages').where('room_id', '==', room_id).order_by('timestamp').limit(limit)
    for doc in query.stream():
        messages.append(doc.to_dict())
    return messages

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    db = get_db()
    if not db:
        await websocket.close(code=1008, reason="Database not configured")
        return
        
    room_doc = db.collection('rooms').document(room_id).get()
    if not room_doc.exists:
        await websocket.close(code=1008, reason="Room not found")
        return
        
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        username = f"User_{user_id[:8]}"
        db.collection('users').document(user_id).set({
            "id": user_id, "username": username, "password": "", "is_banned": 0
        })
        user_row = {"username": username, "is_banned": 0}
    else:
        user_row = user_doc.to_dict()
        
    if user_row.get("is_banned", 0) == 1:
        await websocket.close(code=1008, reason="User is banned")
        return
        
    username = user_row["username"]
    await manager.connect(room_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Recheck ban
            u_doc = db.collection('users').document(user_id).get()
            if u_doc.exists and u_doc.to_dict().get("is_banned") == 1:
                await websocket.send_json({"error": "You are banned"})
                continue
                
            filtered_text, is_filtered = filter_message(message_data.get("text", ""))
            message_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            db.collection('messages').document(message_id).set({
                "id": message_id,
                "room_id": room_id,
                "user_id": user_id,
                "username": username,
                "text": filtered_text,
                "timestamp": timestamp,
                "is_filtered": int(is_filtered)
            })
            
            await manager.broadcast(room_id, {
                "type": "message",
                "message": {
                    "id": message_id,
                    "username": username,
                    "text": filtered_text,
                    "timestamp": timestamp,
                    "is_filtered": is_filtered
                }
            })
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        manager.disconnect(room_id, websocket)
        await manager.broadcast(room_id, {
            "type": "user_left",
            "user_id": user_id, "username": username
        })

# ========== ADMIN ENDPOINTS ==========

def verify_admin(user_id: str):
    db = get_db()
    if not db: raise HTTPException(status_code=500, detail="Database not configured")
    admin_doc = db.collection('admins').document(user_id).get()
    if not admin_doc.exists:
        raise HTTPException(status_code=403, detail="Admin privilege required")
    return db

@app.post("/users/{user_id}/kick/{target_user_id}/room/{room_id}", tags=["Admin"])
async def kick_user(user_id: str, target_user_id: str, room_id: str):
    db = verify_admin(user_id)
    room_doc = db.collection('rooms').document(room_id).get()
    if not room_doc.exists:
        raise HTTPException(status_code=404, detail="Room not found")
        
    room_user_id = f"{room_id}_{target_user_id}"
    db.collection('room_users').document(room_user_id).delete()
    
    count = len(list(db.collection('room_users').where('room_id', '==', room_id).stream()))
    db.collection('rooms').document(room_id).update({"current_users": count})
    return {"message": f"User {target_user_id} kicked from room"}

@app.post("/users/{user_id}/ban/{target_user_id}", tags=["Admin"])
async def ban_user(user_id: str, target_user_id: str):
    db = verify_admin(user_id)
    user_ref = db.collection('users').document(target_user_id)
    if not user_ref.get().exists:
        raise HTTPException(status_code=404, detail="User not found")
    user_ref.update({"is_banned": 1})
    return {"message": f"User {target_user_id} banned"}

@app.post("/users/{user_id}/unban/{target_user_id}", tags=["Admin"])
async def unban_user(user_id: str, target_user_id: str):
    db = verify_admin(user_id)
    user_ref = db.collection('users').document(target_user_id)
    if not user_ref.get().exists:
        raise HTTPException(status_code=404, detail="User not found")
    user_ref.update({"is_banned": 0})
    return {"message": f"User {target_user_id} unbanned"}

def get_bad_words_file_path():
    return Path(__file__).resolve().parent / "bad_words.txt"

@app.get("/badwords", tags=["Admin"])
async def get_bad_words_endpoint():
    try:
        file_path = get_bad_words_file_path()
        words_list = []
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word and not word.startswith('#'):
                        words_list.append(word)
        return {"bad_words": words_list, "count": len(words_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading bad words: {str(e)}")

@app.post("/badwords", tags=["Admin"])
async def add_bad_word_endpoint(user_id: str, word: str):
    verify_admin(user_id)
    try:
        if not word or len(word.strip()) == 0:
            raise HTTPException(status_code=400, detail="Word cannot be empty")
        word = word.strip().lower()
        file_path = get_bad_words_file_path()
        existing = set()
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    w = line.strip()
                    if w and not w.startswith('#'):
                        existing.add(w.lower())
        if word in existing:
            raise HTTPException(status_code=400, detail="Word already exists")
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"{word}\n")
            
        global bad_word_filter, bad_words_list
        bad_words_list = load_bad_words_from_file(str(file_path))
        bad_word_filter = BadWordFilter(bad_words_list=bad_words_list)
        return {"message": f"Bad word '{word}' added"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/badwords", tags=["Admin"])
async def delete_bad_word_endpoint(user_id: str, word: str):
    verify_admin(user_id)
    try:
        if not word or len(word.strip()) == 0:
            raise HTTPException(status_code=400, detail="Word cannot be empty")
        word = word.strip().lower()
        file_path = get_bad_words_file_path()
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
            
        lines = []
        found = False
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                w = line.strip()
                if w.lower() == word:
                    found = True
                else:
                    lines.append(line)
        if not found:
            raise HTTPException(status_code=404, detail="Word not found")
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        global bad_word_filter, bad_words_list
        bad_words_list = load_bad_words_from_file(str(file_path))
        bad_word_filter = BadWordFilter(bad_words_list=bad_words_list)
        return {"message": f"Bad word '{word}' deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/badwords/manage", tags=["Admin"])
async def manage_badwords_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "badwords.html")

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
