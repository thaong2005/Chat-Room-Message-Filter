import os
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

# Provide path to your Firebase Service Account JSON file here
SERVICE_ACCOUNT_PATH = Path(__file__).resolve().parent / "firebase-service-account.json"

db = None

def init_db():
    global db
    if not firebase_admin._apps:
        if not SERVICE_ACCOUNT_PATH.exists():
            print("WARNING: firebase-service-account.json not found! Please create it.")
            # For placeholder purposes during development if no key exists
            return None
        cred = credentials.Certificate(str(SERVICE_ACCOUNT_PATH))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully!")
    return db

def get_db():
    if db is None:
        return init_db()
    return db