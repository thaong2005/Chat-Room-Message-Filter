import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "chatroom.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name like a dict
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
# SQLite doesn't have boolean value so we replaced it with integer (0 = false | 1 = true)
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_banned INTEGER DEFAULT 0 
        );

        CREATE TABLE IF NOT EXISTS rooms (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            max_users INTEGER DEFAULT 50,
            current_users INTEGER DEFAULT 0,
            created_by TEXT
        );

        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            room_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            username TEXT NOT NULL,
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            is_filtered INTEGER DEFAULT 0,
            FOREIGN KEY (room_id) REFERENCES rooms(id)
        );

        CREATE TABLE IF NOT EXISTS room_users (
            room_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            PRIMARY KEY (room_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS banned_users (
            user_id TEXT PRIMARY KEY
        );
    """)

    conn.commit()
    conn.close()