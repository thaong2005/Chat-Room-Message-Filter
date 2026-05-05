# Chat-Room-Message-Filter

Real-time chat with automatic profanity filtering. Built with FastAPI, WebSocket, SQLite, and ANTLR.

## Quick Start

**Requirements:** Node.js, Python 3.8+

```bash
npm install
npm start
```

Open `http://localhost:3000`

## Features

- Real-time WebSocket chat
- Profanity filtering (bad words → `***`)
- User auth & registration
- Chat rooms with admin controls
- SQLite persistence

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/login`, `/register` | Authentication |
| `/rooms` | List/create rooms |
| `/rooms/{room_id}/messages` | Send/get messages |
| `/ws/{room_id}/{user_id}` | WebSocket chat |
| `/bad-words` | Manage bad words (admin) |
| `/docs` | API docs |

## Backend

- Port 8000 (FastAPI)
- SQLite database
- ANTLR-based word filtering

## Frontend

- Port 3000 (Vanilla JS)
- Real-time chat UI

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port in use | Kill process or change port |
| Backend won't start | Activate venv, check Python 3.8+ |
| WebSocket fails | Verify backend on port 8000 |