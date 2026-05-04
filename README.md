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

## Quick Start (All Platforms)

**Requirements:** Node.js, Python 3.8+

**Setup (1 time only):**
```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate venv
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 3. Install all dependencies
npm install
```

**Run Application:**
```bash
npm start
```

This will:
- ✅ Start backend (FastAPI on port 8000)
- ✅ Start frontend (serve on port 3000)

Open `http://localhost:3000` in your browser

**API Documentation:** `http://localhost:8000/docs`

**Alternative: Manual Setup**
```bash
# Terminal 1 - Backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
cd backend
python main.py

# Terminal 2 - Frontend
npx serve frontend -p 3000
```

**Test**
- View rooms from the lobby
- Click a room to chat
- Send a message (banned words are replaced with `***`)
- Open same room in another tab to see real-time messaging

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