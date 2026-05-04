#!/usr/bin/env python3
"""
Script để tạo admin account
Usage: python create_admin.py
"""

import sqlite3
import uuid
import hashlib
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "chatroom.db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin():
    username = "admin"
    password = "admin@123"
    role = "admin"
    user_id = str(uuid.uuid4())
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        hashed_password = hash_password(password)
        
        cursor.execute("""
            INSERT INTO users (id, username, password, role, is_banned)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, hashed_password, role, 0))
        
        conn.commit()
        print(f"   Admin account created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Role: {role}")
        print(f"   User ID: {user_id}")
        
    except sqlite3.IntegrityError:
        print(f"Admin account already exists!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin()
