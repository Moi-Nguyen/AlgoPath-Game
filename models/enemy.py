"""
==============================================================================
MODEL ENEMY - QUẢN LÝ KẺ ĐỊCH AI
==============================================================================

Mô tả:
    Class Enemy đại diện cho kẻ địch trong game mê cung.
    Kẻ địch sử dụng AI (thuật toán BFS) để đuổi theo người chơi.

Tích hợp thuật toán:
    - BFS (Breadth-First Search): Tìm đường ngắn nhất đến người chơi
    - Được gọi mỗi khi kẻ địch cần di chuyển

Đặc điểm AI:
    - Luôn tìm đường ngắn nhất đến người chơi
    - Cập nhật đường đi mỗi lượt (vì người chơi di chuyển)
    - Tốc độ có thể điều chỉnh (số ô di chuyển mỗi lượt)

Điều kiện thua:
    - Khi kẻ địch bắt được người chơi (cùng vị trí)
==============================================================================
"""

from typing import Tuple, Optional


class Enemy:
    """
    Lớp Enemy quản lý kẻ địch AI trong game.
    
    Attributes:
        x, y: Vị trí hiện tại
        initial_x, initial_y: Vị trí ban đầu (để reset)
        speed: Tốc độ di chuyển
        path_history: Lịch sử di chuyển
        current_path: Đường đi hiện tại đến người chơi
        target: Mục tiêu hiện tại
    """
    
    def __init__(self, x: int, y: int, speed: int = 1):
        """
        Khởi tạo kẻ địch tại vị trí ban đầu.
        
        Args:
            x: Tọa độ x ban đầu
            y: Tọa độ y ban đầu
            speed: Tốc độ di chuyển (số ô mỗi lượt, mặc định 1)
        """
        self.x = x
        self.y = y
        # Lưu vị trí ban đầu để reset
        self.initial_x = x
        self.initial_y = y
        self.speed = speed
        # Lịch sử di chuyển - để vẽ đường đi
        self.path_history = [(x, y)]
        # Đường đi tính được từ BFS
        self.current_path = []
        # Mục tiêu hiện tại (vị trí người chơi)
        self.target = None
        
    def move(self, new_x: int, new_y: int):
        """
        Di chuyển kẻ địch đến vị trí mới.
        
        Args:
            new_x: Tọa độ x mới
            new_y: Tọa độ y mới
        """
        self.x = new_x
        self.y = new_y
        self.path_history.append((new_x, new_y))
        
    def get_position(self) -> Tuple[int, int]:
        """
        Lấy vị trí hiện tại của kẻ địch.
        
        Returns:
            Tuple (x, y) - vị trí hiện tại
        """
        return (self.x, self.y)
    
    def set_path(self, path: list):
        """
        Thiết lập đường đi cho AI (từ kết quả BFS).
        
        Đường đi được tính bởi thuật toán BFS, bao gồm
        danh sách các vị trí từ vị trí hiện tại đến người chơi.
        
        Args:
            path: Danh sách các vị trí [(x1,y1), (x2,y2), ...]
        """
        self.current_path = path
        
    def get_next_move(self) -> Optional[Tuple[int, int]]:
        """
        Lấy bước đi tiếp theo từ đường đi đã tính.
        
        Returns:
            Vị trí tiếp theo (x, y) hoặc None nếu không có đường
        """
        if self.current_path and len(self.current_path) > 1:
            # current_path[0] là vị trí hiện tại
            # current_path[1] là vị trí tiếp theo cần đi đến
            return self.current_path[1]
        return None
    
    def update_ai(self, player_pos: Tuple[int, int], pathfinder) -> bool:
        """
        Cập nhật AI và di chuyển về phía người chơi.
        
        Quy trình:
            1. Gọi pathfinder (BFS) để tìm đường đến người chơi
            2. Lấy bước đi tiếp theo
            3. Thực hiện di chuyển
        
        Args:
            player_pos: Vị trí hiện tại của người chơi (x, y)
            pathfinder: Thuật toán tìm đường (BFS)
            
        Returns:
            True nếu di chuyển thành công
        """
        # Gọi BFS để tìm đường ngắn nhất đến người chơi
        next_move = pathfinder.get_next_move(self.get_position(), player_pos)
        
        if next_move:
            # Di chuyển đến vị trí tiếp theo
            self.move(next_move[0], next_move[1])
            return True
        
        return False
    
    def reset(self):
        """
        Reset kẻ địch về vị trí ban đầu.
        
        Được gọi khi bắt đầu game mới.
        """
        self.x = self.initial_x
        self.y = self.initial_y
        self.path_history = [(self.x, self.y)]
        self.current_path = []
        self.target = None
    
    def distance_to(self, x: int, y: int) -> int:
        """
        Tính khoảng cách Manhattan đến một điểm.
        
        Công thức: d = |x1 - x2| + |y1 - y2|
        
        Dùng để:
            - Kiểm tra kẻ địch có bắt được người chơi không
            - Đánh giá mức độ nguy hiểm
        
        Args:
            x: Tọa độ x của điểm
            y: Tọa độ y của điểm
            
        Returns:
            Khoảng cách Manhattan (số nguyên)
        """
        return abs(self.x - x) + abs(self.y - y)
