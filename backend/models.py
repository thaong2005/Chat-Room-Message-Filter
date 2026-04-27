from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    password: str
    role: str = "user"  # "user" or "admin"
    is_banned: bool = False

class Message(BaseModel):
    id: str
    room_id: str
    user_id: str
    username: str
    text: str
    timestamp: datetime
    is_filtered: bool = False

class ChatRoom(BaseModel):
    id: str
    name: str
    description: str
    max_users: int
    current_users: int = 0
    users: List[str] = []  # list of user_ids
    messages: List[Message] = []
    created_by: str

class BadWord(BaseModel):
    word: str
    replacement: str = "***"

class JoinRoomRequest(BaseModel):
    room_id: str
    user_id: str
    username: str

class SendMessageRequest(BaseModel):
    room_id: str
    user_id: str
    username: str
    text: str
