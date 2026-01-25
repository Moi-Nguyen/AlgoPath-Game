"""
==============================================================================
THUẬT TOÁN BFS (BREADTH-FIRST SEARCH) - TÌM KIẾM THEO CHIỀU RỘNG
==============================================================================

Mô tả bài toán:
    Tìm đường đi ngắn nhất từ điểm A đến điểm B trong mê cung.
    
Ứng dụng trong game:
    - AI kẻ địch tìm đường ngắn nhất đến người chơi để truy đuổi
    - Cập nhật đường đi real-time khi người chơi di chuyển

Chiến lược: TÌM KIẾM THEO CHIỀU RỘNG
    - Sử dụng hàng đợi (Queue) - FIFO
    - Duyệt các đỉnh theo thứ tự khoảng cách tăng dần từ nguồn
    - Đảm bảo tìm được đường ngắn nhất (với trọng số = 1)

Ý tưởng:
    1. Thêm điểm bắt đầu vào Queue
    2. Lặp: Lấy đỉnh đầu Queue (dequeue), duyệt các đỉnh kề chưa thăm
    3. Thêm các đỉnh kề vào cuối Queue (enqueue)
    4. Dừng khi đến đích hoặc Queue rỗng

Độ phức tạp:
    - Thời gian: O(V + E) - V là số đỉnh, E là số cạnh
    - Không gian: O(V) - lưu Queue và visited

Cấu trúc dữ liệu:
    - Queue (deque): FIFO, enqueue/dequeue O(1)
    - Set: Đánh dấu đỉnh đã thăm - O(1) lookup

Tham khảo: Chương 2 - Sắp xếp và tìm kiếm
==============================================================================
"""

from collections import deque
from typing import List, Tuple, Optional, Dict


class BFS:
    """
    Lớp triển khai thuật toán BFS cho bài toán tìm đường trong mê cung.
    
    Đặc điểm:
        - Sử dụng Queue (FIFO) để duyệt đỉnh
        - Đảm bảo tìm đường ngắn nhất khi trọng số = 1
        - Phù hợp cho AI truy đuổi real-time
    """
    
    def __init__(self, maze: List[List[int]]):
        """
        Khởi tạo thuật toán BFS.

        Args:
            maze: Ma trận mê cung (0 = đường đi, 1 = tường)
        """
        self.maze = maze
        self.height = len(maze)
        self.width = len(maze[0])
        # Lưu các bước để debug và trực quan hóa
        
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], List]:
        """
        Tìm đường đi ngắn nhất từ start đến goal bằng BFS.

        Thuật toán:
            1. Khởi tạo Queue với điểm bắt đầu
            2. Lặp khi Queue không rỗng:
               - Dequeue đỉnh đầu tiên
               - Nếu là đích -> trả về đường đi
               - Duyệt 4 hướng kề, enqueue các ô hợp lệ
            3. Trả về [] nếu không tìm thấy

        Args:
            start: Tọa độ bắt đầu (x, y)
            goal: Tọa độ đích (x, y)

        Returns:
            path: Danh sách các ô trên đường đi ngắn nhất
            steps: Các bước để trực quan hóa quá trình tìm kiếm
        """
        self.steps = []

        # ===== KHỞI TẠO =====
        # Queue chứa: (x, y, đường_đi_đến_ô_này)
        # Dùng deque để enqueue/dequeue O(1)
        queue = deque([(start[0], start[1], [start])])
        # Tập các ô đã thăm để tránh duyệt lại - O(1) lookup
        visited = {start}

        # 4 hướng di chuyển: Lên, Phải, Xuống, Trái
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        # ===== VÒNG LẶP CHÍNH =====
        while queue:
            # Lấy đỉnh đầu Queue (FIFO)
            x, y, path = queue.popleft()

            # Lưu bước hiện tại để trực quan hóa
            self.steps.append({
                'current': (x, y),
                'visited': visited.copy(),
                'queue_size': len(queue),
                'path': path.copy()
            })

            # ===== KIỂM TRA ĐÃ ĐẾN ĐÍCH =====
            if (x, y) == goal:
                return path, self.steps

            # ===== DUYỆT CÁC Ô KẾ TIẾP =====
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy

                # Kiểm tra hợp lệ: trong biên, là đường đi, chưa thăm
                if (0 <= new_x < self.width and 
                    0 <= new_y < self.height and 
                    self.maze[new_y][new_x] == 0 and 
                    (new_x, new_y) not in visited):
                    
                    # Đánh dấu đã thăm NGAY để tránh thêm trùng vào Queue
                    visited.add((new_x, new_y))
                    # Thêm vào cuối Queue (FIFO)
                    new_path = path + [(new_x, new_y)]
                    queue.append((new_x, new_y, new_path))

        # Không tìm thấy đường đi
    def get_next_move(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Lấy bước đi tiếp theo cho AI (tối ưu, không cần đường đi đầy đủ).
        
        Hàm này được gọi mỗi khi AI cần di chuyển, chỉ trả về
        bước đi tiếp theo thay vì toàn bộ đường đi.

        Args:
            start: Vị trí hiện tại của AI (kẻ địch)
            goal: Vị trí mục tiêu (người chơi)

        Returns:
            Tọa độ bước đi tiếp theo hoặc None nếu không có đường
        """
        path, _ = self.find_path(start, goal)

        if len(path) > 1:
            return path[1]  # Trả về bước đi tiếp theo (bỏ qua vị trí hiện tại)
        return None

    def get_complexity_info(self) -> dict:
        """
        Trả về thông tin độ phức tạp và đặc điểm của thuật toán.
        
        Dùng để hiển thị trong Debug Panel.

        Returns:
            Dict chứa thông tin phân tích thuật toán
        """
        return {
            'name': 'BFS (Breadth-First Search)',
            'time_complexity': 'O(V + E)',
            'space_complexity': 'O(V)',
            'description': 'Duyệt theo chiều rộng, đảm bảo tìm đường ngắn nhất khi trọng số bằng nhau.',
            'advantages': [
                'Tìm được đường đi ngắn nhất (trọng số = 1)',
                'Đơn giản, dễ cài đặt',
                'Phù hợp cho AI real-time',
                'Thời gian O(V+E) tuyến tính'
            ],
            'disadvantages': [
                'Tốn bộ nhớ với đồ thị lớn (lưu Queue)',
                'Không tối ưu khi có trọng số khác nhau',
                'Không sử dụng heuristic',
                'Duyệt nhiều ô không cần thiết'
            ]
        }
