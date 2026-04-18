# Chat Room Message Filter - Setup Guide

Hướng dẫn để chạy toàn bộ hệ thống chat room với message filter.

## Yêu Cầu

- Python 3.8+
- Node.js/npm (optional, nếu muốn run development server cho frontend)
- Browser hiện đại (Chrome, Firefox, Safari, Edge)

## Cấu Trúc Project

```
Chat-Room-Message-Filter/
├── backend/           # FastAPI backend
│   ├── main.py       # Main server file
│   ├── models.py     # Pydantic models
│   ├── requirements.txt
│   └── README.md
└── frontend/         # HTML/CSS/JS frontend
    ├── index.html    # Lobby page
    ├── chat.html     # Chat room page
    ├── style.css     # Styles
    ├── lobby.js      # Load rooms from API
    ├── chat.js       # Chat logic & WebSocket
    └── config.js     # API configuration
```

## Hướng Dẫn Chạy

### 1. Chạy Backend

```bash
# Di chuyển vào thư mục backend
cd backend

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
python main.py
```

Server sẽ chạy tại `http://localhost:8000`

**Interactive API Docs:** http://localhost:8000/docs

### 2. Chạy Frontend

**Option 1: Dùng Live Server (VS Code)**
- Cài extension "Live Server" trong VS Code
- Click chuột phải trên `frontend/index.html` → "Open with Live Server"
- Frontend sẽ mở tại `http://127.0.0.1:5500`

**Option 2: Dùng Python simple HTTP server**
```bash
cd frontend
python -m http.server 8080
```
Truy cập: `http://localhost:8080/index.html`

**Option 3: Dùng npm serve**
```bash
npm install -g serve
cd frontend
serve
```

## Cách Sử Dụng

### Trang Chủ (Lobby)
1. Mở `http://localhost:PORT/index.html` (tùy theo cách chạy frontend)
2. Danh sách phòng sẽ được tải từ backend
3. Click vào một phòng để vào chat

### Trang Chat
1. Giao diện chat sẽ hiển thị
2. Tin nhắn trước đó sẽ được tải từ backend
3. Gửi tin nhắn:
   - Nếu WebSocket kết nối được → gửi real-time
   - Nếu không → fallback dùng HTTP API
4. Tin nhắn chứa từ xấu sẽ được lọc tự động

## Tính Năng

✅ **Real-time Chat:** WebSocket cho chat tức thời
✅ **Message Filter:** Tự động lọc từ xấu
✅ **Rooms List:** Load danh sách phòng từ backend
✅ **Search:** Tìm kiếm phòng theo tên
✅ **Auto User Creation:** Tự động tạo user khi join phòng
✅ **Session Storage:** Lưu user info trong localStorage

## API Endpoints

### Rooms
- `GET /rooms` - Lấy tất cả phòng
- `GET /rooms/{room_id}` - Lấy thông tin phòng

### Messages
- `GET /rooms/{room_id}/messages` - Lấy tin nhắn
- `POST /rooms/{room_id}/messages` - Gửi tin nhắn

### WebSocket
- `WS /ws/{room_id}/{user_id}` - Real-time chat

Xem đầy đủ tại: http://localhost:8000/docs

## Cách Kết Nối Backend-Frontend

### 1. Backend API Configuration
File `frontend/config.js`:
```javascript
const API_BASE_URL = "http://localhost:8000";
const WS_BASE_URL = "ws://localhost:8000";
```

### 2. Workflow Kết Nối

**Trang Lobby (index.html):**
1. `lobby.js` gọi `GET /rooms` để lấy danh sách phòng
2. Nếu backend không sẵn sàng, sử dụng demo rooms
3. Click vào phòng → chuyển sang `chat.html?room={room_id}`

**Trang Chat (chat.html):**
1. `chat.js` gọi `GET /rooms/{room_id}/messages` để lấy tin nhắn cũ
2. Kết nối WebSocket: `WS /ws/{room_id}/{user_id}`
3. Khi gửi tin nhắn → gửi qua WebSocket (hoặc HTTP fallback)
4. Nhận tin nhắn từ WebSocket → hiển thị trên UI

### 3. CORS Configuration

Backend đã được cấu hình CORS để chấp nhận request từ frontend:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: chỉ định origin cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### WebSocket không kết nối
- Kiểm tra backend có chạy tại `http://localhost:8000`
- Check console browser (F12) xem lỗi gì
- Thử refresh trang

### API request failed
- Kiểm tra backend có chạy không
- Kiểm tra URL trong `config.js`
- Check CORS headers

### Không có phòng hiển thị
- Kiểm tra backend có initialize rooms không
- Check Network tab trong DevTools

### Message gửi không được
- Kiểm tra console log
- Nếu WebSocket lỗi, system sẽ fallback dùng HTTP
- Kiểm tra từ xấu có được lọc không (check `is_filtered`)

## Notes

- Backend sử dụng **in-memory storage** (dữ liệu mất khi restart)
- Để production, cần thay bằng database (PostgreSQL, MongoDB, etc.)
- User được tạo tự động khi join room
- Username được lưu trong localStorage
- WebSocket timeout sau ~30 giây inactivity (tuỳ browser)

## Development Tips

- Dùng DevTools (F12) để debug JavaScript
- Check Network tab để xem requests
- Check Console tab để xem logs
- API docs có sẵn tại `/docs` để test endpoints

## Support

Nếu gặp vấn đề:
1. Kiểm tra console browser
2. Check backend logs
3. Kiểm tra URL và port
4. Try restart backend và frontend
