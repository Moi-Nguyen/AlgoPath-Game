"""
==============================================================================
THUẬT TOÁN DIJKSTRA - TÌM ĐƯỜNG NGẮN NHẤT (CHIẾN LƯỢC THAM LAM)
==============================================================================

Mô tả bài toán:
    Tìm đường đi ngắn nhất từ một đỉnh nguồn đến tất cả các đỉnh khác
    trong đồ thị có trọng số KHÔNG ÂM.

Ứng dụng trong game:
    - Người chơi tìm đường ngắn nhất đến Exit
    - Hiển thị gợi ý đường đi tối ưu

Chiến lược: THAM LAM (Greedy)
    - Luôn chọn đỉnh có khoảng cách nhỏ nhất chưa được xử lý
    - Cập nhật (relax) khoảng cách các đỉnh kề
    - Sử dụng Priority Queue để lấy min hiệu quả

Ý tưởng:
    1. Khởi tạo d[start] = 0, d[others] = ∞
    2. Lặp: Chọn đỉnh u có d[u] nhỏ nhất chưa xét
    3. Với mỗi đỉnh v kề u: nếu d[u] + w(u,v) < d[v] thì cập nhật
    4. Dừng khi đến đích hoặc hết đỉnh

Cấu trúc dữ liệu:
    - Min-Heap (heapq): Lấy đỉnh có d nhỏ nhất - O(log V)
    - Dictionary: Lưu distances và previous - O(1) lookup
    - Set: Đánh dấu đỉnh đã xử lý

Độ phức tạp:
    - Thời gian: O((V + E) log V) với Binary Heap
    - Không gian: O(V)

Tham khảo: Chương 6 - Chiến lược tham lam
==============================================================================
"""

import heapq
from typing import List, Tuple, Optional, Dict


