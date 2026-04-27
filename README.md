# Chat-Room-Message-Filter

A real-time chat room application with automatic message filtering for banned words. Built with FastAPI, WebSocket, SQLite, and vanilla JavaScript.

**Tech Stack:** Python, FastAPI, WebSocket, SQLite, ANTLR, HTML/CSS/JavaScript

## Project Structure

```
Chat-Room-Message-Filter/
├── backend/          # FastAPI server
│   ├── main.py       # Main app
│   ├── bad_word_filter.py  # Filter logic
│   ├── db.py         # Database
│   └── requirements.txt
├── frontend/         # Static site
│   ├── index.html    # Lobby
│   ├── chat.html     # Chat room
│   └── *.js, *.css
└── documents/        # Diagrams
```

## Quick Start

**Requirements:** Python 3.8+, modern browser

**1. Backend (Terminal 1)**
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Server runs at `http://localhost:8000`

**2. Frontend (Terminal 2)**
```bash
cd frontend
python -m http.server 8080
```
Open `http://localhost:8080` in your browser

**3. Test**
- View rooms from the lobby
- Click a room to chat
- Send a message (banned words are replaced with `***`)
- Open same room in another tab to see real-time messaging

API docs available at `http://localhost:8000/docs`

## Features

- ✅ Real-time chat via WebSocket
- ✅ Automatic message filtering (banned words → `***`)
- ✅ Login & register system
- ✅ Create or join chat rooms
- ✅ SQLite database for persistence

## API Endpoints

**Auth:** `POST /login`, `POST /register`  
**Rooms:** `GET /rooms`, `POST /rooms`, `GET /rooms/{room_id}`, `DELETE /rooms/{room_id}`  
**Chat:** `WebSocket /ws/{room_id}/{user_id}`  
**Docs:** `http://localhost:8000/docs`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check port 8000 isn't in use; ensure Python 3.8+ |
| WebSocket connection fails | Check browser console; may fallback to HTTP polling |
| Bad words not filtering | Verify `backend/bad_words.txt` exists |