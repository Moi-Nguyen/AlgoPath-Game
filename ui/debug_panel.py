"""
Debug Panel - Hiển thị thông tin debug từng bước thuật toán với styled UI
"""

import tkinter as tk
from tkinter import ttk


class DebugPanel(tk.Frame):
    def __init__(self, parent, theme_manager=None):
        """
        Khởi tạo panel debug với enhanced styled UI
        
        Args:
            parent: Widget cha
            theme_manager: ThemeManager instance để lấy màu sắc
        """
        super().__init__(parent, bg='#16213e')
        
        self.theme_manager = theme_manager
        self._current_theme = self._get_default_theme()
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Debug.TLabel', background='#16213e', foreground='#ffffff', font=('Consolas', 10))
        style.configure('Title.TLabel', background='#16213e', foreground='#00ff41', font=('Arial', 14, 'bold'))
        
        # Animation states cho smooth transitions
        self._fade_alpha = 1.0
        self._transition_queue = []
        self._animating = False
        
        self.create_widgets()
    
    def _get_default_theme(self):
        """Lấy theme mặc định"""
        return {
            'bg': '#1a1a2e',
            'panel': '#16213e',
            'panel_dark': '#0f3460',
            'panel_light': '#1e2a4a',
            'text': '#ffffff',
            'text_dim': '#c9ada7',
            'text_muted': '#8a8a9a',
            'accent': '#00ff41',
            'accent2': '#00d4ff',
            'accent3': '#f72585',
            'separator': '#00ff41',
            'separator_dim': '#0a5a1a',
            'border': '#2a3a5e',
            'border_light': '#3a4a6e',
            'card_bg': '#1e2848',
            'card_border': '#2a3858',
            'card_header': '#243050',
            'section_bg': '#141a30',
            'success': '#00ff41',
            'warning': '#ffb400',
            'error': '#ff0080',
            'info': '#00d4ff',
        }
    
    def get_theme(self):
        """Lấy theme hiện tại"""
        if self.theme_manager:
            return self.theme_manager.get_theme()
        return self._current_theme
    
    def set_theme(self, theme):
        """Cập nhật theme"""
        self._current_theme = theme
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply theme cho panel - CHỈ ĐỔI MÀU, KHÔNG CLEAR CONTENT"""
        theme = self.get_theme()
        self.configure(bg=theme.get('panel', '#16213e'))
        self.scroll_canvas.configure(bg=theme.get('panel', '#16213e'))
        self.content_frame.configure(bg=theme.get('panel', '#16213e'))
        
        # Recursive update colors cho tất cả children
        self._update_widget_colors(self.content_frame, theme)
    
    def _update_widget_colors(self, widget, theme):
        """Recursive update màu sắc cho widgets - CẬP NHẬT CẢ VIỀN"""
        try:
            widget_type = widget.winfo_class()
            
            if widget_type in ['Frame', 'Labelframe']:
                try:
                    current_bg = str(widget.cget('bg')).lower()
                    
                    # === BORDER/SEPARATOR FRAMES ===
                    border_color_map = {
                        # Dark
                        '#00ff41': theme.get('separator', '#00ff41'),
                        '#0a5a1a': theme.get('separator_dim', '#0a5a1a'),
                        '#2a3a5e': theme.get('border', '#2a3a5e'),
                        '#3a4a6e': theme.get('border_light', '#3a4a6e'),
                        # Black
                        '#00ff00': theme.get('separator', '#00ff41'),
                        '#004400': theme.get('separator_dim', '#0a5a1a'),
                        '#333333': theme.get('border', '#2a3a5e'),
                        '#444444': theme.get('border_light', '#3a4a6e'),
                        # White
                        '#0066cc': theme.get('separator', '#00ff41'),
                        '#a0c4e8': theme.get('separator_dim', '#0a5a1a'),
                        '#d0d0d0': theme.get('border', '#2a3a5e'),
                        '#e0e0e0': theme.get('border_light', '#3a4a6e'),
                        # Galaxy
                        '#ff00ff': theme.get('separator', '#00ff41'),
                        '#660066': theme.get('separator_dim', '#0a5a1a'),
                        '#3a2060': theme.get('border', '#2a3a5e'),
                        '#4a3070': theme.get('border_light', '#3a4a6e'),
                        # Ocean
                        '#64ffda': theme.get('separator', '#00ff41'),
                        '#1a5a4a': theme.get('separator_dim', '#0a5a1a'),
                        '#233554': theme.get('border', '#2a3a5e'),
                        '#334564': theme.get('border_light', '#3a4a6e'),
                        # Sunset
                        '#fd79a8': theme.get('separator', '#00ff41'),
                        '#6d3948': theme.get('separator_dim', '#0a5a1a'),
                        '#4d3f5d': theme.get('border', '#2a3a5e'),
                        '#5d4f6d': theme.get('border_light', '#3a4a6e'),
                    }
                    
                    if current_bg in border_color_map:
                        widget.configure(bg=border_color_map[current_bg])
                    else:
                        # Panel backgrounds
                        panel_bg_map = {
                            # Dark
                            '#16213e': theme.get('panel', '#16213e'),
                            '#1a1a2e': theme.get('bg', '#1a1a2e'),
                            '#243050': theme.get('card_header', '#243050'),
                            '#1e2848': theme.get('card_bg', '#1e2848'),
                            '#141a30': theme.get('section_bg', '#141a30'),
                            # Black
                            '#0a0a0a': theme.get('panel', '#16213e'),
                            '#000000': theme.get('bg', '#1a1a2e'),
                            '#0d0d0d': theme.get('card_bg', '#1e2848'),
                            '#111111': theme.get('card_header', '#243050'),
                            # White
                            '#f5f5f5': theme.get('panel', '#16213e'),
                            '#ffffff': theme.get('bg', '#1a1a2e'),
                            '#f0f0f0': theme.get('card_header', '#243050'),
                            # Galaxy
                            '#1a0030': theme.get('panel', '#16213e'),
                            '#0a0015': theme.get('bg', '#1a1a2e'),
                            '#150025': theme.get('card_bg', '#1e2848'),
                            '#200040': theme.get('card_header', '#243050'),
                            # Ocean
                            '#112240': theme.get('panel', '#16213e'),
                            '#0a192f': theme.get('bg', '#1a1a2e'),
                            '#152238': theme.get('card_bg', '#1e2848'),
                            '#1a2a48': theme.get('card_header', '#243050'),
                            '#0d1a2d': theme.get('section_bg', '#141a30'),
                            # Sunset
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
                    
                    # Map accent colors
                    accent_map = {
                        # Dark
                        '#00ff41': theme.get('accent', '#00ff41'),
                        '#00d4ff': theme.get('accent2', '#00d4ff'),
                        '#f72585': theme.get('accent3', '#f72585'),
                        '#ffb400': theme.get('warning', '#ffb400'),
                        '#c9ada7': theme.get('text_dim', '#c9ada7'),
                        '#8a8a9a': theme.get('text_muted', '#8a8a9a'),
                        # Black
                        '#00ff00': theme.get('accent', '#00ff41'),
                        '#00ffff': theme.get('accent2', '#00d4ff'),
                        '#ff0000': theme.get('accent3', '#f72585'),
                        '#ffff00': theme.get('warning', '#ffb400'),
                        # White
                        '#0066cc': theme.get('accent', '#00ff41'),
                        '#00aa00': theme.get('accent2', '#00d4ff'),
                        '#cc0000': theme.get('accent3', '#f72585'),
                        # Galaxy
                        '#ff00ff': theme.get('accent', '#00ff41'),
                        '#e0d0ff': theme.get('text', '#ffffff'),
                        '#9080b0': theme.get('text_dim', '#c9ada7'),
                        # Ocean
                        '#64ffda': theme.get('accent', '#00ff41'),
                        '#57cbff': theme.get('accent2', '#00d4ff'),
                        '#ff6b9d': theme.get('accent3', '#f72585'),
                        '#ccd6f6': theme.get('text', '#ffffff'),
                        '#8892b0': theme.get('text_dim', '#c9ada7'),
                        # Sunset
                        '#fd79a8': theme.get('accent', '#00ff41'),
                        '#fdcb6e': theme.get('accent2', '#00d4ff'),
                        '#74b9ff': theme.get('accent3', '#f72585'),
                        '#ffeaa7': theme.get('text', '#ffffff'),
                        '#dda0a0': theme.get('text_dim', '#c9ada7'),
                    }
                    new_fg = accent_map.get(current_fg, theme.get('text', '#ffffff'))
                    
                    # Background cho label
                    bg_map = {
                        '#16213e': theme.get('panel', '#16213e'),
                        '#243050': theme.get('card_header', '#243050'),
                        '#1e2848': theme.get('card_bg', '#1e2848'),
                        '#141a30': theme.get('section_bg', '#141a30'),
                    }
                    new_bg = bg_map.get(current_bg, theme.get('panel', '#16213e'))
                    
                    widget.configure(bg=new_bg, fg=new_fg)
                except:
                    pass
                    
            elif widget_type == 'Canvas':
                try:
                    widget.configure(bg=theme.get('panel', '#16213e'))
                except:
                    pass
            
            for child in widget.winfo_children():
                self._update_widget_colors(child, theme)
        except:
            pass
    
    def create_widgets(self):
        """Tạo các widget với styled UI"""
        theme = self.get_theme()
        
        # === STYLED HEADER ===
        header_frame = tk.Frame(self, bg=theme.get('card_header', '#243050'))
        header_frame.pack(fill='x', padx=5, pady=(5, 0))
        
        # Top accent line
        tk.Frame(header_frame, height=3, bg=theme.get('accent2', '#00d4ff')).pack(fill='x')
        
        # Header content
        header_content = tk.Frame(header_frame, bg=theme.get('card_header', '#243050'))
        header_content.pack(fill='x', padx=10, pady=8)
        
        # Icon + Title
        title_row = tk.Frame(header_content, bg=theme.get('card_header', '#243050'))
        title_row.pack(fill='x')
        
        tk.Label(title_row, text='🔍', bg=theme.get('card_header', '#243050'), 
                font=('Arial', 16)).pack(side='left')
        tk.Label(title_row, text=' DEBUG PANEL', bg=theme.get('card_header', '#243050'), 
                fg=theme.get('accent', '#00ff41'), font=('Arial', 14, 'bold')).pack(side='left')
        
        # Subtitle
        tk.Label(header_content, text='Phân tích thuật toán', 
                bg=theme.get('card_header', '#243050'), 
                fg=theme.get('text_dim', '#c9ada7'), 
                font=('Arial', 9)).pack(anchor='w')
        
        # === STYLED SEPARATOR ===
        sep_frame = tk.Frame(self, bg=theme.get('panel', '#16213e'))
        sep_frame.pack(fill='x', padx=10, pady=5)
        
        # Gradient separator
        tk.Frame(sep_frame, height=1, bg=theme.get('separator_dim', '#0a5a1a')).pack(fill='x')
        
        sep_inner = tk.Frame(sep_frame, bg=theme.get('panel', '#16213e'))
        sep_inner.pack(fill='x', pady=1)
        
        tk.Frame(sep_inner, width=20, height=2, bg=theme.get('accent', '#00ff41')).pack(side='left')
        tk.Frame(sep_inner, height=1, bg=theme.get('separator', '#00ff41')).pack(side='left', fill='x', expand=True, padx=2)
        tk.Frame(sep_inner, width=20, height=2, bg=theme.get('accent', '#00ff41')).pack(side='right')
        
        tk.Frame(sep_frame, height=1, bg=theme.get('separator_dim', '#0a5a1a')).pack(fill='x')
        
        # === SMOOTH SCROLLABLE CONTENT ===
        scroll_container = tk.Frame(self, bg=theme.get('panel', '#16213e'))
        scroll_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tạo canvas cho smooth scrolling
        self.scroll_canvas = tk.Canvas(scroll_container, bg=theme.get('panel', '#16213e'), 
                                       highlightthickness=0)
        self.scrollbar = tk.Scrollbar(scroll_container, orient='vertical', 
                                      command=self.scroll_canvas.yview)
        self.content_frame = tk.Frame(self.scroll_canvas, bg=theme.get('panel', '#16213e'))
        
        # Configure canvas
        self.scroll_canvas.create_window((0, 0), window=self.content_frame, anchor='nw', width=270)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack
        self.scroll_canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        
        # Smooth scroll handling
        self._scroll_velocity = 0
        self._scroll_animating = False
        
        def _smooth_scroll_update():
            if not self._scroll_animating:
                return
            if abs(self._scroll_velocity) > 0.3:
                self.scroll_canvas.yview_scroll(int(self._scroll_velocity), "units")
                self._scroll_velocity *= 0.85
                self.after(16, _smooth_scroll_update)
            else:
                self._scroll_velocity = 0
                self._scroll_animating = False
        
        def _on_mousewheel(event):
            delta = -1 if event.delta > 0 else 1
            self._scroll_velocity = delta * 3
            if not self._scroll_animating:
                self._scroll_animating = True
                _smooth_scroll_update()
        
        self.scroll_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.content_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # Bind scroll cho tất cả children
        def _bind_scroll(widget):
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                _bind_scroll(child)
        
        self.after(100, lambda: _bind_scroll(self.content_frame))
    
    def _create_card(self, parent, title=None, accent_color=None):
        """Tạo styled card container"""
        theme = self.get_theme()
        
        if accent_color is None:
            accent_color = theme.get('accent', '#00ff41')
        
        card = tk.Frame(parent, bg=theme.get('card_bg', '#1e2848'))
        
        # Top accent
        tk.Frame(card, height=2, bg=accent_color).pack(fill='x')
        
        # Content area
        content = tk.Frame(card, bg=theme.get('card_bg', '#1e2848'))
        content.pack(fill='x', padx=10, pady=8)
        
        if title:
            title_frame = tk.Frame(content, bg=theme.get('card_bg', '#1e2848'))
            title_frame.pack(fill='x', pady=(0, 5))
            
            tk.Label(title_frame, text=title, bg=theme.get('card_bg', '#1e2848'), 
                    fg=accent_color, font=('Arial', 11, 'bold')).pack(side='left')
            
            # Separator after title
            tk.Frame(content, height=1, bg=theme.get('border', '#2a3a5e')).pack(fill='x', pady=(0, 5))
        
        # Bottom border
        tk.Frame(card, height=1, bg=theme.get('card_border', '#2a3858')).pack(fill='x')
        
        return card, content
        
    def show_algorithm_info(self, algo_info: dict):
        """
        Hiển thị thông tin thuật toán với styled cards
        
        Args:
            algo_info: Dict chứa thông tin thuật toán
        """
        self.clear()
        theme = self.get_theme()
        
        # === ALGORITHM NAME CARD ===
        name_card, name_content = self._create_card(self.content_frame, None, theme.get('accent', '#00ff41'))
        name_card.pack(fill='x', padx=5, pady=(5, 3))
        
        name_row = tk.Frame(name_content, bg=theme.get('card_bg', '#1e2848'))
        name_row.pack(fill='x')
        
        tk.Label(name_row, text='📊', bg=theme.get('card_bg', '#1e2848'), 
                font=('Arial', 14)).pack(side='left')
        tk.Label(name_row, text=f" {algo_info['name']}", bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('accent', '#00ff41'), font=('Arial', 12, 'bold')).pack(side='left')
        
        # === COMPLEXITY CARD ===
        complex_card, complex_content = self._create_card(self.content_frame, '⚡ Độ phức tạp', 
                                                          theme.get('accent2', '#00d4ff'))
        complex_card.pack(fill='x', padx=5, pady=3)
        
        self._add_styled_row(complex_content, '⏱️ Time:', algo_info['time_complexity'], theme)
        self._add_styled_row(complex_content, '💾 Space:', algo_info['space_complexity'], theme)
        
        # === DESCRIPTION CARD ===
        desc_card, desc_content = self._create_card(self.content_frame, '📝 Mô tả', 
                                                    theme.get('info', '#00d4ff'))
        desc_card.pack(fill='x', padx=5, pady=3)
        
        desc_label = tk.Label(desc_content, text=algo_info['description'], 
                            bg=theme.get('card_bg', '#1e2848'), 
                            fg=theme.get('text', '#ffffff'), 
                            font=('Arial', 9), wraplength=240, justify='left')
        desc_label.pack(fill='x')
        
        # === ADVANTAGES CARD ===
        if 'advantages' in algo_info:
            adv_card, adv_content = self._create_card(self.content_frame, '✅ Ưu điểm', 
                                                      theme.get('success', '#00ff41'))
            adv_card.pack(fill='x', padx=5, pady=3)
            
            for item in algo_info['advantages']:
                item_frame = tk.Frame(adv_content, bg=theme.get('card_bg', '#1e2848'))
                item_frame.pack(fill='x', pady=1)
                
                tk.Frame(item_frame, width=6, height=6, bg=theme.get('success', '#00ff41')).pack(side='left', padx=(0, 6))
                tk.Label(item_frame, text=item, bg=theme.get('card_bg', '#1e2848'), 
                        fg=theme.get('text', '#ffffff'), font=('Arial', 9),
                        wraplength=220, justify='left').pack(side='left', fill='x')
        
        # === DISADVANTAGES CARD ===
        if 'disadvantages' in algo_info:
            dis_card, dis_content = self._create_card(self.content_frame, '❌ Nhược điểm', 
                                                      theme.get('error', '#ff0080'))
            dis_card.pack(fill='x', padx=5, pady=3)
            
            for item in algo_info['disadvantages']:
                item_frame = tk.Frame(dis_content, bg=theme.get('card_bg', '#1e2848'))
                item_frame.pack(fill='x', pady=1)
                
                tk.Frame(item_frame, width=6, height=6, bg=theme.get('error', '#ff0080')).pack(side='left', padx=(0, 6))
                tk.Label(item_frame, text=item, bg=theme.get('card_bg', '#1e2848'), 
                        fg=theme.get('text', '#ffffff'), font=('Arial', 9),
                        wraplength=220, justify='left').pack(side='left', fill='x')
        
        # Update scroll region
        self.after(50, self._update_scroll_region)
    
    def _add_styled_row(self, parent, label, value, theme):
        """Thêm dòng thông tin với styling"""
        row = tk.Frame(parent, bg=theme.get('card_bg', '#1e2848'))
        row.pack(fill='x', pady=2)
        
        tk.Label(row, text=label, bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('text_dim', '#c9ada7'), font=('Consolas', 9),
                width=10, anchor='w').pack(side='left')
        tk.Label(row, text=value, bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('text', '#ffffff'), font=('Consolas', 9, 'bold')).pack(side='left')
    
    def show_step_info(self, step: dict, step_number: int, total_steps: int):
        """
        Hiển thị thông tin bước hiện tại với styled cards
        
        Args:
            step: Dict chứa thông tin bước
            step_number: Số thứ tự bước
            total_steps: Tổng số bước
        """
        self.clear()
        theme = self.get_theme()
        
        # === PROGRESS CARD ===
        progress_card, progress_content = self._create_card(self.content_frame, None, 
                                                           theme.get('accent', '#00ff41'))
        progress_card.pack(fill='x', padx=5, pady=(5, 3))
        
        # Progress header
        progress_header = tk.Frame(progress_content, bg=theme.get('card_bg', '#1e2848'))
        progress_header.pack(fill='x')
        
        tk.Label(progress_header, text=f"Bước {step_number}", bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('accent', '#00ff41'), font=('Arial', 12, 'bold')).pack(side='left')
        tk.Label(progress_header, text=f" / {total_steps}", bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('text_dim', '#c9ada7'), font=('Arial', 10)).pack(side='left')
        
        # Percentage
        percent = int((step_number / total_steps) * 100)
        tk.Label(progress_header, text=f"{percent}%", bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('accent2', '#00d4ff'), font=('Arial', 10, 'bold')).pack(side='right')
        
        # Styled progress bar
        bar_container = tk.Frame(progress_content, bg=theme.get('section_bg', '#141a30'), 
                                height=16, relief='flat')
        bar_container.pack(fill='x', pady=(8, 0))
        bar_container.pack_propagate(False)
        
        # Border
        bar_border = tk.Frame(bar_container, bg=theme.get('border', '#2a3a5e'))
        bar_border.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Inner bar background
        bar_bg = tk.Frame(bar_border, bg=theme.get('panel_dark', '#0f3460'))
        bar_bg.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Actual progress
        progress_width = max(1, int((step_number / total_steps) * 240))
        progress_bar = tk.Frame(bar_bg, bg=theme.get('accent', '#00ff41'), width=progress_width)
        progress_bar.place(x=0, y=0, relheight=1)
        
        # === STEP INFO CARD ===
        info_card, info_content = self._create_card(self.content_frame, '📍 Chi tiết bước', 
                                                    theme.get('info', '#00d4ff'))
        info_card.pack(fill='x', padx=5, pady=3)
        
        # Thông tin bước
        if 'current' in step:
            self._add_styled_row(info_content, '📍 Vị trí:', f"{step['current']}", theme)
        
        if 'visited' in step:
            self._add_styled_row(info_content, '✓ Đã thăm:', f"{len(step['visited'])} ô", theme)
        
        if 'queue_size' in step:
            self._add_styled_row(info_content, '📦 Queue:', f"{step['queue_size']}", theme)
        
        if 'heap_size' in step:
            self._add_styled_row(info_content, '🗂️ Heap:', f"{step['heap_size']}", theme)
        
        if 'current_distance' in step:
            self._add_styled_row(info_content, '📏 Distance:', f"{step['current_distance']}", theme)
        
        if 'current_g' in step:
            self._add_styled_row(info_content, '📏 g(n):', f"{step['current_g']}", theme)
        
        if 'current_f' in step:
            self._add_styled_row(info_content, '🎯 f(n):', f"{step['current_f']}", theme)
        
        if 'heuristic' in step:
            self._add_styled_row(info_content, '🧭 h(n):', f"{step['heuristic']}", theme)
        
        # Update scroll region
        self.after(50, self._update_scroll_region)
    
    def show_result(self, result: dict):
        """
        Hiển thị kết quả thuật toán với styled cards
        
        Args:
            result: Dict chứa kết quả
        """
        self.clear()
        theme = self.get_theme()
        
        # === SUCCESS HEADER CARD ===
        header_card, header_content = self._create_card(self.content_frame, None, 
                                                        theme.get('success', '#00ff41'))
        header_card.pack(fill='x', padx=5, pady=(5, 3))
        
        # Success animation effect (static version)
        header_row = tk.Frame(header_content, bg=theme.get('card_bg', '#1e2848'))
        header_row.pack(fill='x')
        
        tk.Label(header_row, text='🎉', bg=theme.get('card_bg', '#1e2848'), 
                font=('Arial', 16)).pack(side='left')
        tk.Label(header_row, text=' KẾT QUẢ', bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('success', '#00ff41'), font=('Arial', 14, 'bold')).pack(side='left')
        tk.Label(header_row, text=' ✓', bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('success', '#00ff41'), font=('Arial', 14)).pack(side='right')
        
        # === RESULTS CARD ===
        result_card, result_content = self._create_card(self.content_frame, '📊 Thống kê', 
                                                        theme.get('accent2', '#00d4ff'))
        result_card.pack(fill='x', padx=5, pady=3)
        
        # Results in styled rows
        if 'path_length' in result:
            self._add_result_styled_row(result_content, '📏 Độ dài đường', 
                                       f"{result['path_length']} ô", theme, theme.get('accent', '#00ff41'))
        
        if 'steps' in result:
            self._add_result_styled_row(result_content, '🔄 Số bước duyệt', 
                                       f"{result['steps']}", theme, theme.get('warning', '#ffb400'))
        
        if 'time' in result:
            self._add_result_styled_row(result_content, '⏱️ Thời gian', 
                                       f"{result['time']:.4f}s", theme, theme.get('info', '#00d4ff'))
        
        if 'visited_count' in result:
            self._add_result_styled_row(result_content, '✓ Ô đã thăm', 
                                       f"{result['visited_count']}", theme, theme.get('accent3', '#f72585'))
        
        # Update scroll region
        self.after(50, self._update_scroll_region)
    
    def _add_result_styled_row(self, parent, label, value, theme, value_color):
        """Thêm dòng kết quả với màu sắc đặc biệt"""
        row = tk.Frame(parent, bg=theme.get('card_bg', '#1e2848'))
        row.pack(fill='x', pady=3)
        
        # Left: label
        tk.Label(row, text=label, bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('text_dim', '#c9ada7'), font=('Arial', 10),
                anchor='w').pack(side='left')
        
        # Right: value with accent
        value_frame = tk.Frame(row, bg=theme.get('section_bg', '#141a30'), relief='flat')
        value_frame.pack(side='right')
        
        tk.Label(value_frame, text=f" {value} ", bg=theme.get('section_bg', '#141a30'), 
                fg=value_color, font=('Consolas', 10, 'bold')).pack(padx=5, pady=2)
    
    def show_comparison(self, comparison: dict):
        """
        Hiển thị bảng so sánh các thuật toán với styled cards
        
        Args:
            comparison: Dict chứa dữ liệu so sánh
        """
        self.clear()
        theme = self.get_theme()
        
        # === HEADER CARD ===
        header_card, header_content = self._create_card(self.content_frame, None, 
                                                        theme.get('accent2', '#00d4ff'))
        header_card.pack(fill='x', padx=5, pady=(5, 3))
        
        header_row = tk.Frame(header_content, bg=theme.get('card_bg', '#1e2848'))
        header_row.pack(fill='x')
        
        tk.Label(header_row, text='📊', bg=theme.get('card_bg', '#1e2848'), 
                font=('Arial', 14)).pack(side='left')
        tk.Label(header_row, text=' SO SÁNH THUẬT TOÁN', bg=theme.get('card_bg', '#1e2848'), 
                fg=theme.get('accent2', '#00d4ff'), font=('Arial', 12, 'bold')).pack(side='left')
        
        # === ALGORITHM CARDS ===
        algo_colors = {
            'BFS': theme.get('info', '#00d4ff'),
            'Dijkstra': theme.get('warning', '#ffb400'),
            'A*': theme.get('success', '#00ff41')
        }
        
        algo_icons = {'BFS': '🔵', 'Dijkstra': '🟡', 'A*': '🟢'}
        
        for algo_name, data in comparison.items():
            accent = algo_colors.get(algo_name, theme.get('accent', '#00ff41'))
            icon = algo_icons.get(algo_name, '⚪')
            
            algo_card, algo_content = self._create_card(self.content_frame, f"{icon} {algo_name}", accent)
            algo_card.pack(fill='x', padx=5, pady=3)
            
            # Data rows
            for key, value in data.items():
                row = tk.Frame(algo_content, bg=theme.get('card_bg', '#1e2848'))
                row.pack(fill='x', pady=1)
                
                tk.Label(row, text=f"{key}:", bg=theme.get('card_bg', '#1e2848'), 
                        fg=theme.get('text_dim', '#c9ada7'), font=('Consolas', 9),
                        width=13, anchor='w').pack(side='left')
                tk.Label(row, text=str(value), bg=theme.get('card_bg', '#1e2848'), 
                        fg=theme.get('text', '#ffffff'), font=('Consolas', 9, 'bold')).pack(side='left')
        
        # Update scroll region
        self.after(50, self._update_scroll_region)
    
    def _add_info_row(self, label: str, value: str, large: bool = False):
        """Thêm một dòng thông tin"""
        row = tk.Frame(self.content_frame, bg='#16213e')
        row.pack(fill='x', padx=10, pady=3)
        
        font_size = 11 if large else 10
        
        label_widget = tk.Label(row, text=label, bg='#16213e', fg='#c9ada7', 
                               font=('Consolas', font_size), anchor='w')
        label_widget.pack(side='left')
        
        value_widget = tk.Label(row, text=value, bg='#16213e', fg='#ffffff', 
                               font=('Consolas', font_size, 'bold'), anchor='w')
        value_widget.pack(side='left', padx=5)
    
    def _add_list(self, title: str, items: list, color: str):
        """Thêm một danh sách có bullet points"""
        title_label = tk.Label(self.content_frame, text=title, 
                             bg='#16213e', fg=color, font=('Arial', 10, 'bold'))
        title_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        for item in items:
            item_label = tk.Label(self.content_frame, text=f"  • {item}", 
                                bg='#16213e', fg='#ffffff', font=('Arial', 9), 
                                wraplength=280, justify='left')
            item_label.pack(anchor='w', padx=15, pady=2)
        
        # Update scroll region sau khi thêm content
        self.after(50, self._update_scroll_region)
    
    def _update_scroll_region(self):
        """Cập nhật scroll region sau khi thay đổi content"""
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        # Bind scroll cho các widget mới
        def _bind_scroll(widget):
            def _on_mousewheel(event):
                delta = -1 if event.delta > 0 else 1
                self._scroll_velocity = delta * 3
                if not self._scroll_animating:
                    self._scroll_animating = True
                    self._smooth_scroll_frame()
            widget.bind("<MouseWheel>", _on_mousewheel)
            for child in widget.winfo_children():
                _bind_scroll(child)
        _bind_scroll(self.content_frame)
    
    def _smooth_scroll_frame(self):
        """Frame animation cho smooth scroll"""
        if not self._scroll_animating:
            return
        if abs(self._scroll_velocity) > 0.3:
            self.scroll_canvas.yview_scroll(int(self._scroll_velocity), "units")
            self._scroll_velocity *= 0.85
            self.after(16, self._smooth_scroll_frame)
        else:
            self._scroll_velocity = 0
            self._scroll_animating = False
    
    def clear(self):
        """Xóa nội dung với smooth transition"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Reset scroll position
        self.scroll_canvas.yview_moveto(0)
        # Update scroll region
        self.after(50, lambda: self.scroll_canvas.configure(
            scrollregion=self.scroll_canvas.bbox("all") or (0, 0, 280, 100)))
