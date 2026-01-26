"""
==============================================================================
MODEL PLAYER - QUẢN LÝ NGƯỜI CHƠI
==============================================================================

Mô tả:
    Class Player đại diện cho nhân vật người chơi trong game mê cung.
    Quản lý vị trí, lịch sử di chuyển và các thao tác di chuyển.

Thuộc tính:
    - x, y: Vị trí hiện tại của người chơi
    - path_history: Lịch sử các vị trí đã đi qua
    - moves: Tổng số bước đi (dùng để tính điểm)

Tương tác với thuật toán:
    - Dijkstra/A*: Tính đường đi ngắn nhất cho người chơi
    - Người chơi có thể di chuyển thủ công hoặc theo đường gợi ý
==============================================================================
"""

from typing import Tuple


class Player:
    """
    Lớp Player quản lý trạng thái và hành vi của người chơi.
    
    Attributes:
        x: Tọa độ x hiện tại (cột)
        y: Tọa độ y hiện tại (hàng)
        path_history: Danh sách các vị trí đã đi qua
        moves: Số bước đã di chuyển
    """
    
    def __init__(self, x: int, y: int):
        """
        Khởi tạo người chơi tại vị trí ban đầu.
        
        Args:
            x: Tọa độ x ban đầu
            y: Tọa độ y ban đầu
        """
        self.x = x
        self.y = y
        # Lịch sử di chuyển - dùng để vẽ đường đi đã qua
        self.path_history = [(x, y)]
        # Đếm số bước - dùng để tính điểm
        self.moves = 0
        
    def move(self, new_x: int, new_y: int):
        """
        Di chuyển người chơi đến vị trí mới.
        
        Cập nhật:
            - Vị trí hiện tại (x, y)
            - Thêm vào lịch sử di chuyển
            - Tăng số bước đi
        
        Args:
            new_x: Tọa độ x mới
            new_y: Tọa độ y mới
        """
        self.x = new_x
        self.y = new_y
        self.path_history.append((new_x, new_y))
        self.moves += 1
        
    def get_position(self) -> Tuple[int, int]:
        """
        Lấy vị trí hiện tại của người chơi.
        
        Returns:
            Tuple (x, y) - vị trí hiện tại
        """
        return (self.x, self.y)
    
    def reset(self, x: int, y: int):
        """
        Reset người chơi về vị trí mới (khi bắt đầu game mới).
        
        Xóa toàn bộ lịch sử và đặt lại số bước về 0.
        
        Args:
            x: Tọa độ x mới
            y: Tọa độ y mới
        """
        self.x = x
        self.y = y
        self.path_history = [(x, y)]
        self.moves = 0
    
    def can_move_to(self, maze, new_x: int, new_y: int) -> bool:
        """
        Kiểm tra người chơi có thể di chuyển đến vị trí không.
        
        Điều kiện di chuyển hợp lệ:
            1. Vị trí mới kề với vị trí hiện tại (Manhattan distance = 1)
            2. Vị trí mới không phải tường
        
        Args:
            maze: Đối tượng Maze để kiểm tra tường
            new_x: Tọa độ x muốn đi đến
            new_y: Tọa độ y muốn đi đến
            
        Returns:
            True nếu có thể di chuyển đến vị trí đó
        """
        # Kiểm tra ô kề nhau (chỉ đi được 1 ô mỗi lượt)
        # Manhattan distance = |x1 - x2| + |y1 - y2| phải = 1
        if abs(new_x - self.x) + abs(new_y - self.y) != 1:
            return False
        
        # Kiểm tra vị trí mới không phải tường
        return maze.is_valid_position(new_x, new_y)
