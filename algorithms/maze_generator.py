"""
==============================================================================
THUẬT TOÁN BACKTRACKING - SINH MÊ CUNG TỰ ĐỘNG
==============================================================================

Mô tả bài toán:
    Sinh mê cung ngẫu nhiên với kích thước NxM sao cho:
    - Luôn tồn tại đường đi từ Start đến Exit
    - Mê cung có cấu trúc "perfect" (chỉ có 1 đường đi duy nhất)

Chiến lược: ĐỆ QUY + QUAY LUI (Backtracking)
    1. Bắt đầu từ một ô, đánh dấu là đường đi
    2. Chọn ngẫu nhiên một hướng chưa thăm
    3. Phá tường giữa ô hiện tại và ô kế tiếp
    4. Nếu không còn hướng nào -> QUAY LUI (Backtrack)
    5. Lặp lại đến khi Stack rỗng

Độ phức tạp:
    - Thời gian: O(N × M) - duyệt mỗi ô tối đa 1 lần
    - Không gian: O(N × M) - lưu ma trận và Stack

Cấu trúc dữ liệu:
    - Stack (List): Lưu các ô đã đi qua để quay lui
    - Set: Đánh dấu các ô đã thăm - O(1) lookup

Tham khảo: Chương 3 - Đệ quy và chiến lược quay lui
==============================================================================
"""

import random
from typing import List, Tuple, Set


class MazeGenerator:
    """
    Lớp sinh mê cung sử dụng thuật toán Backtracking.
    
    Thuật toán tạo ra "perfect maze" - mê cung mà giữa 2 điểm bất kỳ
    chỉ có đúng 1 đường đi duy nhất.
    """
    
    def __init__(self, width: int, height: int):
        """
        Khởi tạo bộ sinh mê cung.

        Args:
            width: Chiều rộng mê cung (số cột, nên là số LẺ)
            height: Chiều cao mê cung (số hàng, nên là số LẺ)
        """
        self.width = width
        self.height = height
        # Khởi tạo toàn bộ là tường (1), sau đó đào đường (0)
        self.maze = [[1 for _ in range(width)] for _ in range(height)]
        # Lưu các bước để debug và trực quan hóa quá trình sinh
        self.steps = []

    def generate(self) -> Tuple[List[List[int]], List]:
        """
        Sinh mê cung bằng thuật toán Backtracking (DFS + Random).

        Thuật toán:
            1. Push ô bắt đầu vào Stack
            2. Lặp khi Stack không rỗng:
               a. Lấy ô trên cùng Stack (KHÔNG pop)
               b. Nếu có ô kề chưa thăm -> chọn ngẫu nhiên, phá tường, push
               c. Nếu không -> pop Stack (QUAY LUI)
            3. Kết thúc khi Stack rỗng

        Returns:
            maze: Ma trận mê cung (0 = đường đi, 1 = tường)
            steps: Các bước sinh mê cung để debug/trực quan hóa
        """
        self.steps = []

        # ===== BƯỚC 1: KHỞI TẠO =====
        # Bắt đầu từ ô (1, 1) - tránh viền ngoài
        start_x, start_y = 1, 1
        self.maze[start_y][start_x] = 0  # Đánh dấu là đường đi

        # Stack để thực hiện DFS và quay lui
        stack = [(start_x, start_y)]
        # Tập các ô đã thăm - dùng Set để lookup O(1)
        visited = {(start_x, start_y)}
        
        # ===== BƯỚC 2: VÒNG LẶP CHÍNH =====
        while stack:
            # Lấy ô trên cùng Stack (không pop ngay)
            current_x, current_y = stack[-1]

            # Lưu bước hiện tại để trực quan hóa
            self.steps.append({
                'maze': [row[:] for row in self.maze],  # Copy ma trận
                'current': (current_x, current_y),
                'stack_size': len(stack)
            })

            # Tìm các ô kế tiếp chưa thăm (cách 2 ô để có chỗ cho tường)
            neighbors = self._get_unvisited_neighbors(current_x, current_y, visited)

            if neighbors:
                # ===== TRƯỜNG HỢP 1: CÒN Ô CHƯA THĂM =====
                # Chọn ngẫu nhiên một ô kế tiếp
                next_x, next_y = random.choice(neighbors)

                # Phá tường giữa ô hiện tại và ô kế tiếp
                wall_x = (current_x + next_x) // 2
                wall_y = (current_y + next_y) // 2
                self.maze[wall_y][wall_x] = 0  # Phá tường
                self.maze[next_y][next_x] = 0  # Đánh dấu ô mới là đường

                # Đánh dấu đã thăm và thêm vào stack
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
            else:
                # ===== TRƯỜNG HỢP 2: KHÔNG CÒN Ô NÀO - QUAY LUI =====
                stack.pop()

        # ===== BƯỚC 3: HOÀN TẤT =====
        # Đảm bảo điểm Start và Exit là đường đi
        self.maze[1][1] = 0                              # Start (góc trái-trên)
        self.maze[self.height - 2][self.width - 2] = 0   # Exit (góc phải-dưới)
        
        return self.maze, self.steps
    
    def _get_unvisited_neighbors(self, x: int, y: int, visited: Set[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Lấy danh sách các ô kế tiếp chưa thăm.
        
        Lưu ý: Các ô kế tiếp cách 2 ô (không phải 1) để chừa chỗ cho tường.

        Args:
            x, y: Tọa độ ô hiện tại
            visited: Tập các ô đã thăm

        Returns:
            Danh sách các ô kế tiếp hợp lệ (chưa thăm và trong biên)
        """
        neighbors = []
        # 4 hướng: Lên(-2), Phải(+2), Xuống(+2), Trái(-2)
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy

            # Kiểm tra trong biên (tránh viền ngoài) và chưa thăm
            if (1 <= new_x < self.width - 1 and 
                1 <= new_y < self.height - 1 and 
                (new_x, new_y) not in visited):
                neighbors.append((new_x, new_y))

        return neighbors

    def get_complexity_info(self) -> dict:
        """
        Trả về thông tin độ phức tạp và đặc điểm của thuật toán.
        
        Dùng để hiển thị trong Debug Panel.

        Returns:
            Dict chứa thông tin phân tích thuật toán
        """
        return {
            'name': 'Backtracking (Quay lui)',
            'time_complexity': 'O(N × M)',
            'space_complexity': 'O(N × M)',
            'description': 'Dùng Stack để quay lui khi gặp ngõ cụt, đảm bảo duyệt hết mọi ô.',
            'advantages': [
                'Tạo mê cung "perfect" (chỉ 1 đường đi)',
                'Đảm bảo mọi ô đều có thể tiếp cận',
                'Dễ hiểu và cài đặt',
                'Áp dụng được cho nhiều bài toán khác'
            ],
            'disadvantages': [
                'Mê cung có xu hướng tuyến tính (ít nhánh)',
                'Không tối ưu cho mê cung phức tạp',
                'Stack sâu với mê cung lớn'
            ]
        }
