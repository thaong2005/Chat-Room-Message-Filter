# Chatroom Messenger Filter Backend

Backend API cho hệ thống chat room với chức năng lọc tin nhắn xấu.

## Yêu cầu

- Python 3.8+
- pip

## Cài đặt

1. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

2. **Chạy server:**
```bash
python main.py
```

Server sẽ chạy tại `http://localhost:8000`

## API Documentation

### Interactive Docs
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Các Endpoint Chính

### Phòng Chat
- `GET /rooms` - Lấy tất cả phòng
- `POST /rooms` - Tạo phòng mới
- `GET /rooms/{room_id}` - Lấy thông tin phòng
- `DELETE /rooms/{room_id}` - Xóa phòng (Admin only)

### Người Dùng
- `POST /users` - Tạo người dùng
- `POST /users/{user_id}/join-room` - Tham gia phòng
- `POST /users/{user_id}/leave-room/{room_id}` - Rời phòng
- `GET /rooms/{room_id}/users` - Lấy danh sách người dùng trong phòng
- `POST /users/{user_id}/kick/{target_user_id}/room/{room_id}` - Kick người dùng (Admin)
- `POST /users/{user_id}/ban/{target_user_id}` - Ban người dùng (Admin)
- `POST /users/{user_id}/unban/{target_user_id}` - Unban người dùng (Admin)

### Tin Nhắn
- `POST /rooms/{room_id}/messages` - Gửi tin nhắn
- `GET /rooms/{room_id}/messages?limit=50` - Lấy tin nhắn
- `WebSocket /ws/{room_id}/{user_id}` - Chat real-time

### Quản lý Từ Xấu
- `GET /bad-words?user_id={admin_id}` - Lấy danh sách từ xấu (Admin)
- `POST /bad-words?user_id={admin_id}` - Thêm từ xấu (Admin)
- `DELETE /bad-words/{word}?user_id={admin_id}` - Xóa từ xấu (Admin)

### Khác
- `GET /health` - Health check
- `GET /` - Root endpoint

## Ví dụ Sử Dụng

### 1. Tạo Người Dùng
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "user1",
    "username": "Alice",
    "role": "user"
  }'
```

### 2. Tạo Phòng Chat
```bash
curl -X POST "http://localhost:8000/rooms" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "room1",
    "name": "Gaming Central",
    "description": "Game chat room",
    "max_users": 100,
    "created_by": "user1"
  }'
```

### 3. Tham Gia Phòng
```bash
curl -X POST "http://localhost:8000/users/user1/join-room" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "room1",
    "user_id": "user1",
    "username": "Alice"
  }'
```

### 4. Gửi Tin Nhắn
```bash
curl -X POST "http://localhost:8000/rooms/room1/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "room_id": "room1",
    "user_id": "user1",
    "username": "Alice",
    "text": "Hello everyone!"
  }'
```

### 5. Lấy Tin Nhắn
```bash
curl "http://localhost:8000/rooms/room1/messages?limit=10"
```

### 6. WebSocket (Real-time Chat)
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/room1/user1");

ws.onmessage = function(event) {
  console.log("Message:", event.data);
};

ws.send(JSON.stringify({
  text: "Hello from WebSocket!"
}));
```

## Tính Năng

✅ **Quản lý Phòng:** Tạo, xóa, lấy danh sách phòng
✅ **Quản lý Người Dùng:** Tạo user, join/leave room, ban/unban
✅ **Gửi Tin Nhắn:** HTTP REST API và WebSocket real-time
✅ **Lọc Từ Xấu:** Tự động thay thế từ xấu trong tin nhắn
✅ **Phân Quyền:** User vs Admin
✅ **In-memory Storage:** Lưu trữ dữ liệu tạm thời trong bộ nhớ

## Cấu Trúc Project

```
backend/
├── main.py           # FastAPI main server
├── models.py         # Pydantic models
├── requirements.txt  # Python dependencies
└── README.md         # Documentation
```

## Lưu Ý

- Backend sử dụng in-memory storage, dữ liệu sẽ mất khi server restart
- Để production, nên thay thế bằng database (PostgreSQL, MongoDB, etc.)
- WebSocket chỉ hoạt động khi kết nối từ frontend
