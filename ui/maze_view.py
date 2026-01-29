"""
Maze View - Hiển thị mê cung với đồ họa đẹp
"""

import tkinter as tk
from typing import List, Tuple, Optional


class MazeView(tk.Canvas):
    def __init__(self, parent, width: int = 600, height: int = 600):
        """
        Khởi tạo canvas hiển thị mê cung
        
        Args:
            parent: Widget cha
            width, height: Kích thước canvas
        """
        super().__init__(parent, width=width, height=height, bg='#1a1a2e', 
                        highlightthickness=2, highlightbackground='#00ff41', 
                        highlightcolor='#00ff41', takefocus=True)
        
        self.cell_size = 18  # Ô vuông nhỏ chuyên nghiệp (18px)
        self.maze = None
        self.player_pos = None
        self.enemy_pos = None
        self.path = []
        self.visited_cells = set()
        self.current_cell = None
        
        # Cache system cho performance
        self._maze_cached = False
        self._last_maze_id = None
        
        # === SMOOTH RENDERING SYSTEM ===
        self._render_queue = []  # Queue các thao tác render
        self._render_scheduled = False
        self._last_render_time = 0
        self._frame_time = 16  # ~60fps (16ms per frame)
        
        # Animation states cho smooth movement
        self._player_anim = {'x': 0, 'y': 0, 'target_x': 0, 'target_y': 0, 'animating': False}
        self._enemy_anim = {'x': 0, 'y': 0, 'target_x': 0, 'target_y': 0, 'animating': False}
        
        # Double buffering flag
        self._use_double_buffer = True
        
        # Màu sắc theme đẹp
        self.colors = {
            'wall': '#0f3460',
            'path': '#16213e',
            'start': '#00ff41',
            'exit': '#ff0080',
            'player': '#00d4ff',
            'enemy': '#ffb400',
            'solution': '#7b2cbf',
            'visited': '#c9ada7',
            'current': '#f72585',
            'grid': '#1a1a2e'
        }
        
    def set_maze(self, maze):
        """
        Thiết lập mê cung để hiển thị
        
        Args:
            maze: Đối tượng Maze
        """
        self.maze = maze
        # Tính toán kích thước ô phù hợp - ô nhỏ chuyên nghiệp
        self.cell_size = min(
            (self.winfo_width() or 600) // maze.width,
            (self.winfo_height() or 600) // maze.height
        )
        self.cell_size = max(8, min(24, self.cell_size))  # Giới hạn 8-24px - nhỏ gọn
        
    def draw_maze(self):
        """Vẽ mê cung - với optimized batch rendering"""
        if not self.maze:
            return
        
        maze_id = id(self.maze.grid)
        
        # Chỉ vẽ lại nếu maze thay đổi
        if self._maze_cached and self._last_maze_id == maze_id:
            # Maze đã cache, chỉ xóa dynamic elements
            self.delete('dynamic', 'player', 'enemy', 'path', 'visited', 'current')
            return
        
        # Vẽ mê cung mới - batch delete trước
        self.delete('all')
        
        # Tạo lookup table cho colors - giảm function calls
        wall_color = self.colors['wall']
        path_color = self.colors['path']
        
        # Batch create với optimized loop
        cell_size = self.cell_size
        height = self.maze.height
        width = self.maze.width
        grid = self.maze.grid
        
        # Vẽ tất cả walls trước (gộp lại thành ít operations hơn)
        for y in range(height):
            row = grid[y]
            y1 = y * cell_size
            y2 = y1 + cell_size
            
            for x in range(width):
                x1 = x * cell_size
                x2 = x1 + cell_size
                
                color = wall_color if row[x] == 1 else path_color
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline='', width=0, tags='maze')
        
        # Vẽ điểm bắt đầu và kết thúc
        self.draw_special_cell(self.maze.start_pos[0], self.maze.start_pos[1], self.colors['start'], 'S')
        self.draw_special_cell(self.maze.exit_pos[0], self.maze.exit_pos[1], self.colors['exit'], 'E')
        
        self._maze_cached = True
        self._last_maze_id = maze_id
        
    def draw_special_cell(self, x: int, y: int, color: str, text: str = ''):
        """Vẽ ô đặc biệt với màu và chữ"""
        x1 = x * self.cell_size + 2
        y1 = y * self.cell_size + 2
        x2 = (x + 1) * self.cell_size - 2
        y2 = (y + 1) * self.cell_size - 2
        
        # Outer glow
        self.create_oval(x1 - 2, y1 - 2, x2 + 2, y2 + 2, fill='', outline=color, width=1, tags='maze')
        # Main circle
        self.create_oval(x1, y1, x2, y2, fill=color, outline='white', width=2, tags='maze')
        
        if text:
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            font_size = max(10, self.cell_size // 2 + 1)
            self.create_text(cx, cy, text=text, fill='white', font=('Arial', font_size, 'bold'), tags='maze')
    
    def draw_path(self, path: List[Tuple[int, int]], color: str = None):
        """Vẽ đường đi - với smoother rendering"""
        if not path or len(path) < 2:
            return
        
        if not color:
            color = self.colors['solution']
        
        cell_size = self.cell_size
        half_cell = cell_size // 2
        
        # Tạo list points cho smooth line
        points = []
        for x, y in path:
            cx = x * cell_size + half_cell
            cy = y * cell_size + half_cell
            points.extend([cx, cy])
        
        # Vẽ line mượt với smooth=True
        if len(points) >= 4:
            self.create_line(points, fill=color, width=3, 
                           smooth=True, splinesteps=12,
                           capstyle=tk.ROUND, joinstyle=tk.ROUND,
                           tags='path')
            
            # Vẽ arrow ở cuối
            if len(path) >= 2:
                last_x, last_y = path[-1]
                prev_x, prev_y = path[-2]
                
                cx1 = prev_x * cell_size + half_cell
                cy1 = prev_y * cell_size + half_cell
                cx2 = last_x * cell_size + half_cell
                cy2 = last_y * cell_size + half_cell
                
                self.create_line(cx1, cy1, cx2, cy2, fill=color, width=3,
                               arrow=tk.LAST, arrowshape=(10, 12, 5), tags='path')
    
    def draw_visited(self, visited: set):
        """Vẽ các ô đã thăm - với optimized rendering"""
        if not visited:
            return
        
        # Batch rendering - giới hạn số cells vẽ nếu quá nhiều
        cell_size = self.cell_size
        visited_color = self.colors['visited']
        
        # Smart culling - chỉ vẽ những cells trong viewport
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        
        for x, y in visited:
            x1 = x * cell_size + 2
            y1 = y * cell_size + 2
            
            # Skip cells ngoài viewport
            if x1 > canvas_width or y1 > canvas_height:
                continue
            
            x2 = (x + 1) * cell_size - 2
            y2 = (y + 1) * cell_size - 2
            
            self.create_rectangle(x1, y1, x2, y2, fill=visited_color, 
                                outline='', stipple='gray50', tags='visited')
    
    def highlight_current(self, x: int, y: int):
        """Highlight ô hiện tại - nhanh"""
        x1 = x * self.cell_size + 2
        y1 = y * self.cell_size + 2
        x2 = (x + 1) * self.cell_size - 2
        y2 = (y + 1) * self.cell_size - 2
        
        self.create_rectangle(x1, y1, x2, y2, outline=self.colors['current'], 
                            width=2, tags='current')
    
    def draw_player(self, x: int, y: int, animated: bool = True):
        """Vẽ người chơi với smooth animation"""
        target_cx = x * self.cell_size + self.cell_size // 2
        target_cy = y * self.cell_size + self.cell_size // 2
        
        # Smooth animation
        if animated and self._player_anim['animating']:
            cx = self._player_anim['x']
            cy = self._player_anim['y']
        else:
            cx = target_cx
            cy = target_cy
            # Khởi tạo animation state
            if self._player_anim['x'] == 0:
                self._player_anim['x'] = cx
                self._player_anim['y'] = cy
        
        r = self.cell_size // 3
        
        # Outer glow với gradient effect
        self.create_oval(cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3,
                        fill='', outline=self.colors['player'], width=1, 
                        stipple='gray50', tags='player')
        self.create_oval(cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2,
                        fill='', outline=self.colors['player'], width=1, tags='player')
        # Main circle
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                        fill=self.colors['player'], outline='white', width=2, tags='player')
        # Text
        font_size = max(8, self.cell_size // 2)
        self.create_text(cx, cy, text='P', fill='white',
                        font=('Arial', font_size, 'bold'), tags='player')
        
        # Trigger smooth animation nếu vị trí thay đổi
        if animated and (target_cx != self._player_anim.get('target_x', 0) or 
                         target_cy != self._player_anim.get('target_y', 0)):
            self._start_smooth_move('player', target_cx, target_cy)
    
    def draw_enemy(self, x: int, y: int, animated: bool = True):
        """Vẽ kẻ địch với smooth animation"""
        target_cx = x * self.cell_size + self.cell_size // 2
        target_cy = y * self.cell_size + self.cell_size // 2
        
        # Smooth animation
        if animated and self._enemy_anim['animating']:
            cx = self._enemy_anim['x']
            cy = self._enemy_anim['y']
        else:
            cx = target_cx
            cy = target_cy
            if self._enemy_anim['x'] == 0:
                self._enemy_anim['x'] = cx
                self._enemy_anim['y'] = cy
        
        r = self.cell_size // 3
        
        # Outer glow với gradient effect
        self.create_oval(cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3,
                        fill='', outline=self.colors['enemy'], width=1,
                        stipple='gray50', tags='enemy')
        self.create_oval(cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2,
                        fill='', outline=self.colors['enemy'], width=1, tags='enemy')
        # Main circle
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                        fill=self.colors['enemy'], outline='white', width=2, tags='enemy')
        # Text
        font_size = max(8, self.cell_size // 2)
        self.create_text(cx, cy, text='A', fill='white',
                        font=('Arial', font_size, 'bold'), tags='enemy')
        
        # Trigger smooth animation nếu vị trí thay đổi
        if animated and (target_cx != self._enemy_anim.get('target_x', 0) or 
                         target_cy != self._enemy_anim.get('target_y', 0)):
            self._start_smooth_move('enemy', target_cx, target_cy)
    
    def _start_smooth_move(self, entity: str, target_x: float, target_y: float):
        """Bắt đầu smooth movement animation"""
        anim = self._player_anim if entity == 'player' else self._enemy_anim
        
        anim['target_x'] = target_x
        anim['target_y'] = target_y
        
        if not anim['animating']:
            anim['animating'] = True
            self._animate_move(entity)
    
    def _animate_move(self, entity: str):
        """Frame animation cho smooth movement"""
        anim = self._player_anim if entity == 'player' else self._enemy_anim
        
        if not anim['animating']:
            return
        
        # Easing function (ease-out)
        ease = 0.3  # Tốc độ lerp
        
        dx = anim['target_x'] - anim['x']
        dy = anim['target_y'] - anim['y']
        
        # Kiểm tra đã đến đích chưa
        if abs(dx) < 1 and abs(dy) < 1:
            anim['x'] = anim['target_x']
            anim['y'] = anim['target_y']
            anim['animating'] = False
            return
        
        # Lerp position
        anim['x'] += dx * ease
        anim['y'] += dy * ease
        
        # Redraw entity
        self.delete(entity)
        if entity == 'player':
            self._draw_player_at(anim['x'], anim['y'])
        else:
            self._draw_enemy_at(anim['x'], anim['y'])
        
        # Next frame
        self.after(16, lambda: self._animate_move(entity))  # ~60fps
    
    def _draw_player_at(self, cx: float, cy: float):
        """Vẽ player tại tọa độ pixel cụ thể"""
        r = self.cell_size // 3
        self.create_oval(cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3,
                        fill='', outline=self.colors['player'], width=1,
                        stipple='gray50', tags='player')
        self.create_oval(cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2,
                        fill='', outline=self.colors['player'], width=1, tags='player')
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                        fill=self.colors['player'], outline='white', width=2, tags='player')
        font_size = max(8, self.cell_size // 2)
        self.create_text(cx, cy, text='P', fill='white',
                        font=('Arial', font_size, 'bold'), tags='player')
    
    def _draw_enemy_at(self, cx: float, cy: float):
        """Vẽ enemy tại tọa độ pixel cụ thể"""
        r = self.cell_size // 3
        self.create_oval(cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3,
                        fill='', outline=self.colors['enemy'], width=1,
                        stipple='gray50', tags='enemy')
        self.create_oval(cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2,
                        fill='', outline=self.colors['enemy'], width=1, tags='enemy')
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                        fill=self.colors['enemy'], outline='white', width=2, tags='enemy')
        font_size = max(8, self.cell_size // 2)
        self.create_text(cx, cy, text='A', fill='white',
                        font=('Arial', font_size, 'bold'), tags='enemy')
    
    def update_display(self, player_pos=None, enemy_pos=None, path=None, visited=None, current=None):
        """Cập nhật toàn bộ hiển thị - tối ưu hóa triệt để với batched rendering"""
        import time
        
        # Throttle renders to max 60fps
        current_time = time.time() * 1000
        if current_time - self._last_render_time < self._frame_time:
            # Schedule delayed render
            if not self._render_scheduled:
                self._render_scheduled = True
                delay = int(self._frame_time - (current_time - self._last_render_time))
                self.after(max(1, delay), lambda: self._do_render(
                    player_pos, enemy_pos, path, visited, current))
            return
        
        self._do_render(player_pos, enemy_pos, path, visited, current)
    
    def _do_render(self, player_pos=None, enemy_pos=None, path=None, visited=None, current=None):
        """Thực hiện render thực sự"""
        import time
        self._last_render_time = time.time() * 1000
        self._render_scheduled = False
        
        # Vẽ maze nếu cần (chỉ lần đầu hoặc khi thay đổi)
        self.draw_maze()
        
        # Vẽ các elements động
        if visited:
            self.draw_visited(visited)
        
        if path:
            self.draw_path(path)
        
        if current:
            self.highlight_current(current[0], current[1])
        
        if enemy_pos:
            self.draw_enemy(enemy_pos[0], enemy_pos[1])
        
        if player_pos:
            self.draw_player(player_pos[0], player_pos[1])
        
        # Optimized update - chỉ update khi cần thiết
        self.update_idletasks()
    
    def reset_animations(self):
        """Reset tất cả animation states"""
        self._player_anim = {'x': 0, 'y': 0, 'target_x': 0, 'target_y': 0, 'animating': False}
        self._enemy_anim = {'x': 0, 'y': 0, 'target_x': 0, 'target_y': 0, 'animating': False}
        self._render_scheduled = False
    
    def get_cell_from_click(self, event) -> Optional[Tuple[int, int]]:
        """
        Chuyển đổi tọa độ click thành tọa độ ô
        
        Args:
            event: Sự kiện click
            
        Returns:
            Tọa độ ô (x, y) hoặc None
        """
        if not self.maze:
            return None
        
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if 0 <= x < self.maze.width and 0 <= y < self.maze.height:
            return (x, y)
        
        return None