class Dijkstra:
    """
    Lớp triển khai thuật toán Dijkstra cho bài toán tìm đường trong mê cung.
    
    Đặc điểm:
        - Chiến lược THAM LAM: luôn chọn đỉnh có khoảng cách nhỏ nhất
        - Sử dụng Min-Heap để tối ưu việc chọn đỉnh
        - Đảm bảo tìm đường ngắn nhất với trọng số không âm
    """
    
    def __init__(self, maze: List[List[int]]):
        """
        Khởi tạo thuật toán Dijkstra.

        Args:
            maze: Ma trận mê cung (0 = đường đi, 1 = tường)
        """
        self.maze = maze
        self.height = len(maze)
        self.width = len(maze[0])
        # Lưu các bước để debug và trực quan hóa
        
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], List, Dict]:
        """
        Tìm đường đi ngắn nhất từ start đến goal bằng Dijkstra.

        Thuật toán (Tham lam):
            1. d[start] = 0, push (0, start) vào Heap
            2. Lặp khi Heap không rỗng:
               - Pop đỉnh có d nhỏ nhất (THAM LAM)
               - Nếu đã thăm -> bỏ qua
               - Nếu là đích -> tái tạo đường đi
               - Duyệt các đỉnh kề, RELAX nếu tìm được đường ngắn hơn
            3. Trả về đường đi và các bảng dữ liệu

        Args:
            start: Tọa độ bắt đầu (x, y)
            goal: Tọa độ đích (x, y)

        Returns:
            path: Danh sách các ô trên đường đi ngắn nhất
            steps: Các bước để trực quan hóa
            tables: Dict chứa {distances, previous, visited}
        """
        self.steps = []

        # ===== KHỞI TẠO =====
        # distances[v] = khoảng cách ngắn nhất từ start đến v
        distances = {start: 0}

        # previous[v] = đỉnh trước v trên đường đi ngắn nhất (để tái tạo path)
        previous = {}

        # Min-Heap: (khoảng_cách, x, y) - luôn pop đỉnh có d nhỏ nhất
        heap = [(0, start[0], start[1])]
        # Tập các đỉnh đã xử lý xong (không cần xét lại)
        visited = set()

        # 4 hướng di chuyển: Lên, Phải, Xuống, Trái
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        # ===== VÒNG LẶP CHÍNH =====
        while heap:
            # THAM LAM: Lấy đỉnh có khoảng cách nhỏ nhất
            current_dist, x, y = heapq.heappop(heap)
            current = (x, y)

            # Bỏ qua nếu đã xử lý (có thể có nhiều entry trong heap)
            if current in visited:
                continue

            # Đánh dấu đã xử lý
            visited.add(current)

            # Lưu bước hiện tại để trực quan hóa
            self.steps.append({
                'current': current,
                'visited': visited.copy(),
                'distances': distances.copy(),
                'heap_size': len(heap),
                'current_distance': current_dist
            })

            # ===== KIỂM TRA ĐÃ ĐẾN ĐÍCH =====
            if current == goal:
                path = self._reconstruct_path(previous, start, goal)
                tables = {
                    'distances': distances,
                    'previous': previous,
                    'visited': visited
                }
                return path, self.steps, tables

            # ===== DUYỆT CÁC ĐỈNH KỀ (RELAX) =====
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                neighbor = (new_x, new_y)

                # Kiểm tra hợp lệ: trong biên, là đường đi, chưa xử lý
                if (0 <= new_x < self.width and 
                    0 <= new_y < self.height and 
                    self.maze[new_y][new_x] == 0 and 
                    neighbor not in visited):

                    # Tính khoảng cách mới (mỗi bước = 1 đơn vị)
                    new_dist = current_dist + 1

                    # RELAX: Nếu tìm được đường ngắn hơn, cập nhật
                    if neighbor not in distances or new_dist < distances[neighbor]:
                        distances[neighbor] = new_dist
                        previous[neighbor] = current
                        # Thêm vào Heap (có thể có nhiều entry cho cùng đỉnh)
                        heapq.heappush(heap, (new_dist, new_x, new_y))

        # Không tìm thấy đường đi
        return [], self.steps, {'distances': distances, 'previous': previous, 'visited': visited}

    def _reconstruct_path(self, previous: Dict, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Tái tạo đường đi từ bảng previous.
        
        Thuật toán: Truy ngược từ goal về start theo bảng previous.

        Args:
            previous: Bảng đỉnh trước (previous[v] = đỉnh đến trước v)
            start: Điểm bắt đầu
            goal: Điểm kết thúc

        Returns:
            Danh sách các ô trên đường đi (từ start đến goal)
        """
        path = []
        current = goal

        # Truy ngược từ goal về start
        while current != start:
            path.append(current)
            if current not in previous:
                return []  # Không có đường đi
            current = previous[current]

        path.append(start)
        path.reverse()  # Đảo ngược để có thứ tự từ start -> goal

        return path

    def get_complexity_info(self) -> dict:
        """
        Trả về thông tin độ phức tạp và đặc điểm của thuật toán.
        
        Dùng để hiển thị trong Debug Panel.

        Returns:
            Dict chứa thông tin phân tích thuật toán
        """
        return {
            'name': 'Dijkstra (Tham lam)',
            'time_complexity': 'O((V + E) log V)',
            'space_complexity': 'O(V)',
            'description': 'Chiến lược THAM LAM: luôn chọn đỉnh có khoảng cách nhỏ nhất, dùng Heap tối ưu.',
            'advantages': [
                'Tìm được đường đi ngắn nhất CHÍNH XÁC',
                'Hiệu quả với đồ thị có trọng số không âm',
                'Phù hợp cho đồ thị lớn',
                'Cung cấp thông tin khoảng cách đến mọi đỉnh'
            ],
            'disadvantages': [
                'Chậm hơn BFS khi trọng số bằng nhau',
                'Không sử dụng heuristic để tối ưu hướng',
                'Phức tạp hơn BFS',
                'Duyệt nhiều ô không cần thiết'
            ]
        }
