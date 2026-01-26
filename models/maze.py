"""
==============================================================================
MODEL MAZE - QUẢN LÝ MÊ CUNG
==============================================================================

Mô tả:
    Class Maze đại diện cho cấu trúc dữ liệu mê cung trong game.
    Mê cung được biểu diễn dưới dạng ma trận 2D (grid) với:
    - 0: Đường đi (có thể di chuyển)
    - 1: Tường (không thể di chuyển)

Cấu trúc dữ liệu:
    - grid: List[List[int]] - Ma trận 2D lưu trạng thái các ô
    - Truy cập: grid[y][x] (hàng trước, cột sau)

Tọa độ:
    - (0, 0): Góc trên bên trái
    - (width-1, height-1): Góc dưới bên phải
    - x tăng về phải, y tăng xuống dưới

Sử dụng với các thuật toán:
    - Backtracking: Sinh mê cung ngẫu nhiên
    - BFS, Dijkstra, A*: Tìm đường đi trong mê cung
==============================================================================
"""

from typing import List, Tuple


class Maze:
    """
    Lớp Maze quản lý cấu trúc và trạng thái của mê cung.
    
    Attributes:
        width: Chiều rộng mê cung (số cột)
        height: Chiều cao mê cung (số hàng)
        grid: Ma trận 2D lưu trữ mê cung
        start_pos: Vị trí bắt đầu
        exit_pos: Vị trí đích (lối thoát)
    """
    
    def __init__(self, width: int = 21, height: int = 21):
        """
        Khởi tạo mê cung với kích thước cho trước.
        
        Tại sao dùng số lẻ?
            - Thuật toán Backtracking tạo tường ở các vị trí chẵn
            - Đường đi ở các vị trí lẻ
            - Số lẻ đảm bảo có biên tường bao quanh
        
        Args:
            width: Chiều rộng (nên là số lẻ, mặc định 21)
            height: Chiều cao (nên là số lẻ, mặc định 21)
        """
        self.width = width
        self.height = height
        # Khởi tạo tất cả là tường (1)
        self.grid = [[1 for _ in range(width)] for _ in range(height)]
        # Vị trí mặc định: start ở góc trên trái, exit ở góc dưới phải
        self.start_pos = (1, 1)
        self.exit_pos = (width - 2, height - 2)
        
    def set_grid(self, grid: List[List[int]]):
        """
        Thiết lập lưới mê cung từ ma trận có sẵn.
        
        Được gọi sau khi thuật toán Backtracking sinh mê cung.
        
        Args:
            grid: Ma trận mê cung (0 = đường, 1 = tường)
        """
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        
    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Kiểm tra vị trí có hợp lệ để di chuyển không.
        
        Điều kiện hợp lệ:
            1. Nằm trong biên mê cung (0 <= x < width, 0 <= y < height)
            2. Là đường đi (grid[y][x] == 0)
        
        Args:
            x: Tọa độ x (cột)
            y: Tọa độ y (hàng)
            
        Returns:
            True nếu có thể di chuyển đến vị trí này
        """
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.grid[y][x] == 0)
    
    def is_wall(self, x: int, y: int) -> bool:
        """
        Kiểm tra vị trí có phải là tường không.
        
        Lưu ý: Vị trí ngoài biên cũng được coi là tường
        
        Args:
            x: Tọa độ x (cột)
            y: Tọa độ y (hàng)
            
        Returns:
            True nếu là tường hoặc ngoài biên
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] == 1
        return True  # Ngoài biên = tường
    
    def get_cell(self, x: int, y: int) -> int:
        """
        Lấy giá trị của một ô trong mê cung.
        
        Args:
            x: Tọa độ x (cột)
            y: Tọa độ y (hàng)
            
        Returns:
            0 nếu là đường đi
            1 nếu là tường hoặc ngoài biên
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return 1  # Ngoài biên = tường
    
    def set_start(self, x: int, y: int):
        """
        Thiết lập điểm bắt đầu của mê cung.
        
        Args:
            x, y: Tọa độ điểm bắt đầu
        """
        self.start_pos = (x, y)
        
    def set_exit(self, x: int, y: int):
        """
        Thiết lập điểm thoát (đích) của mê cung.
        
        Args:
            x, y: Tọa độ lối thoát
        """
        self.exit_pos = (x, y)
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Lấy danh sách các ô kề hợp lệ (có thể di chuyển đến).
        
        Đây là hàm quan trọng được sử dụng bởi các thuật toán tìm đường:
        - BFS: Duyệt các ô kề theo thứ tự
        - Dijkstra/A*: Xét các ô kề để cập nhật chi phí
        
        Args:
            x: Tọa độ x của ô hiện tại
            y: Tọa độ y của ô hiện tại
            
        Returns:
            Danh sách các ô kề có thể di chuyển đến
            Thứ tự: Lên, Phải, Xuống, Trái
        """
        neighbors = []
        # 4 hướng di chuyển: Lên (0,-1), Phải (1,0), Xuống (0,1), Trái (-1,0)
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            # Chỉ thêm vào nếu là đường đi hợp lệ
            if self.is_valid_position(new_x, new_y):
                neighbors.append((new_x, new_y))
        
        return neighbors
