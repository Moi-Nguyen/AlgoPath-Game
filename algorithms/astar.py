"""
==============================================================================
THUẬT TOÁN A* (A-STAR) - TÌM ĐƯỜNG TỐI ƯU VỚI HEURISTIC
==============================================================================

Mô tả bài toán:
    Tìm đường đi ngắn nhất từ Start đến Goal, nhưng NHANH HƠN Dijkstra
    bằng cách sử dụng hàm heuristic để hướng về đích.

Ứng dụng trong game:
    - Tìm đường tối ưu cho người chơi
    - Được sử dụng rộng rãi trong game pathfinding (RPG, RTS, ...)

Chiến lược: THAM LAM + HEURISTIC
    Kết hợp ưu điểm của Dijkstra (đảm bảo tối ưu) và Greedy Best-First
    (hướng về đích nhanh).

Công thức cốt lõi:
    f(n) = g(n) + h(n)
    - g(n): Chi phí THỰC TẾ từ Start đến n (như Dijkstra)
    - h(n): Chi phí ƯỚC LƯỢNG từ n đến Goal (heuristic)
    - f(n): Tổng chi phí ước tính đi qua n

Heuristic - Khoảng cách Manhattan:
    h(n) = |x_n - x_goal| + |y_n - y_goal|
    
    Tính chất quan trọng:
    - ADMISSIBLE: Không bao giờ đánh giá cao hơn chi phí thực
    - CONSISTENT: h(n) ≤ cost(n, n') + h(n') với mọi n'
    => Đảm bảo A* tìm được đường NGẮN NHẤT

Độ phức tạp:
    - Thời gian: O((V + E) log V) - THỰC TẾ nhanh hơn Dijkstra nhiều
    - Không gian: O(V)

Tại sao A* nhanh hơn?
    - Dijkstra duyệt đều tất cả các hướng (như vòng tròn)
    - A* ưu tiên hướng về đích (như hình elip hướng về goal)
    => Duyệt ÍT Ô HƠN mà vẫn đảm bảo tối ưu

Tham khảo: Chương 6 - Chiến lược tham lam (mở rộng với heuristic)
==============================================================================
"""

import heapq
from typing import List, Tuple, Optional, Dict


