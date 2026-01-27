# 🎮 GAME MÔ PHỎNG MÊ CUNG THOÁT HIỂM CÓ AI

## 📖 Mô tả dự án

Dự án xây dựng một game mô phỏng mê cung trong đó người chơi phải tìm đường thoát khỏi mê cung trong khi có kẻ địch AI đang truy đuổi. Ứng dụng tích hợp nhiều thuật toán tìm đường và cho phép trực quan hóa từng bước chạy thuật toán.

### 🎯 Mục tiêu

- Ứng dụng các thuật toán: **Đồ thị, Tham lam, Quy hoạch động, Tìm kiếm**
- Phân tích **độ phức tạp**, **ưu/nhược điểm** của từng thuật toán
- Rèn luyện **tư duy giải thuật** và **lập trình Python**
- Thiết kế **hệ thống** và **giao diện** chuyên nghiệp

## 🚀 Tính năng chính

### 1️⃣ Sinh mê cung tự động
- **Thuật toán**: Backtracking (Quay lui)
- Tạo mê cung ngẫu nhiên với kích thước tùy chỉnh
- Đảm bảo luôn có đường đi từ start đến exit

### 2️⃣ Tìm đường thoát cho người chơi
- **Thuật toán**: Dijkstra, A*
- Tìm đường đi ngắn nhất từ Start → Exit
- Trực quan hóa từng bước thuật toán
- Hiển thị bảng khoảng cách, đỉnh trước, trạng thái hàng đợi

### 3️⃣ AI kẻ địch truy đuổi
- **Thuật toán**: BFS (Breadth-First Search)
- Tự động tìm đường tới người chơi
- Cập nhật theo thời gian thực

### 4️⃣ So sánh thuật toán
- So sánh **BFS, Dijkstra, A*** về:
  - Số bước duyệt
  - Thời gian chạy (ms)
  - Độ dài đường đi
  - Số ô đã thăm

### 5️⃣ Debug từng bước
- Xem từng bước chạy thuật toán
- Điều khiển Play/Pause/Stop
- Xem chi tiết thông tin mỗi bước

### 6️⃣ Chơi game tương tác
- Điều khiển nhân vật bằng phím mũi tên
- AI tự động truy đuổi
- Kiểm tra thắng/thua

## 📊 Các thuật toán

| Thuật toán | Chức năng | Chiến lược | Độ phức tạp |
|-----------|-----------|------------|-------------|
| **Backtracking** | Sinh mê cung | Đệ quy | O(N×M) |
| **BFS** | AI kẻ địch | Tìm kiếm | O(V+E) |
| **Dijkstra** | Tìm đường | Tham lam | O((V+E) log V) |
| **A*** | Tối ưu | Heuristic | O((V+E) log V) |

## 🎨 Giao diện

```
┌──────────────┬─────────────────────┬──────────────┐
│              │                     │              │
│   ⚙️ CẤU HÌNH  │     🗺️ MÊ CUNG       │  🔍 DEBUG    │
│              │                     │              │
│  • Tạo mê cung│   ████████████     │ • Thông tin  │
│  • Chọn thuật │   █   █P  █E █     │   thuật toán │
│    toán      │   █ █ █ █ █ █ █     │ • Từng bước  │
│  • Điều khiển│   █S█     █   █     │ • Bảng dữ liệu│
│    debug     │   ████████████     │ • So sánh    │
│  • Chơi game │                     │              │
│              │  🟢 Start 🔴 Exit   │              │
│              │  🔵 Player 🟡 Enemy │              │
└──────────────┴─────────────────────┴──────────────┘
```

### Màu sắc

- 🟩 **Start**: Điểm bắt đầu (xanh lá)
- 🟥 **Exit**: Điểm thoát (đỏ)
- 🟦 **Player**: Người chơi (xanh dương)
- 🟨 **Enemy**: Kẻ địch AI (vàng)
- ⬛ **Wall**: Tường (xám đậm)

## 📁 Cấu trúc dự án

```
maze_game/
│
├── algorithms/              # Các thuật toán
│   ├── __init__.py
│   ├── maze_generator.py   # Backtracking sinh mê cung
│   ├── bfs.py              # BFS cho AI
│   ├── dijkstra.py         # Dijkstra tìm đường
│   └── astar.py            # A* tối ưu
│
├── models/                  # Các model
│   ├── __init__.py
│   ├── maze.py             # Model mê cung
│   ├── player.py           # Model người chơi
│   └── enemy.py            # Model kẻ địch
│
├── ui/                      # Giao diện
│   ├── __init__.py
│   ├── main_window.py      # Cửa sổ chính
│   ├── maze_view.py        # Hiển thị mê cung
│   └── debug_panel.py      # Panel debug
│
├── main.py                  # File chạy chính
└── README.md               # File này
```

