"""
Main Window - Cửa sổ chính của ứng dụng
Giao diện 3 cột: Cấu hình | Mê cung | Debug
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import json
import os
from datetime import datetime
from .maze_view import MazeView
from .debug_panel import DebugPanel
from .theme_manager import ThemeManager
from models import Maze, Player, Enemy
from models.stats_manager import StatsManager
from algorithms import MazeGenerator, BFS, Dijkstra, AStar

# Import pygame cho âm thanh
try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except:
    SOUND_AVAILABLE = False


class MainWindow:
    def __init__(self, root):
        """
        Khởi tạo cửa sổ chính
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title('🎮 GAME MÔ PHỎNG MÊ CUNG THOÁT HIỂM - AI PATHFINDING')
        self.root.geometry('1400x800')
        self.root.configure(bg='#0f0f0f')
        
        # Dữ liệu
        self.maze = Maze(21, 21)
        self.player = None
        self.enemy = None
        self.current_algorithm = None
        self.algorithm_steps = []
        self.current_step = 0
        self.is_playing = False
        self.game_mode = 'manual'  # 'manual' hoặc 'auto'
        
        # Game balance - AI di chuyển chậm hơn người chơi
        self.player_move_count = 0  # Đếm số bước của người chơi
        self.ai_move_frequency = 3  # AI di chuyển mỗi 3 bước của người chơi (CÂN BẰNG)
        self.move_delay = 30  # Giảm delay xuống 30ms - instant response
        
        # Kết quả so sánh
        self.comparison_results = {}
        
        # New features
        self.theme_manager = ThemeManager()
        self.stats_manager = StatsManager()
        self.game_start_time = None
        self.game_timer_id = None
        self.current_score = 0
        
        # ===== ÂM THANH =====
        self.sound_enabled = True
        self.music_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       'music', 'Super Mario RPG - Forest Maze Extended (15 Minutes).mp3')
        
        self.create_ui()
        
        # Auto play nhạc khi khởi động
        self.init_music()
        
    def create_ui(self):
        """Tạo giao diện"""
        # Main container với 3 cột
        main_container = tk.Frame(self.root, bg='#0f0f0f')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # === CỘT TRÁI: CẤU HÌNH (300px) với Scrollbar ===
        left_panel = tk.Frame(main_container, bg='#16213e', width=300)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Tạo canvas và scrollbar
        self.config_canvas = tk.Canvas(left_panel, bg='#16213e', highlightthickness=0)
        self.config_scrollbar = tk.Scrollbar(left_panel, orient='vertical', command=self.config_canvas.yview)
        self.config_scrollable_frame = tk.Frame(self.config_canvas, bg='#16213e')
        
        # Create window and configure
        self.config_canvas.create_window((0, 0), window=self.config_scrollable_frame, anchor='nw', width=280)
        self.config_canvas.configure(yscrollcommand=self.config_scrollbar.set)
        
        # Pack canvas và scrollbar
        self.config_canvas.pack(side='left', fill='both', expand=True)
        self.config_scrollbar.pack(side='right', fill='y')
        
        # === SMOOTH SCROLLING SYSTEM ===
        self._scroll_velocity = 0
        self._scroll_target = 0
        self._scroll_animating = False
        self._last_scroll_time = 0
        
        def _smooth_scroll_update():
            """Animation frame cho smooth scroll"""
            if not self._scroll_animating:
                return
            
            # Easing với friction
            if abs(self._scroll_velocity) > 0.5:
                # Apply velocity
                self.config_canvas.yview_scroll(int(self._scroll_velocity), "units")
                # Friction/damping
                self._scroll_velocity *= 0.85
                self.root.after(16, _smooth_scroll_update)  # ~60fps
            else:
                self._scroll_velocity = 0
                self._scroll_animating = False
        
        def _on_config_mousewheel(event):
            """Xử lý scroll với momentum"""
            import time
            current_time = time.time()
            
            # Tính delta dựa trên scroll direction
            delta = -1 if event.delta > 0 else 1
            
            # Tích lũy velocity nếu scroll liên tục
            if current_time - self._last_scroll_time < 0.1:
                self._scroll_velocity += delta * 2
                # Giới hạn tốc độ
                self._scroll_velocity = max(-15, min(15, self._scroll_velocity))
            else:
                self._scroll_velocity = delta * 3
            
            self._last_scroll_time = current_time
            
            # Bắt đầu animation nếu chưa chạy
            if not self._scroll_animating:
                self._scroll_animating = True
                _smooth_scroll_update()
        
        # Bind scroll events cho tất cả children
        def _bind_scroll_to_children(widget):
            widget.bind("<MouseWheel>", _on_config_mousewheel)
            for child in widget.winfo_children():
                _bind_scroll_to_children(child)
        
        self.config_canvas.bind("<MouseWheel>", _on_config_mousewheel)
        self.config_scrollable_frame.bind("<MouseWheel>", _on_config_mousewheel)
        
        # Bind sau khi tạo UI
        self.root.after(200, lambda: _bind_scroll_to_children(self.config_scrollable_frame))
        
        # Tạo config panel
        self.create_config_panel(self.config_scrollable_frame)
        
        # Update scroll region after widgets are created
        self.root.after(100, lambda: self.config_canvas.configure(scrollregion=self.config_canvas.bbox("all")))
        
        # === CỘT GIỮA: MÊ CUNG (700px) ===
        center_panel = tk.Frame(main_container, bg='#1a1a2e')
        center_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.create_maze_panel(center_panel)
        
        # === CỘT PHẢI: DEBUG (300px) ===
        right_panel = tk.Frame(main_container, bg='#16213e', width=300)
        right_panel.pack(side='left', fill='y')
        right_panel.pack_propagate(False)
        
        self.debug_panel = DebugPanel(right_panel)
        self.debug_panel.pack(fill='both', expand=True)
        
    def create_config_panel(self, parent):
        """Tạo panel cấu hình bên trái với enhanced UI"""
        theme = self.theme_manager.get_theme()
        
        # === STYLED HEADER ===
        header_frame = tk.Frame(parent, bg=theme.get('card_header', '#243050'))
        header_frame.pack(fill='x', padx=5, pady=(10, 5))
        
        # Header border top
        tk.Frame(header_frame, height=3, bg=theme.get('accent', '#00ff41')).pack(fill='x')
        
        # Header content
        header_content = tk.Frame(header_frame, bg=theme.get('card_header', '#243050'))
        header_content.pack(fill='x', padx=10, pady=10)
        
        # Icon + Title
        title = tk.Label(header_content, text='⚙️ CẤU HÌNH', 
                        bg=theme.get('card_header', '#243050'), 
                        fg=theme.get('accent', '#00ff41'), 
                        font=('Arial', 16, 'bold'))
        title.pack()
        
        # Subtitle
        subtitle = tk.Label(header_content, text='Thiết lập trò chơi', 
                           bg=theme.get('card_header', '#243050'), 
                           fg=theme.get('text_dim', '#c9ada7'), 
                           font=('Arial', 9))
        subtitle.pack()
        
        # Header border bottom
        tk.Frame(header_frame, height=1, bg=theme.get('border', '#2a3a5e')).pack(fill='x')
        
        # === PHẦN 1: CẤU HÌNH MÊ CUNG ===
        self._create_section(parent, '🏗️ Tạo mê cung')
        
        # Kích thước
        size_frame = tk.Frame(parent, bg='#16213e')
        size_frame.pack(fill='x', padx=15, pady=5)
        
        tk.Label(size_frame, text='Kích thước:', bg='#16213e', fg='#ffffff', 
                font=('Arial', 10)).pack(anchor='w')
        
        self.size_var = tk.StringVar(value='21x21')
        size_combo = ttk.Combobox(size_frame, textvariable=self.size_var, 
                                  values=['11x11', '15x15', '21x21', '25x25', '31x31', 'Tùy chỉnh'], 
                                  state='readonly', width=10, takefocus=False)
        size_combo.pack(anchor='w', pady=2)
        size_combo.bind('<<ComboboxSelected>>', self.on_size_change)
        
        # Custom size frame (ẩn mặc định)
        self.custom_size_frame = tk.Frame(parent, bg='#16213e')
        self.custom_size_frame.pack(fill='x', padx=15, pady=5)
        self.custom_size_frame.pack_forget()  # Ẩn ban đầu
        
        tk.Label(self.custom_size_frame, text='📐 Custom size (max 50x50):', 
                bg='#16213e', fg='#00ff41', font=('Arial', 8, 'bold')).pack(anchor='w')
        
        custom_input_frame = tk.Frame(self.custom_size_frame, bg='#16213e')
        custom_input_frame.pack(fill='x', pady=3)
        
        # Width
        tk.Label(custom_input_frame, text='Rộng:', bg='#16213e', fg='#ffffff',
                font=('Arial', 8)).grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.custom_width = tk.Entry(custom_input_frame, width=5, font=('Arial', 9),
                                     bg='#0f3460', fg='#ffffff', insertbackground='#00ff41')
        self.custom_width.grid(row=0, column=1, padx=(0, 10))
        self.custom_width.insert(0, '21')
        
        # Height
        tk.Label(custom_input_frame, text='Cao:', bg='#16213e', fg='#ffffff',
                font=('Arial', 8)).grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.custom_height = tk.Entry(custom_input_frame, width=5, font=('Arial', 9),
                                      bg='#0f3460', fg='#ffffff', insertbackground='#00ff41')
        self.custom_height.grid(row=0, column=3)
        self.custom_height.insert(0, '21')
        
        # Nút tạo mê cung
        btn_generate = tk.Button(parent, text='🎲 Tạo mê cung mới', bg='#7b2cbf', fg='#ffffff', 
                                font=('Arial', 11, 'bold'), relief='flat', cursor='hand2',
                                command=self.generate_maze)
        btn_generate.pack(fill='x', padx=15, pady=10)
        
        # === PHẦN 2: THUẬT TOÁN TÌM ĐƯỜNG ===
        self._create_section(parent, '🧭 Thuật toán tìm đường')
        
        algo_frame = tk.Frame(parent, bg='#16213e')
        algo_frame.pack(fill='x', padx=15, pady=5)
        
        self.algo_var = tk.StringVar(value='Dijkstra')
        
        algorithms = [
            ('BFS', 'BFS'),
            ('Dijkstra', 'Dijkstra'),
            ('A*', 'A*')
        ]
        
        for text, value in algorithms:
            rb = tk.Radiobutton(algo_frame, text=text, variable=self.algo_var, value=value,
                               bg='#16213e', fg='#ffffff', selectcolor='#0f3460',
                               font=('Arial', 10), activebackground='#16213e', 
                               activeforeground='#00ff41', cursor='hand2')
            rb.pack(anchor='w', pady=2)
        
        # Nút tìm đường
        btn_find = tk.Button(parent, text='🔍 Tìm đường thoát', bg='#00d4ff', fg='#000000', 
                            font=('Arial', 11, 'bold'), relief='flat', cursor='hand2',
                            command=self.find_path)
        btn_find.pack(fill='x', padx=15, pady=10)
        
        # === PHẦN 3: ĐIỀU KHIỂN DEBUG ===
        self._create_section(parent, '🎬 Điều khiển Debug')
        
        control_frame = tk.Frame(parent, bg='#16213e')
        control_frame.pack(fill='x', padx=15, pady=5)
        
        # Play/Pause/Stop buttons
        btn_row1 = tk.Frame(control_frame, bg='#16213e')
        btn_row1.pack(fill='x', pady=2)
        
        self.btn_play = tk.Button(btn_row1, text='▶️ Play', bg='#00ff41', fg='#000000',
                                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2',
                                 command=self.play_animation, width=8)
        self.btn_play.pack(side='left', padx=2)
        
        self.btn_pause = tk.Button(btn_row1, text='⏸️ Pause', bg='#ffb400', fg='#000000',
                                   font=('Arial', 9, 'bold'), relief='flat', cursor='hand2',
                                   command=self.pause_animation, width=8, state='disabled')
        self.btn_pause.pack(side='left', padx=2)
        
        self.btn_stop = tk.Button(btn_row1, text='⏹️ Stop', bg='#ff0080', fg='#ffffff',
                                 font=('Arial', 9, 'bold'), relief='flat', cursor='hand2',
                                 command=self.stop_animation, width=8)
        self.btn_stop.pack(side='left', padx=2)
        
        # Step buttons
        btn_row2 = tk.Frame(control_frame, bg='#16213e')
        btn_row2.pack(fill='x', pady=2)
        
        tk.Button(btn_row2, text='⏮️ First', bg='#0f3460', fg='#ffffff',
                 font=('Arial', 8), relief='flat', cursor='hand2',
                 command=self.first_step, width=8).pack(side='left', padx=2)
        
        tk.Button(btn_row2, text='◀️ Prev', bg='#0f3460', fg='#ffffff',
                 font=('Arial', 8), relief='flat', cursor='hand2',
                 command=self.prev_step, width=8).pack(side='left', padx=2)
        
        tk.Button(btn_row2, text='Next ▶️', bg='#0f3460', fg='#ffffff',
                 font=('Arial', 8), relief='flat', cursor='hand2',
                 command=self.next_step, width=8).pack(side='left', padx=2)
        
        # Speed control - Cực nhanh
        speed_frame = tk.Frame(control_frame, bg='#16213e')
        speed_frame.pack(fill='x', pady=5)
        
        tk.Label(speed_frame, text='Tốc độ:', bg='#16213e', fg='#ffffff',
                font=('Arial', 9)).pack(anchor='w')
        
        self.speed_var = tk.IntVar(value=100)  # Giảm default về 100ms - cực nhanh
        speed_slider = tk.Scale(speed_frame, from_=20, to=500, orient='horizontal',
                               variable=self.speed_var, bg='#16213e', fg='#ffffff',
                               troughcolor='#0f3460', highlightthickness=0,
                               font=('Arial', 8), resolution=20)  # Step 20ms
        speed_slider.pack(fill='x')
        
        # === PHẦN 4: GAME MODE ===
        self._create_section(parent, '🎮 Chế độ chơi')
        
        # Độ khó
        difficulty_frame = tk.Frame(parent, bg='#16213e')
        difficulty_frame.pack(fill='x', padx=15, pady=5)
        
        tk.Label(difficulty_frame, text='Độ khó:', bg='#16213e', fg='#ffffff',
                font=('Arial', 10)).pack(anchor='w')
        
        self.difficulty_var = tk.StringVar(value='Dễ')
        self.difficulty_combo = ttk.Combobox(difficulty_frame, textvariable=self.difficulty_var,
                                            values=['Rất dễ', 'Dễ', 'Trung bình', 'Khó'], 
                                            state='readonly', width=12, takefocus=False)
        self.difficulty_combo.pack(anchor='w', pady=2)
        self.difficulty_combo.bind('<<ComboboxSelected>>', self.on_difficulty_change)
        
        # Timer & Score
        timer_frame = tk.Frame(parent, bg='#0f3460', relief='solid', bd=1)
        timer_frame.pack(fill='x', padx=15, pady=5)
        
        self.timer_label = tk.Label(timer_frame, text='⏱️ Thời gian: 00:00', 
                                    bg='#0f3460', fg='#00ff41', font=('Arial', 10, 'bold'))
        self.timer_label.pack(pady=3)
        
        self.score_label = tk.Label(timer_frame, text='🏆 Score: 0',
                                    bg='#0f3460', fg='#ffb400', font=('Arial', 10, 'bold'))
        self.score_label.pack(pady=3)
        
        # Nút Start Game
        btn_start = tk.Button(parent, text='🚀 BẮT ĐẦU TRÒ CHƠI', bg='#f72585', fg='#ffffff',
                             font=('Arial', 12, 'bold'), relief='raised', cursor='hand2',
                             command=self.start_game, bd=2, activebackground='#ff0080')
        btn_start.pack(fill='x', padx=15, pady=10)
        
        # Nút Reset
        btn_reset = tk.Button(parent, text='🔄 Reset trò chơi', bg='#0f3460', fg='#ffffff',
                             font=('Arial', 11, 'bold'), relief='raised', cursor='hand2',
                             command=self.reset_game, bd=2)
        btn_reset.pack(fill='x', padx=15, pady=8)
        
        # === PHẦN 5: SO SÁNH THUẬT TOÁN ===
        self._create_section(parent, '📊 So sánh')
        
        btn_compare = tk.Button(parent, text='📈 So sánh tất cả thuật toán', bg='#7b2cbf', 
                               fg='#ffffff', font=('Arial', 10, 'bold'), relief='flat', 
                               cursor='hand2', command=self.compare_algorithms)
        btn_compare.pack(fill='x', padx=15, pady=10)
        
        # === PHẦN 6: THEME & SAVE/LOAD ===
        self._create_section(parent, '🎨 Nâng cao')
        
        # Theme selector
        theme_frame = tk.Frame(parent, bg='#16213e')
        theme_frame.pack(fill='x', padx=15, pady=5)
        
        tk.Label(theme_frame, text='Theme:', bg='#16213e', fg='#ffffff',
                font=('Arial', 10)).pack(anchor='w')
        
        self.theme_var = tk.StringVar(value='Dark')
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                   values=self.theme_manager.get_theme_names(),
                                   state='readonly', width=12, takefocus=False)
        theme_combo.pack(anchor='w', pady=2)
        theme_combo.bind('<<ComboboxSelected>>', self.on_theme_change)
        
        # Save/Load buttons
        save_load_frame = tk.Frame(parent, bg='#16213e')
        save_load_frame.pack(fill='x', padx=15, pady=5)
        
        btn_save = tk.Button(save_load_frame, text='💾 Save', bg='#00d4ff', fg='#000000',
                            font=('Arial', 9, 'bold'), cursor='hand2', command=self.save_game)
        btn_save.pack(side='left', expand=True, fill='x', padx=(0, 5))
        
        btn_load = tk.Button(save_load_frame, text='📂 Load', bg='#00d4ff', fg='#000000',
                            font=('Arial', 9, 'bold'), cursor='hand2', command=self.load_game)
        btn_load.pack(side='left', expand=True, fill='x')
        
        # === PHẦN 7: THỐNG KÊ ===
        self._create_section(parent, '📊 Thống kê')
        
        stats_frame = tk.Frame(parent, bg='#0f3460', relief='solid', bd=1)
        stats_frame.pack(fill='x', padx=15, pady=5)
        
        stats = self.stats_manager.get_summary()
        
        self.stats_labels = {}
        stats_info = [
            ('🎮 Tổng trận:', f"{stats['total']}"),
            ('✅ Thắng:', f"{stats['wins']}"),
            ('❌ Thua:', f"{stats['losses']}"),
            ('📈 Win rate:', f"{stats['win_rate']:.1f}%"),
            ('⏱️ Best time:', f"{stats['best_time']:.1f}s" if stats['best_time'] else 'N/A'),
            ('🏆 Best score:', f"{stats['best_score']}")
        ]
        
        for label_text, value_text in stats_info:
            row = tk.Frame(stats_frame, bg='#0f3460')
            row.pack(fill='x', padx=5, pady=2)
            
            tk.Label(row, text=label_text, bg='#0f3460', fg='#c9ada7',
                    font=('Arial', 9), width=12, anchor='w').pack(side='left')
            
            val_label = tk.Label(row, text=value_text, bg='#0f3460', fg='#00ff41',
                                font=('Arial', 9, 'bold'), anchor='w')
            val_label.pack(side='left')
            self.stats_labels[label_text] = val_label
        
        # Thêm padding cuối để có thể scroll hết
        tk.Label(parent, text='', bg='#16213e', height=3).pack()
        
    def create_maze_panel(self, parent):
        """Tạo panel hiển thị mê cung ở giữa với enhanced UI"""
        theme = self.theme_manager.get_theme()
        
        # === STYLED HEADER ===
        header_frame = tk.Frame(parent, bg=theme.get('card_header', '#243050'))
        header_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        # Top border gradient effect
        border_frame = tk.Frame(header_frame, bg=theme.get('bg', '#1a1a2e'))
        border_frame.pack(fill='x')
        
        # Gradient lines
        tk.Frame(border_frame, height=1, bg=theme.get('separator_dim', '#0a5a1a')).pack(fill='x')
        tk.Frame(border_frame, height=2, bg=theme.get('separator', '#00ff41')).pack(fill='x')
        tk.Frame(border_frame, height=1, bg=theme.get('separator_dim', '#0a5a1a')).pack(fill='x')
        
        # Header content
        header_content = tk.Frame(header_frame, bg=theme.get('card_header', '#243050'))
        header_content.pack(fill='x', pady=10)
        
        # Title row với nút âm thanh
        title_row = tk.Frame(header_content, bg=theme.get('card_header', '#243050'))
        title_row.pack(fill='x', padx=20)
        
        # Spacer trái để căn giữa
        tk.Frame(title_row, bg=theme.get('card_header', '#243050'), width=50).pack(side='left')
        
        title = tk.Label(title_row, text='🗺️ MÊ CUNG', 
                        bg=theme.get('card_header', '#243050'), 
                        fg=theme.get('accent', '#00ff41'),
                        font=('Arial', 18, 'bold'))
        title.pack(side='left', expand=True)
        
        # ===== NÚT ÂM THANH =====
        self.sound_btn = tk.Button(title_row, text='🔊', 
                                   bg=theme.get('button', '#7b2cbf'),
                                   fg='#ffffff',
                                   font=('Arial', 14),
                                   relief='flat',
                                   cursor='hand2',
                                   width=3,
                                   command=self.toggle_sound)
        self.sound_btn.pack(side='right', padx=5)
        
        # Tooltip cho nút âm thanh
        self._create_tooltip(self.sound_btn, "Bật/Tắt nhạc nền (đang bật)")
        
        # Status bar với styled container
        status_container = tk.Frame(header_content, bg=theme.get('section_bg', '#141a30'), 
                                   relief='flat', bd=0)
        status_container.pack(fill='x', padx=20, pady=(8, 0))
        
        # Status inner padding
        status_inner = tk.Frame(status_container, bg=theme.get('section_bg', '#141a30'))
        status_inner.pack(fill='x', padx=10, pady=5)
        
        self.status_label = tk.Label(status_inner, text='Chưa có mê cung. Nhấn "Tạo mê cung mới"',
                                    bg=theme.get('section_bg', '#141a30'), 
                                    fg=theme.get('text_dim', '#c9ada7'), 
                                    font=('Arial', 10))
        self.status_label.pack()
        
        # Bottom border
        tk.Frame(header_frame, height=1, bg=theme.get('border', '#2a3a5e')).pack(fill='x')
        
        # === MAZE CANVAS ===
        # Sử dụng canvas container với kích thước cố định để legend không bị đè
        canvas_container = tk.Frame(parent, bg=theme.get('bg', '#1a1a2e'))
        canvas_container.pack(fill='both', expand=True, padx=10, pady=(10, 5))
        
        # Canvas border frame - center maze
        canvas_border = tk.Frame(canvas_container, bg=theme.get('border_accent', '#00ff41'), bd=0)
        canvas_border.pack(expand=False)  # Không expand để không chiếm hết không gian
        
        # Inner canvas frame
        canvas_inner = tk.Frame(canvas_border, bg=theme.get('bg', '#1a1a2e'), bd=2)
        canvas_inner.pack(padx=2, pady=2)
        
        # Giảm kích thước canvas để có chỗ cho legend
        self.maze_view = MazeView(canvas_inner, width=650, height=500)
        self.maze_view.pack(expand=True)
        
        # Bind click event
        self.maze_view.bind('<Button-1>', self.on_maze_click)
        
        # === STYLED LEGEND ===
        legend_container = tk.Frame(parent, bg=theme.get('bg', '#1a1a2e'))
        legend_container.pack(fill='x', padx=10, pady=(0, 10))
        
        # Legend card
        legend_frame = tk.Frame(legend_container, bg=theme.get('card_bg', '#1e2848'))
        legend_frame.pack(fill='x')
        
        # Top accent
        tk.Frame(legend_frame, height=2, bg=theme.get('accent2', '#00d4ff')).pack(fill='x')
        
        # Legend content
        legend_content = tk.Frame(legend_frame, bg=theme.get('card_bg', '#1e2848'))
        legend_content.pack(fill='x', padx=15, pady=8)
        
        # Row 1: Chú thích
        row1 = tk.Frame(legend_content, bg=theme.get('card_bg', '#1e2848'))
        row1.pack(fill='x')
        
        tk.Label(row1, text='🎯', bg=theme.get('card_bg', '#1e2848'), 
                font=('Arial', 11)).pack(side='left')
        tk.Label(row1, text=' Chú thích: ', bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('text', '#ffffff'), font=('Arial', 10, 'bold')).pack(side='left')
        
        # Color indicators
        for color, label in [('#00ff41', 'Start'), ('#ff0080', 'Exit'), 
                             ('#00d4ff', 'Player'), ('#ffb400', 'Enemy')]:
            tk.Frame(row1, width=12, height=12, bg=color).pack(side='left', padx=(8, 2))
            tk.Label(row1, text=label, bg=theme.get('card_bg', '#1e2848'), 
                    fg=theme.get('text_dim', '#c9ada7'), font=('Arial', 9)).pack(side='left')
        
        # Divider
        tk.Frame(legend_content, height=1, bg=theme.get('border', '#2a3a5e')).pack(fill='x', pady=6)
        
        # Row 2: Điều khiển
        row2 = tk.Frame(legend_content, bg=theme.get('card_bg', '#1e2848'))
        row2.pack(fill='x')
        
        tk.Label(row2, text='⌨️', bg=theme.get('card_bg', '#1e2848'), 
                font=('Arial', 11)).pack(side='left')
        tk.Label(row2, text=' Điều khiển: ', bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('text', '#ffffff'), font=('Arial', 10, 'bold')).pack(side='left')
        
        # Key indicators
        for key in ['←', '↑', '→', '↓']:
            key_frame = tk.Frame(row2, bg=theme.get('panel_dark', '#0f3460'), bd=1, relief='raised')
            key_frame.pack(side='left', padx=2)
            tk.Label(key_frame, text=key, bg=theme.get('panel_dark', '#0f3460'), 
                    fg=theme.get('accent', '#00ff41'), font=('Arial', 10, 'bold'),
                    padx=4, pady=1).pack()
        
        tk.Label(row2, text='  | Chọn độ khó phù hợp!', bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('text_muted', '#8a8a9a'), font=('Arial', 9)).pack(side='left')
        
        # Bottom border
        tk.Frame(legend_frame, height=1, bg=theme.get('border', '#2a3a5e')).pack(fill='x')
        
    def _create_section(self, parent, title):
        """Tạo tiêu đề section với styled separator"""
        theme = self.theme_manager.get_theme()
        
        # Container cho section header
        section_container = tk.Frame(parent, bg=theme.get('panel', '#16213e'))
        section_container.pack(fill='x', padx=10, pady=(15, 5))
        
        # === STYLED SEPARATOR ===
        # Top line (dim)
        top_line = tk.Frame(section_container, height=1, bg=theme.get('separator_dim', '#0a5a1a'))
        top_line.pack(fill='x', pady=(0, 2))
        
        # Main separator with gradient effect (using 3 lines)
        sep_frame = tk.Frame(section_container, bg=theme.get('panel', '#16213e'))
        sep_frame.pack(fill='x')
        
        # Left decorative element
        left_cap = tk.Frame(sep_frame, width=8, height=3, bg=theme.get('accent', '#00ff41'))
        left_cap.pack(side='left')
        
        # Center line
        center_line = tk.Frame(sep_frame, height=2, bg=theme.get('separator', '#00ff41'))
        center_line.pack(side='left', fill='x', expand=True, padx=2)
        
        # Right decorative element
        right_cap = tk.Frame(sep_frame, width=8, height=3, bg=theme.get('accent', '#00ff41'))
        right_cap.pack(side='right')
        
        # Bottom line (dim)
        bottom_line = tk.Frame(section_container, height=1, bg=theme.get('separator_dim', '#0a5a1a'))
        bottom_line.pack(fill='x', pady=(2, 0))
        
        # Section title with icon styling
        title_frame = tk.Frame(section_container, bg=theme.get('panel', '#16213e'))
        title_frame.pack(fill='x', pady=(8, 3))
        
        # Left accent bar
        accent_bar = tk.Frame(title_frame, width=4, bg=theme.get('accent2', '#00d4ff'))
        accent_bar.pack(side='left', fill='y', padx=(0, 8))
        
        label = tk.Label(title_frame, text=title, bg=theme.get('panel', '#16213e'), 
                        fg=theme.get('accent2', '#00d4ff'),
                        font=('Arial', 11, 'bold'))
        label.pack(side='left')
    
    def on_difficulty_change(self, event=None):
        """Xử lý thay đổi độ khó"""
        difficulty = self.difficulty_var.get()
        
        # Tối ưu hóa tốc độ AI theo độ khó
        if difficulty == 'Rất dễ':
            self.ai_move_frequency = 5  # AI di chuyển mỗi 5 bước - rất chậm
        elif difficulty == 'Dễ':
            self.ai_move_frequency = 3  # AI di chuyển mỗi 3 bước (mặc định)
        elif difficulty == 'Trung bình':
            self.ai_move_frequency = 2  # AI di chuyển mỗi 2 bước - nhanh hơn
        else:  # Khó
            self.ai_move_frequency = 1  # AI di chuyển mỗi bước - rất nhanh
    
    def on_size_change(self, event=None):
        """Xử lý khi thay đổi size"""
        if self.size_var.get() == 'Tùy chỉnh':
            self.custom_size_frame.pack(fill='x', padx=15, pady=5, after=self.custom_size_frame.master.winfo_children()[2])
        else:
            self.custom_size_frame.pack_forget()
    
    def generate_maze(self):
        """Tạo mê cung mới - phản hồi ngay lập tức"""
        # Lấy kích thước
        size_str = self.size_var.get()
        
        if size_str == 'Tùy chỉnh':
            # Validate custom input
            try:
                width = int(self.custom_width.get())
                height = int(self.custom_height.get())
                
                # Kiểm tra giới hạn
                if width < 5 or height < 5:
                    messagebox.showerror('Lỗi', 'Kích thước tối thiểu là 5x5!')
                    return
                if width > 50 or height > 50:
                    messagebox.showerror('Lỗi', 'Kích thước tối đa là 50x50!')
                    return
                if width % 2 == 0 or height % 2 == 0:
                    messagebox.showerror('Lỗi', 'Kích thước phải là số lẻ!\n(Ví dụ: 21x21, 25x31)')
                    return
            except ValueError:
                messagebox.showerror('Lỗi', 'Vui lòng nhập số hợp lệ!')
                return
        else:
            width = height = int(size_str.split('x')[0])
        
        # Update status NGAY LẬP TỨC
        self.status_label.config(text='⏳ Đang tạo...')
        self.root.update_idletasks()
        
        # Generate in background thread - cực nhanh
        import threading
        
        def _generate_thread():
            generator = MazeGenerator(width, height)
            grid, steps = generator.generate()
            
            def _update_ui():
                self.maze = Maze(width, height)
                self.maze.set_grid(grid)
                self.maze.set_start(1, 1)
                self.maze.set_exit(width - 2, height - 2)
                
                self.maze_view.set_maze(self.maze)
                self.maze_view._maze_cached = False  # Force redraw
                self.maze_view.update_display()
                
                self.player = None
                self.enemy = None
                
                self.debug_panel.show_algorithm_info(generator.get_complexity_info())
                self.status_label.config(text=f'✅ {width}x{height}')
            
            self.root.after(0, _update_ui)
        
        thread = threading.Thread(target=_generate_thread, daemon=True)
        thread.start()
        
    def find_path(self):
        """Tìm đường đi"""
        if not self.maze:
            messagebox.showwarning('Cảnh báo', 'Vui lòng tạo mê cung trước!')
            return
        
        algo_name = self.algo_var.get()
        self.status_label.config(text=f'Đang chạy {algo_name}...')
        self.root.update()
        
        # Tạo thuật toán
        start_time = time.time()
        
        if algo_name == 'BFS':
            algo = BFS(self.maze.grid)
        elif algo_name == 'Dijkstra':
            algo = Dijkstra(self.maze.grid)
        else:  # A*
            algo = AStar(self.maze.grid)
        
        # Tìm đường
        if algo_name == 'BFS':
            path, steps = algo.find_path(self.maze.start_pos, self.maze.exit_pos)
            tables = {}
        else:
            path, steps, tables = algo.find_path(self.maze.start_pos, self.maze.exit_pos)
        
        end_time = time.time()
        
        # Lưu kết quả
        self.current_algorithm = algo
        self.algorithm_steps = steps
        self.current_step = 0
        
        if path:
            # Hiển thị kết quả
            result = {
                'path_length': len(path),
                'steps': len(steps),
                'time': end_time - start_time,
                'visited_count': len(steps[-1].get('visited', set())) if steps else 0
            }
            
            self.debug_panel.show_result(result)
            
            # Hiển thị đường đi
            self.maze_view.update_display(path=path, visited=steps[-1].get('visited', set()) if steps else None)
            
            self.status_label.config(text=f'✅ Tìm thấy đường đi! Độ dài: {len(path)} ô')
        else:
            messagebox.showinfo('Thông báo', 'Không tìm thấy đường đi!')
            self.status_label.config(text='❌ Không tìm thấy đường đi')
    
    def play_animation(self):
        """Chạy animation từng bước"""
        if not self.algorithm_steps:
            messagebox.showwarning('Cảnh báo', 'Vui lòng chạy thuật toán trước!')
            return
        
        self.is_playing = True
        self.btn_play.config(state='disabled')
        self.btn_pause.config(state='normal')
        
        self._animate_step()
    
    def _animate_step(self):
        """Animate một bước - với smoother transitions"""
        if not self.is_playing or self.current_step >= len(self.algorithm_steps):
            self.is_playing = False
            self.btn_play.config(state='normal')
            self.btn_pause.config(state='disabled')
            return
        
        # Hiển thị bước hiện tại
        step = self.algorithm_steps[self.current_step]
        
        visited = step.get('visited', set())
        current = step.get('current')
        path = step.get('path', [])
        
        # Batched update - giảm số lần redraw
        self.maze_view.update_display(visited=visited, current=current, path=path)
        self.debug_panel.show_step_info(step, self.current_step + 1, len(self.algorithm_steps))
        
        self.current_step += 1
        
        # Tiếp tục animation với dynamic delay
        if self.is_playing:
            # Invert slider và thêm minimum delay
            delay = max(16, 2100 - self.speed_var.get())  # Minimum 16ms (~60fps)
            self.root.after(delay, self._animate_step)
    
    def pause_animation(self):
        """Tạm dừng animation"""
        self.is_playing = False
        self.btn_play.config(state='normal')
        self.btn_pause.config(state='disabled')
    
    def stop_animation(self):
        """Dừng animation"""
        self.is_playing = False
        self.current_step = 0
        self.btn_play.config(state='normal')
        self.btn_pause.config(state='disabled')
        
        if self.algorithm_steps:
            self.maze_view.update_display()
    
    def first_step(self):
        """Về bước đầu tiên"""
        if not self.algorithm_steps:
            return
        self.current_step = 0
        self._show_current_step()
    
    def prev_step(self):
        """Bước trước"""
        if not self.algorithm_steps or self.current_step == 0:
            return
        self.current_step -= 1
        self._show_current_step()
    
    def next_step(self):
        """Bước tiếp theo"""
        if not self.algorithm_steps or self.current_step >= len(self.algorithm_steps) - 1:
            return
        self.current_step += 1
        self._show_current_step()
    
    def _show_current_step(self):
        """Hiển thị bước hiện tại"""
        if not self.algorithm_steps:
            return
        
        step = self.algorithm_steps[self.current_step]
        visited = step.get('visited', set())
        current = step.get('current')
        path = step.get('path', [])
        
        self.maze_view.update_display(visited=visited, current=current, path=path)
        self.debug_panel.show_step_info(step, self.current_step + 1, len(self.algorithm_steps))
    
    def start_game(self):
        """Bắt đầu trò chơi"""
        if not self.maze:
            messagebox.showwarning('Cảnh báo', 'Vui lòng tạo mê cung trước!')
            return
        
        # Tạo player và enemy
        self.player = Player(self.maze.start_pos[0], self.maze.start_pos[1])
        
        # Reset đếm bước
        self.player_move_count = 0
        
        # Start timer and reset score
        self.start_timer()
        self.current_score = 0
        self.update_score_display(0)
        
        # Enemy ở VỊ TRÍ XA HƠN NỮA (góc đối diện hoàn toàn)
        # Player ở (1,1) góc trái-trên
        # Exit ở (width-2, height-2) góc phải-dưới
        # Enemy ở góc phải-trên (xa cả player và exit)
        enemy_x = self.maze.width - 3
        enemy_y = 2
        self.enemy = Enemy(enemy_x, enemy_y)
        
        # Bind keyboard - PREVENT combobox from stealing focus
        self.root.bind('<Up>', lambda e: self._handle_arrow_key(0, -1))
        self.root.bind('<Down>', lambda e: self._handle_arrow_key(0, 1))
        self.root.bind('<Left>', lambda e: self._handle_arrow_key(-1, 0))
        self.root.bind('<Right>', lambda e: self._handle_arrow_key(1, 0))
        self.root.bind('<space>', lambda e: self.move_enemy())
        
        # Hiển thị
        self.maze_view.update_display(
            player_pos=self.player.get_position(),
            enemy_pos=self.enemy.get_position()
        )
        
        # SET FOCUS VÀO CANVAS ĐỂ NHẬN PHÍM - FIX LỖI PHÍM MŨI TÊN
        self.maze_view.focus_set()
        
        difficulty = self.difficulty_var.get()
        self.status_label.config(text=f'🎮 Trò chơi bắt đầu! Độ khó: {difficulty} | AI đuổi mỗi {self.ai_move_frequency} bước')
    
    def _handle_arrow_key(self, dx, dy):
        """Xử lý phím mũi tên - đảm bảo focus vào game"""
        if self.player:
            # Set focus về canvas để tránh combobox nhận phím
            self.maze_view.focus_set()
            # Di chuyển player
            self.move_player(dx, dy)
        
    def move_player(self, dx, dy):
        """Di chuyển người chơi - với smooth response"""
        if not self.player:
            return
        
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        
        if self.player.can_move_to(self.maze, new_x, new_y):
            self.player.move(new_x, new_y)
            
            # Kiểm tra thắng - immediate response
            if (new_x, new_y) == self.maze.exit_pos:
                elapsed_time = self.stop_timer()
                score = self.calculate_score(elapsed_time, self.player.moves, True)
                self.update_score_display(score)
                
                # Record stats
                self.stats_manager.record_game(
                    won=True,
                    time_seconds=elapsed_time,
                    steps=self.player.moves,
                    difficulty=self.difficulty_var.get(),
                    score=score
                )
                self.update_stats_display()
                
                # Show celebration
                self.show_celebration()
                self.maze_view.update_display(player_pos=self.player.get_position())
                
                messagebox.showinfo('Chúc mừng! 🎉', 
                    f'Bạn đã thoát khỏi mê cung!\nSố bước: {self.player.moves}\n⏱️ Thời gian: {elapsed_time:.1f}s\n🏆 Score: {score}')
                self.reset_game()
                return
            
            # Kiểm tra va chạm enemy
            if self.enemy and (new_x, new_y) == self.enemy.get_position():
                elapsed_time = self.stop_timer()
                
                # Record stats
                self.stats_manager.record_game(
                    won=False,
                    time_seconds=elapsed_time,
                    steps=self.player.moves,
                    difficulty=self.difficulty_var.get(),
                    score=0
                )
                self.update_stats_display()
                
                messagebox.showinfo('Game Over! 💀', 'Bạn đã bị AI bắt!')
                self.reset_game()
                return
            
            # Cập nhật hiển thị - smooth update
            self.maze_view.update_display(
                player_pos=self.player.get_position(),
                enemy_pos=self.enemy.get_position() if self.enemy else None,
                path=self.player.path_history
            )
            
            # Tăng đếm bước
            self.player_move_count += 1
            
            # AI DI CHUYỂN MỖI N BƯỚC CỦA NGƯỜI CHƠI (cân bằng game)
            if self.player_move_count % self.ai_move_frequency == 0:
                # Schedule AI move với smooth delay
                self.root.after(200, self.move_enemy)  # Giảm delay xuống 200ms
                self.status_label.config(text=f'🎮 Bước đi: {self.player.moves} | ⚠️ AI đang đuổi!')
            else:
                next_ai_move = self.ai_move_frequency - (self.player_move_count % self.ai_move_frequency)
                self.status_label.config(text=f'🎮 Bước đi: {self.player.moves} | AI đuổi sau {next_ai_move} bước')
    
    def move_enemy(self):
        """Di chuyển enemy bằng AI"""
        if not self.enemy or not self.player:
            return
        
        # Dùng BFS để tìm đường
        bfs = BFS(self.maze.grid)
        next_move = bfs.get_next_move(self.enemy.get_position(), self.player.get_position())
        
        if next_move:
            self.enemy.move(next_move[0], next_move[1])
            
            # Kiểm tra bắt được player
            if next_move == self.player.get_position():
                elapsed_time = self.stop_timer()
                
                # Record stats
                self.stats_manager.record_game(
                    won=False,
                    time_seconds=elapsed_time,
                    steps=self.player.moves,
                    difficulty=self.difficulty_var.get(),
                    score=0
                )
                self.update_stats_display()
                
                self.maze_view.update_display(
                    player_pos=self.player.get_position(),
                    enemy_pos=self.enemy.get_position()
                )
                messagebox.showinfo('Game Over! 💀', 'AI đã bắt được bạn!')
                self.reset_game()
                return
            
            # Cập nhật hiển thị
            self.maze_view.update_display(
                player_pos=self.player.get_position(),
                enemy_pos=self.enemy.get_position()
            )
    
    def reset_game(self):
        """Reset trò chơi - với animation reset"""
        self.stop_timer()
        self.timer_label.config(text='⏱️ Thời gian: 00:00')
        self.score_label.config(text='🏆 Score: 0')
        self.current_score = 0
        
        # Reset animation states
        self.maze_view.reset_animations()
        
        if self.player:
            self.player.reset(self.maze.start_pos[0], self.maze.start_pos[1])
        
        if self.enemy:
            self.enemy.reset()
        
        if self.maze:
            self.maze_view.update_display(
                player_pos=self.player.get_position() if self.player else None,
                enemy_pos=self.enemy.get_position() if self.enemy else None
            )
        
        self.status_label.config(text='🔄 Đã reset trò chơi')
    
    def compare_algorithms(self):
        """So sánh các thuật toán"""
        if not self.maze:
            messagebox.showwarning('Cảnh báo', 'Vui lòng tạo mê cung trước!')
            return
        
        self.status_label.config(text='Đang so sánh thuật toán...')
        self.root.update()
        
        results = {}
        
        # Test từng thuật toán
        algorithms = [
            ('BFS', BFS),
            ('Dijkstra', Dijkstra),
            ('A*', AStar)
        ]
        
        for name, AlgoClass in algorithms:
            algo = AlgoClass(self.maze.grid)
            
            start_time = time.time()
            
            if name == 'BFS':
                path, steps = algo.find_path(self.maze.start_pos, self.maze.exit_pos)
            else:
                path, steps, _ = algo.find_path(self.maze.start_pos, self.maze.exit_pos)
            
            end_time = time.time()
            
            if path:
                results[name] = {
                    'Độ dài đường': len(path),
                    'Số bước duyệt': len(steps),
                    'Thời gian (ms)': f'{(end_time - start_time) * 1000:.2f}',
                    'Ô đã thăm': len(steps[-1].get('visited', set())) if steps else 0
                }
        
        # Hiển thị bảng so sánh
        self.debug_panel.show_comparison(results)
        self.status_label.config(text='✅ Hoàn thành so sánh thuật toán')
        
    def on_maze_click(self, event):
        """Xử lý click vào mê cung"""
        cell = self.maze_view.get_cell_from_click(event)
        if cell and self.player:
            # Có thể thêm tính năng click để di chuyển
            pass
    
    # ========== NEW FEATURES ==========
    
    def start_timer(self):
        """Bắt đầu đồng hồ"""
        self.game_start_time = time.time()
        self.update_timer()
    
    def update_timer(self):
        """Cập nhật đồng hồ"""
        if self.game_start_time and self.player:
            elapsed = time.time() - self.game_start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.timer_label.config(text=f'⏱️ Thời gian: {minutes:02d}:{seconds:02d}')
            self.game_timer_id = self.root.after(1000, self.update_timer)
    
    def stop_timer(self):
        """Dừng đồng hồ"""
        if self.game_timer_id:
            self.root.after_cancel(self.game_timer_id)
            self.game_timer_id = None
        return time.time() - self.game_start_time if self.game_start_time else 0
    
    def calculate_score(self, time_seconds, steps, won):
        """Tính điểm"""
        if not won:
            return 0
        
        # Base score
        base_score = 10000
        
        # Difficulty multiplier
        difficulty_multipliers = {
            'Rất dễ': 0.5,
            'Dễ': 1.0,
            'Trung bình': 1.5,
            'Khó': 2.0
        }
        multiplier = difficulty_multipliers.get(self.difficulty_var.get(), 1.0)
        
        # Penalties
        time_penalty = int(time_seconds * 10)
        step_penalty = steps * 5
        
        # Calculate final score
        score = int((base_score - time_penalty - step_penalty) * multiplier)
        return max(score, 0)
    
    def update_score_display(self, score):
        """Cập nhật hiển thị điểm"""
        self.current_score = score
        self.score_label.config(text=f'🏆 Score: {score}')
    
    def show_celebration(self):
        """Hiển thị hiệu ứng chiến thắng - smoother animation"""
        colors = ['#00ff41', '#ff0080', '#00d4ff', '#ffb400', '#7b2cbf']
        original_text = self.status_label.cget('text')
        
        def blink(count=0):
            if count < 10:  # Nhiều frame hơn cho smooth hơn
                color = colors[count % len(colors)]
                self.status_label.config(fg=color, text='🎉 CHIẾN THẮNG! 🎉')
                self.root.after(150, lambda: blink(count + 1))  # Nhỏp nhanh hơn
            else:
                self.status_label.config(fg='#00ff41', text=original_text)
        
        blink()
    
    def on_theme_change(self, event=None):
        """Thay đổi theme - CHỈ đổi màu sắc, không thay đổi nội dung"""
        theme_name = self.theme_var.get()
        if self.theme_manager.set_theme(theme_name):
            theme = self.theme_manager.get_theme()
            
            # Update root background
            self.root.configure(bg=theme.get('bg', '#1a1a2e'))
            
            # Update maze view colors - CHỈ ĐỔI MÀU, KHÔNG REDRAW
            self.maze_view.configure(bg=theme.get('bg', '#1a1a2e'),
                                    highlightbackground=theme.get('accent', '#00ff41'),
                                    highlightcolor=theme.get('accent', '#00ff41'))
            self.maze_view.colors = {
                'wall': theme.get('wall', '#0f3460'),
                'path': theme.get('path', '#16213e'),
                'start': theme.get('start', '#00ff41'),
                'exit': theme.get('exit', '#ff0080'),
                'player': theme.get('player', '#00d4ff'),
                'enemy': theme.get('enemy', '#ffb400'),
                'solution': theme.get('solution', '#7b2cbf'),
                'visited': theme.get('visited', '#c9ada7'),
                'current': theme.get('current', '#f72585'),
                'grid': theme.get('bg', '#1a1a2e')
            }
            
            # Chỉ invalidate cache để lần vẽ tiếp theo sử dụng màu mới
            # Không force redraw ngay
            self.maze_view._maze_cached = False
            
            # Update config panel backgrounds
            self.config_canvas.configure(bg=theme.get('panel', '#16213e'))
            self.config_scrollable_frame.configure(bg=theme.get('panel', '#16213e'))
            
            # Update debug panel - chỉ đổi theme, không clear content
            if hasattr(self.debug_panel, 'set_theme'):
                self.debug_panel._current_theme = theme
                self.debug_panel._apply_theme()
            
            # Cập nhật màu các widget - CHỈ MÀU, KHÔNG NỘI DUNG
            self._apply_theme_to_widgets(self.root, theme)
            
            # Nếu có maze, vẽ lại với màu mới nhưng GIỮ NGUYÊN TRẠNG THÁI
            if self.maze:
                # Lưu trạng thái hiện tại
                current_player = self.player.get_position() if self.player else None
                current_enemy = self.enemy.get_position() if self.enemy else None
                
                # Vẽ lại với màu mới
                self.maze_view.update_display(
                    player_pos=current_player,
                    enemy_pos=current_enemy
                )
    
    def _apply_theme_to_widgets(self, widget, theme):
        """Apply theme cho các widgets - CẬP NHẬT CẢ VIỀN VÀ MÀU SẮC"""
        try:
            widget_type = widget.winfo_class()
            
            if widget_type in ['Frame', 'Labelframe']:
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    
                    # === BORDER/SEPARATOR FRAMES - CẬP NHẬT VIỀN ===
                    # Các màu separator/border cũ cần map sang theme mới
                    border_color_map = {
                        # Separator colors (tất cả các theme)
                        '#00ff41': theme.get('separator', '#00ff41'),  # Dark
                        '#0a5a1a': theme.get('separator_dim', '#0a5a1a'),
                        '#00ff00': theme.get('separator', '#00ff41'),  # Black
                        '#004400': theme.get('separator_dim', '#0a5a1a'),
                        '#0066cc': theme.get('separator', '#00ff41'),  # White
                        '#a0c4e8': theme.get('separator_dim', '#0a5a1a'),
                        '#ff00ff': theme.get('separator', '#00ff41'),  # Galaxy
                        '#660066': theme.get('separator_dim', '#0a5a1a'),
                        '#64ffda': theme.get('separator', '#00ff41'),  # Ocean
                        '#1a5a4a': theme.get('separator_dim', '#0a5a1a'),
                        '#fd79a8': theme.get('separator', '#00ff41'),  # Sunset (fixed)
                        '#6d3948': theme.get('separator_dim', '#0a5a1a'),
                        
                        # Border accent colors - Dark
                        '#2a3a5e': theme.get('border', '#2a3a5e'),
                        '#3a4a6e': theme.get('border_light', '#3a4a6e'),
                        # Black
                        '#333333': theme.get('border', '#2a3a5e'),
                        '#444444': theme.get('border_light', '#3a4a6e'),
                        # White
                        '#d0d0d0': theme.get('border', '#2a3a5e'),
                        '#e0e0e0': theme.get('border_light', '#3a4a6e'),
                        # Galaxy
                        '#3a2060': theme.get('border', '#2a3a5e'),
                        '#4a3070': theme.get('border_light', '#3a4a6e'),
                        # Ocean
                        '#233554': theme.get('border', '#2a3a5e'),
                        '#334564': theme.get('border_light', '#3a4a6e'),
                        # Sunset (fixed)
                        '#4d3f5d': theme.get('border', '#2a3a5e'),
                        '#5d4f6d': theme.get('border_light', '#3a4a6e'),
                    }
                    
                    # Kiểm tra xem frame này có phải là border/separator không
                    if current_bg in border_color_map:
                        widget.configure(bg=border_color_map[current_bg])
                    else:
                        # Panel backgrounds
                        panel_bg_map = {
                            # Dark theme
                            '#16213e': theme.get('panel', '#16213e'),
                            '#1a1a2e': theme.get('bg', '#1a1a2e'),
                            '#0f3460': theme.get('panel_dark', '#0f3460'),
                            '#1e2a4a': theme.get('panel_light', '#1e2a4a'),
                            '#243050': theme.get('card_header', '#243050'),
                            '#1e2848': theme.get('card_bg', '#1e2848'),
                            '#141a30': theme.get('section_bg', '#141a30'),
                            '#0f0f0f': theme.get('bg', '#1a1a2e'),
                            # Black theme
                            '#0a0a0a': theme.get('panel', '#16213e'),
                            '#000000': theme.get('bg', '#1a1a2e'),
                            '#0d0d0d': theme.get('card_bg', '#1e2848'),
                            '#111111': theme.get('card_header', '#243050'),
                            # White theme
                            '#f5f5f5': theme.get('panel', '#16213e'),
                            '#ffffff': theme.get('bg', '#1a1a2e'),
                            '#f0f0f0': theme.get('card_header', '#243050'),
                            '#fafafa': theme.get('section_bg', '#141a30'),
                            # Galaxy theme
                            '#1a0030': theme.get('panel', '#16213e'),
                            '#0a0015': theme.get('bg', '#1a1a2e'),
                            '#150025': theme.get('card_bg', '#1e2848'),
                            '#200040': theme.get('card_header', '#243050'),
                            # Ocean theme
                            '#112240': theme.get('panel', '#16213e'),
                            '#0a192f': theme.get('bg', '#1a1a2e'),
                            '#152238': theme.get('card_bg', '#1e2848'),
                            '#1a2a48': theme.get('card_header', '#243050'),
                            '#0d1a2d': theme.get('section_bg', '#141a30'),
                            # Sunset theme
                            '#2d1f3d': theme.get('panel', '#16213e'),
                            '#1a1423': theme.get('bg', '#1a1a2e'),
                            '#2a1a35': theme.get('card_bg', '#1e2848'),
                            '#352545': theme.get('card_header', '#243050'),
                            '#201530': theme.get('section_bg', '#141a30'),
                        }
                        new_bg = panel_bg_map.get(current_bg, theme.get('panel', '#16213e'))
                        widget.configure(bg=new_bg)
                except:
                    pass
                    
            elif widget_type == 'Label':
                try:
                    current_fg = str(widget.cget('fg')).lower()
                    current_bg = str(widget.cget('bg')).lower()
                    
                    # Map accent colors to new theme
                    accent_map = {
                        # Dark theme
                        '#00ff41': theme.get('accent', '#00ff41'),
                        '#00d4ff': theme.get('accent2', '#00d4ff'),
                        '#ff0080': theme.get('accent3', '#f72585'),
                        '#f72585': theme.get('accent3', '#f72585'),
                        '#ffb400': theme.get('warning', '#ffb400'),
                        '#7b2cbf': theme.get('button', '#7b2cbf'),
                        '#c9ada7': theme.get('text_dim', '#c9ada7'),
                        '#8a8a9a': theme.get('text_muted', '#8a8a9a'),
                        # Black theme
                        '#00ff00': theme.get('accent', '#00ff41'),
                        '#00ffff': theme.get('accent2', '#00d4ff'),
                        '#ff0000': theme.get('accent3', '#f72585'),
                        '#ffff00': theme.get('warning', '#ffb400'),
                        # White theme
                        '#0066cc': theme.get('accent', '#00ff41'),
                        '#00aa00': theme.get('accent2', '#00d4ff'),
                        '#cc0000': theme.get('accent3', '#f72585'),
                        '#cc8800': theme.get('warning', '#ffb400'),
                        '#1a1a1a': theme.get('text', '#ffffff'),
                        '#666666': theme.get('text_dim', '#c9ada7'),
                        # Galaxy theme
                        '#ff00ff': theme.get('accent', '#00ff41'),
                        '#e0d0ff': theme.get('text', '#ffffff'),
                        '#9080b0': theme.get('text_dim', '#c9ada7'),
                        # Ocean theme
                        '#64ffda': theme.get('accent', '#00ff41'),
                        '#57cbff': theme.get('accent2', '#00d4ff'),
                        '#ff6b9d': theme.get('accent3', '#f72585'),
                        '#ffd93d': theme.get('warning', '#ffb400'),
                        '#ccd6f6': theme.get('text', '#ffffff'),
                        '#8892b0': theme.get('text_dim', '#c9ada7'),
                        # Sunset theme
                        '#fd79a8': theme.get('accent', '#00ff41'),
                        '#fdcb6e': theme.get('accent2', '#00d4ff'),
                        '#74b9ff': theme.get('accent3', '#f72585'),
                        '#ff7675': theme.get('error', '#ff0080'),
                        '#ffeaa7': theme.get('text', '#ffffff'),
                        '#dda0a0': theme.get('text_dim', '#c9ada7'),
                    }
                    new_fg = accent_map.get(current_fg, theme.get('text', '#ffffff'))
                    
                    # Background cho label
                    bg_map = {
                        '#16213e': theme.get('panel', '#16213e'),
                        '#243050': theme.get('card_header', '#243050'),
                        '#1e2848': theme.get('card_bg', '#1e2848'),
                        '#1a1a2e': theme.get('bg', '#1a1a2e'),
                    }
                    new_bg = bg_map.get(current_bg, theme.get('panel', '#16213e'))
                    
                    widget.configure(bg=new_bg, fg=new_fg)
                except:
                    pass
                    
            elif widget_type == 'Canvas':
                try:
                    widget.configure(bg=theme.get('bg', '#1a1a2e'))
                except:
                    pass
                    
            elif widget_type == 'Button':
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    button_map = {
                        '#7b2cbf': theme.get('button', '#7b2cbf'),
                        '#9b4cdf': theme.get('button_hover', '#9b4cdf'),
                        '#00ff41': theme.get('success', '#00ff41'),
                        '#00d4ff': theme.get('info', '#00d4ff'),
                        '#f72585': theme.get('accent3', '#f72585'),
                        '#ff0080': theme.get('error', '#ff0080'),
                        '#1a1a1a': theme.get('button', '#7b2cbf'),
                        '#2a1050': theme.get('button', '#7b2cbf'),
                        '#1d4e89': theme.get('button', '#7b2cbf'),
                        '#c44520': theme.get('button', '#7b2cbf'),
                        '#e0e0e0': theme.get('button', '#7b2cbf'),
                    }
                    new_bg = button_map.get(current_bg, theme.get('button', '#7b2cbf'))
                    widget.configure(bg=new_bg, fg=theme.get('text', '#ffffff'),
                                   activebackground=theme.get('button_hover', '#9b4cdf'))
                except:
                    pass
            
            # Recursive cho children
            for child in widget.winfo_children():
                self._apply_theme_to_widgets(child, theme)
                self._apply_theme_to_widgets(child, theme)
        except:
            pass
            if self.maze:
                self.maze_view.update_display(
                    player_pos=self.player.position if self.player else None,
                    enemy_pos=self.enemy.position if self.enemy else None
                )
    
    def save_game(self):
        """Lưu game"""
        if not self.maze or not self.player:
            messagebox.showwarning('Cảnh báo', 'Chưa có game để lưu!')
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')]
        )
        
        if filename:
            try:
                game_state = {
                    'maze_size': (self.maze.width, self.maze.height),
                    'maze_grid': self.maze.grid,
                    'player_pos': self.player.position,
                    'enemy_pos': self.enemy.position if self.enemy else None,
                    'difficulty': self.difficulty_var.get(),
                    'elapsed_time': self.stop_timer() if self.game_start_time else 0,
                    'player_moves': self.player_move_count,
                    'score': self.current_score
                }
                
                with open(filename, 'w') as f:
                    json.dump(game_state, f)
                
                messagebox.showinfo('Thành công', 'Đã lưu game!')
                
                # Restart timer if it was running
                if self.game_start_time:
                    self.game_start_time = time.time() - game_state['elapsed_time']
                    self.update_timer()
            except Exception as e:
                messagebox.showerror('Lỗi', f'Không thể lưu: {e}')
    
    def load_game(self):
        """Load game"""
        filename = filedialog.askopenfilename(
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    game_state = json.load(f)
                
                # Restore maze
                width, height = game_state['maze_size']
                self.maze = Maze(width, height)
                self.maze.set_grid(game_state['maze_grid'])
                
                # Restore player
                px, py = game_state['player_pos']
                self.player = Player(px, py)
                self.player_move_count = game_state.get('player_moves', 0)
                
                # Restore enemy
                if game_state.get('enemy_pos'):
                    ex, ey = game_state['enemy_pos']
                    self.enemy = Enemy(ex, ey)
                
                # Restore UI
                self.difficulty_var.set(game_state.get('difficulty', 'Dễ'))
                self.on_difficulty_change()
                
                # Restore timer
                elapsed = game_state.get('elapsed_time', 0)
                self.game_start_time = time.time() - elapsed
                self.update_timer()
                
                # Restore score
                self.current_score = game_state.get('score', 0)
                self.update_score_display(self.current_score)
                
                # Update display
                self.maze_view.set_maze(self.maze)
                self.maze_view.update_display(player_pos=self.player.position,
                                              enemy_pos=self.enemy.position if self.enemy else None)
                
                self.status_label.config(text='✅ Đã load game!')
                messagebox.showinfo('Thành công', 'Đã load game!')
                
            except Exception as e:
                messagebox.showerror('Lỗi', f'Không thể load: {e}')
    
    def update_stats_display(self):
        """Cập nhật hiển thị thống kê"""
        stats = self.stats_manager.get_summary()
        
        self.stats_labels['🎮 Tổng trận:'].config(text=f"{stats['total']}")
        self.stats_labels['✅ Thắng:'].config(text=f"{stats['wins']}")
        self.stats_labels['❌ Thua:'].config(text=f"{stats['losses']}")
        self.stats_labels['📈 Win rate:'].config(text=f"{stats['win_rate']:.1f}%")
        self.stats_labels['⏱️ Best time:'].config(
            text=f"{stats['best_time']:.1f}s" if stats['best_time'] else 'N/A'
        )
        self.stats_labels['🏆 Best score:'].config(text=f"{stats['best_score']}")

    # ========== CHỨC NĂNG ÂM THANH ==========
    
    def init_music(self):
        """Khởi tạo và tự động phát nhạc nền"""
        if not SOUND_AVAILABLE:
            print("⚠️ Pygame không khả dụng, không thể phát nhạc")
            return
        
        try:
            if os.path.exists(self.music_file):
                pygame.mixer.music.load(self.music_file)
                pygame.mixer.music.set_volume(0.3)  # Volume 30%
                pygame.mixer.music.play(-1)  # -1 = loop vô hạn
                self.sound_enabled = True
                print("🎵 Đã bật nhạc nền")
            else:
                print(f"⚠️ Không tìm thấy file nhạc: {self.music_file}")
                self.sound_enabled = False
        except Exception as e:
            print(f"⚠️ Lỗi phát nhạc: {e}")
            self.sound_enabled = False
    
    def toggle_sound(self):
        """Bật/Tắt nhạc nền"""
        if not SOUND_AVAILABLE:
            messagebox.showwarning("Cảnh báo", "Pygame không khả dụng!\nCài đặt: pip install pygame")
            return
        
        theme = self.theme_manager.get_theme()
        
        if self.sound_enabled:
            # Tắt nhạc
            pygame.mixer.music.pause()
            self.sound_enabled = False
            self.sound_btn.config(text='🔇', bg='#ff4444')
            self._update_tooltip(self.sound_btn, "Bật/Tắt nhạc nền (đang tắt)")
        else:
            # Bật nhạc
            try:
                pygame.mixer.music.unpause()
            except:
                # Nếu chưa load thì load lại
                if os.path.exists(self.music_file):
                    pygame.mixer.music.load(self.music_file)
                    pygame.mixer.music.set_volume(0.3)
                    pygame.mixer.music.play(-1)
            self.sound_enabled = True
            self.sound_btn.config(text='🔊', bg=theme.get('button', '#7b2cbf'))
            self._update_tooltip(self.sound_btn, "Bật/Tắt nhạc nền (đang bật)")
    
    def _create_tooltip(self, widget, text):
        """Tạo tooltip cho widget"""
        tooltip = None
        
        def show_tooltip(event):
            nonlocal tooltip
            x, y, _, _ = widget.bbox("insert") if hasattr(widget, 'bbox') else (0, 0, 0, 0)
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(tooltip, text=text, 
                           bg='#333333', fg='#ffffff',
                           relief='solid', borderwidth=1,
                           font=('Arial', 9),
                           padx=5, pady=3)
            label.pack()
            
            # Lưu reference
            widget._tooltip = tooltip
            widget._tooltip_text = text
        
        def hide_tooltip(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None
            if hasattr(widget, '_tooltip') and widget._tooltip:
                try:
                    widget._tooltip.destroy()
                except:
                    pass
                widget._tooltip = None
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def _update_tooltip(self, widget, new_text):
        """Cập nhật text tooltip"""
        if hasattr(widget, '_tooltip_text'):
            widget._tooltip_text = new_text


def run():
    """Chạy ứng dụng"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
