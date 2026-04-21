# Quick Start - Chat Room Message Filter

Chạy hệ thống trong 5 phút!

## Bước 1: Chuẩn Bị

Mở 2 terminal:
- Terminal 1: Cho backend
- Terminal 2: Cho frontend (hoặc dùng VS Code Live Server)

## Bước 2: Chạy Backend

**Terminal 1:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Chờ tới khi thấy:
```
Uvicorn running on http://0.0.0.0:8000
```


**For Python 3.14**

```bash
cd backend
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
```

## Bước 3: Chạy Frontend

**Option A: Live Server (VS Code)**
- Cài extension "Live Server"
- Click phải vào `frontend/index.html` → "Open with Live Server"

**Option B: Python HTTP Server**
```bash
cd frontend
python -m http.server 8080
```

**Option C: npm serve**
```bash
npm install -g serve
cd frontend
serve
```

## Bước 4: Mở Browser

- Nếu dùng Live Server: Auto open (thường là `http://127.0.0.1:5500`)
- Nếu dùng Python HTTP: http://localhost:8080
- Nếu dùng npm serve: http://localhost:3000

## Bước 5: Test

1. Trang lobby sẽ hiển thị danh sách phòng từ backend
2. Click vào một phòng
3. Bạn sẽ vào giao diện chat
4. Gửi tin nhắn thử
5. Nếu khác một phòng khác → tin nhắn sẽ real-time!

## URL Endpoints

- **Frontend:** http://localhost:PORT/index.html
- **Backend API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Test Message Filter

Thử gửi message với từ xấu (default: "badword1", "badword2", "hate", "spam"):
```
Hello badword1!
```

Kết quả: `Hello ***!`

## Xem Tin Nhắn Đã Gửi

Call API trong browser console:
```javascript
fetch('http://localhost:8000/rooms/room1/messages?limit=10')
  .then(r => r.json())
  .then(data => console.log(data))
```

## Chạy Backend ở Background

Trên Windows (PowerShell):
```powershell
Start-Process python -ArgumentList "main.py" -NoNewWindow
```

Trên Mac/Linux:
```bash
python main.py &
```

## Tắt Ứng Dụng

1. Tắt browser
2. Terminal backend: Press `Ctrl+C`
3. Terminal frontend: Press `Ctrl+C`

## Thêm Phòng Mới (Admin)

Dùng Swagger UI tại http://localhost:8000/docs:
1. Tìm `POST /rooms`
2. Click "Try it out"
3. Nhập data:
```json
{
  "id": "new_room",
  "name": "My Room",
  "description": "My description",
  "max_users": 50,
  "created_by": "admin"
}
```
4. Click "Execute"
5. F5 refresh frontend để thấy phòng mới

## Lưu Ý

- ⚠️ Dữ liệu sẽ mất khi restart backend
- ⚠️ Chỉ 2 browser tab có thể chat cùng room (demo limitation)
- ✅ WebSocket auto-reconnect nếu mất kết nối
- ✅ Message filter real-time

## Có Vấn Đề?

- Check console browser (F12)
- Kiểm tra backend có chạy `http://localhost:8000`
- Kiểm tra frontend có load danh sách phòng
- Try refresh trang (F5)

Enjoy! 🎉