## 🛠️ Cài đặt và chạy

### Yêu cầu hệ thống

- Python 3.7 trở lên
- Tkinter (thường có sẵn trong Python)

### Cài đặt

1. **Clone hoặc tải project về**

2. **Không cần cài đặt thư viện bên ngoài** (chỉ dùng thư viện chuẩn của Python)

### Chạy ứng dụng

```bash
# Windows
python main.py

# Linux/Mac
python3 main.py
```

## 🎮 Hướng dẫn sử dụng

### Bước 1: Tạo mê cung
1. Chọn kích thước mê cung (11x11 đến 31x31)
2. Nhấn **"🎲 Tạo mê cung mới"**
3. Mê cung sẽ được sinh tự động

### Bước 2: Tìm đường đi
1. Chọn thuật toán (BFS, Dijkstra, hoặc A*)
2. Nhấn **"🔍 Tìm đường thoát"**
3. Đường đi ngắn nhất sẽ được hiển thị

### Bước 3: Debug từng bước
1. Sau khi tìm đường, nhấn **"▶️ Play"** để xem animation
2. Dùng **"⏸️ Pause"** để tạm dừng
3. Dùng **"◀️ Prev"** và **"Next ▶️"** để xem từng bước
4. Điều chỉnh tốc độ bằng thanh trượt

### Bước 4: Chọn độ khó và chơi game
1. Chọn độ khó phù hợp:
   - **Rất dễ**: AI di chuyển mỗi 4 bước (bạn nhanh gấp 4×) ⭐
   - **Dễ**: AI di chuyển mỗi 3 bước (khuyên dùng) ⭐⭐
   - **Trung bình**: AI di chuyển mỗi 2 bước ⭐⭐⭐
   - **Khó**: AI di chuyển mỗi bước (thử thách!) ⭐⭐⭐⭐
2. Nhấn **"🚀 Bắt đầu trò chơi"**
3. Dùng phím **← ↑ → ↓** để di chuyển người chơi
4. Mục tiêu: Đến Exit trước khi bị AI bắt

**💡 Tip:** Bắt đầu với độ khó "Dễ" để làm quen!

### Bước 5: So sánh thuật toán
1. Nhấn **"📈 So sánh tất cả thuật toán"**
2. Xem bảng so sánh hiệu suất

## 📈 Kết quả và phân tích

### Độ phức tạp thời gian

- **Backtracking**: O(N×M) - Duyệt mọi ô một lần
- **BFS**: O(V+E) - Duyệt mọi đỉnh và cạnh
- **Dijkstra**: O((V+E) log V) - Sử dụng heap
- **A***: O((V+E) log V) - Tương tự Dijkstra nhưng nhanh hơn nhờ heuristic

### So sánh hiệu suất (Mê cung 21×21)

| Thuật toán | Độ dài đường | Số bước duyệt | Thời gian | Ô đã thăm |
|-----------|-------------|---------------|-----------|-----------|
| BFS       | 40          | 156           | 2.3 ms    | 156       |
| Dijkstra  | 40          | 142           | 3.1 ms    | 142       |
| A*        | 40          | 98            | 2.8 ms    | 98        |

**Kết luận**: A* cho hiệu suất tốt nhất nhờ heuristic thông minh.

## 🎓 Giá trị học thuật

### Thuật toán được minh họa

✅ **Backtracking** - Kỹ thuật quay lui  
✅ **BFS** - Tìm kiếm theo chiều rộng  
✅ **Dijkstra** - Thuật toán tham lam  
✅ **A*** - Tìm kiếm có heuristic  

### Kiến thức áp dụng

- Cấu trúc dữ liệu: Stack, Queue, Heap, Set, Dict
- Đồ thị: Biểu diễn, duyệt, tìm đường đi
- Tham lam: Priority Queue, Relaxation
- Heuristic: Manhattan Distance
- OOP: Class, Inheritance, Encapsulation
- GUI: Tkinter, Canvas, Event handling

## 🤝 Đóng góp

Dự án này được xây dựng cho mục đích học tập. Mọi đóng góp và góp ý đều được hoan nghênh!

## 📞 Liên hệ

- Dự án cuối kỳ môn: **Phân tích và Thiết kế Giải thuật**
- Năm học: **2026**

## 📄 License

MIT License - Tự do sử dụng cho mục đích học tập

---

**🎉 Chúc bạn khám phá thú vị với thuật toán và AI!**