class AStar:
    """
    Lớp triển khai thuật toán A* cho bài toán tìm đường trong mê cung.
    
    Đặc điểm:
        - Kết hợp Dijkstra + Heuristic
        - f(n) = g(n) + h(n) với h là Manhattan distance
        - Nhanh hơn Dijkstra nhờ hướng về đích
        - Vẫn đảm bảo tìm đường ngắn nhất (nếu h admissible)
    
    Attributes:
        maze: Ma trận mê cung 2D
        height: Chiều cao mê cung
        width: Chiều rộng mê cung
        steps: Danh sách các bước để trực quan hóa
    """
    
    def __init__(self, maze: List[List[int]]):
        """
        Khởi tạo thuật toán A*.

        Args:
            maze: Ma trận mê cung (0 = đường đi, 1 = tường)
        """
        self.maze = maze
        self.height = len(maze)
        self.width = len(maze[0])
        # Lưu các bước để debug và trực quan hóa
        self.steps = []
        
    def heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """
        Hàm heuristic: Khoảng cách Manhattan.

        Công thức: h(n) = |x1 - x2| + |y1 - y2|

        Tính chất quan trọng:
            - ADMISSIBLE: Không bao giờ đánh giá cao hơn chi phí thực
              (vì trong mê cung ta chỉ đi 4 hướng, không đi chéo)
            - CONSISTENT: h(n) ≤ d(n,n') + h(n') với mọi n'
            => Đảm bảo A* tìm được đường NGẮN NHẤT

        Args:
            pos: Vị trí hiện tại (x, y)
            goal: Vị trí đích (x, y)

        Returns:
            Khoảng cách Manhattan (số nguyên)
        """
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Tuple[List[Tuple[int, int]], List, Dict]:
        """
        Tìm đường đi ngắn nhất từ start đến goal bằng A*.

        Thuật toán:
            1. Khởi tạo g[start] = 0, f[start] = h(start, goal)
            2. Push (f[start], g[start], start) vào Heap
            3. Lặp khi Heap không rỗng:
               - Pop đỉnh có f nhỏ nhất (THÔNG MINH hơn Dijkstra)
               - Nếu đã thăm -> bỏ qua
               - Nếu là đích -> tái tạo đường đi
               - Duyệt các đỉnh kề, cập nhật g và f
            4. Trả về đường đi và các bảng dữ liệu

        Args:
            start: Tọa độ bắt đầu (x, y)
            goal: Tọa độ đích (x, y)

        Returns:
            path: Danh sách các ô trên đường đi ngắn nhất
            steps: Các bước để trực quan hóa
            tables: Dict chứa {g_score, f_score, previous, visited}
        """
        self.steps = []

        # ===== KHỞI TẠO =====
        # g_score[n]: Chi phí THỰC TẾ từ start đến n
        g_score = {start: 0}

        # f_score[n]: g(n) + h(n) = tổng chi phí ước tính qua n
        f_score = {start: self.heuristic(start, goal)}

        # previous[n]: Đỉnh trước n trên đường đi tối ưu
        previous = {}

        # Min-Heap: (f_score, g_score, x, y) - ưu tiên f nhỏ nhất
        # Thêm g_score để tie-breaking khi f bằng nhau
        heap = [(f_score[start], 0, start[0], start[1])]
        visited = set()

        # 4 hướng di chuyển: lên, phải, xuống, trái
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        # ===== VÒNG LẶP CHÍNH =====
        while heap:
            # Lấy đỉnh có f nhỏ nhất (THÔNG MINH: ưu tiên hướng về đích)
            current_f, current_g, x, y = heapq.heappop(heap)
            current = (x, y)

            # Bỏ qua nếu đã xử lý rồi
            if current in visited:
                continue

            visited.add(current)

            # Lưu bước hiện tại để trực quan hóa
            self.steps.append({
                'current': current,
                'visited': visited.copy(),
                'g_score': g_score.copy(),
                'f_score': f_score.copy(),
                'heap_size': len(heap),
                'current_g': current_g,
                'current_f': current_f,
                'heuristic': self.heuristic(current, goal)
            })

            # ===== KIỂM TRA ĐÃ ĐẾN ĐÍCH =====
            if current == goal:
                path = self._reconstruct_path(previous, start, goal)
                tables = {
                    'g_score': g_score,
                    'f_score': f_score,
                    'previous': previous,
                    'visited': visited
                }
                return path, self.steps, tables
            
            # ===== DUYỆT CÁC Ô KỀ (RELAX) =====
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                neighbor = (new_x, new_y)
                
                # Kiểm tra ô có hợp lệ không
                # - Nằm trong biên mê cung
                # - Không phải tường (maze[y][x] == 0)
                # - Chưa được thăm
                if (0 <= new_x < self.width and 
                    0 <= new_y < self.height and 
                    self.maze[new_y][new_x] == 0 and 
                    neighbor not in visited):
                    
                    # Tính g_score tạm thời (qua current)
                    # g(neighbor) = g(current) + weight(current, neighbor)
                    tentative_g = current_g + 1  # weight = 1 cho mỗi bước
                    
                    # ===== RELAX OPERATION =====
                    # Cập nhật nếu tìm được đường ngắn hơn đến neighbor
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        # Cập nhật chi phí thực tế
                        g_score[neighbor] = tentative_g
                        
                        # Tính f(n) = g(n) + h(n) - CÔNG THỨC CỐT LÕI CỦA A*
                        f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal)
                        
                        # Lưu đường đi
                        previous[neighbor] = current
                        
                        # Push vào Heap với f_score làm ưu tiên
                        heapq.heappush(heap, (f_score[neighbor], tentative_g, new_x, new_y))
        
        # Không tìm thấy đường đi (mê cung không có lối)
        return [], self.steps, {'g_score': g_score, 'f_score': f_score, 'previous': previous, 'visited': visited}
    
    def _reconstruct_path(self, previous: Dict, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Tái tạo đường đi từ bảng previous.
        
        Thuật toán:
            1. Bắt đầu từ goal
            2. Lần ngược về start theo previous
            3. Đảo ngược danh sách để có đường đi đúng chiều
        
        Args:
            previous: Bảng đỉnh trước (previous[v] = u nghĩa là đến v qua u)
            start: Điểm bắt đầu
            goal: Điểm kết thúc
            
        Returns:
            Danh sách các ô trên đường đi từ start đến goal
        """
        path = []
        current = goal
        
        # Lần ngược từ goal về start
        while current != start:
            path.append(current)
            if current not in previous:
                # Không có đường đi
                return []
            current = previous[current]
        
        # Thêm điểm bắt đầu
        path.append(start)
        
        # Đảo ngược để có đường đi từ start -> goal
        path.reverse()
        
        return path
    
    def get_complexity_info(self) -> dict:
        """
        Trả về thông tin độ phức tạp thuật toán A*.
        
        Phân tích:
            - Thời gian: O((V + E) log V)
              + Mỗi đỉnh được xử lý tối đa 1 lần
              + Mỗi cạnh được xét tối đa 1 lần
              + Mỗi thao tác Heap là O(log V)
              + Thực tế: NHANH HƠN Dijkstra nhiều nhờ heuristic
              
            - Không gian: O(V)
              + g_score, f_score: O(V)
              + previous: O(V)
              + Heap: O(V)
              + visited: O(V)
        
        Returns:
            Dict chứa thông tin phân tích thuật toán
        """
        return {
            'name': 'A* (A-Star)',
            'time_complexity': 'O((V + E) log V)',
            'space_complexity': 'O(V)',
            'description': 'Kết hợp Dijkstra và heuristic để tìm đường tối ưu nhanh hơn',
            'formula': 'f(n) = g(n) + h(n)',
            'heuristic': 'Manhattan distance: h(n) = |x_n - x_goal| + |y_n - y_goal|',
            'advantages': [
                'Nhanh hơn Dijkstra đáng kể nhờ heuristic',
                'Vẫn đảm bảo tìm đường ngắn nhất (h admissible)',
                'Sử dụng heuristic thông minh để hướng về đích',
                'Chuẩn công nghiệp cho game pathfinding'
            ],
            'disadvantages': [
                'Hiệu quả phụ thuộc vào chất lượng heuristic',
                'Phức tạp hơn BFS và Dijkstra khi implement',
                'Cần thêm bộ nhớ cho f_score'
            ],
            'comparison_dijkstra': 'A* duyệt ít ô hơn Dijkstra vì ưu tiên hướng về đích'
        }
