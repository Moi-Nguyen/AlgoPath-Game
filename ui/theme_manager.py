"""
==============================================================================
THEME MANAGER - QUẢN LÝ GIAO DIỆN MÀU SẮC
==============================================================================

Mô tả:
    Class ThemeManager quản lý các theme màu sắc cho giao diện game.
    Hỗ trợ 2 theme chính: Black (tối) và White (sáng).

Cấu trúc màu sắc:
    - Background: Màu nền các panel
    - Text: Màu chữ với các mức độ sáng/tối
    - Accent: Màu nhấn, highlight
    - UI Elements: Button, separator, border
    - Maze colors: Màu các thành phần mê cung
    - Status: Success, warning, error, info

Tích hợp với Tkinter:
    - Sử dụng mã màu hex (#RRGGBB)
    - Hỗ trợ widget.config(bg=theme['bg'])
==============================================================================
"""


class ThemeManager:
    """
    Lớp ThemeManager quản lý bảng màu cho giao diện game.
    
    Attributes:
        themes: Dictionary chứa các theme và màu sắc
        current_theme: Tên theme đang sử dụng
    """
    
    def __init__(self):
        """
        Khởi tạo Theme Manager với bảng màu đầy đủ.
        
        Mặc định sử dụng theme 'Black' (giao diện tối).
        """
        self.themes = {
            # ===== THEME TỐI (HACKER STYLE) =====
            'Black': {
                # Background colors
                'bg': '#000000',
                'panel': '#0a0a0a',
                'panel_dark': '#050505',
                'panel_light': '#151515',
                
                # Text colors
                'text': '#ffffff',
                'text_dim': '#888888',
                'text_muted': '#555555',
                
                # Accent colors
                'accent': '#00ff00',
                'accent2': '#00ffff',
                'accent3': '#ff0000',
                
                # UI Elements
                'button': '#1a1a1a',
                'button_hover': '#2a2a2a',
                'button_active': '#3a3a3a',
                
                # Separators & Borders
                'separator': '#00ff00',
                'separator_dim': '#004400',
                'border': '#333333',
                'border_light': '#444444',
                'border_accent': '#00ff00',
                
                # Cards & Sections
                'card_bg': '#0d0d0d',
                'card_border': '#1a1a1a',
                'card_header': '#111111',
                'section_bg': '#080808',
                
                # Status colors
                'success': '#00ff00',
                'warning': '#ffff00',
                'error': '#ff0000',
                'info': '#00ffff',
                
                # Maze colors
                'wall': '#1a1a1a',
                'path': '#000000',
                'start': '#00ff00',
                'exit': '#ff0000',
                'player': '#00ffff',
                'enemy': '#ffff00',
                'solution': '#ff00ff',
                'visited': '#333333',
                'current': '#ff6600',
                
                # Gradients (start, end)
                'gradient_primary': ('#00ff00', '#00aa00'),
                'gradient_secondary': ('#00ffff', '#0088aa'),
            },
            'White': {
                # Background colors
                'bg': '#ffffff',
                'panel': '#f5f5f5',
                'panel_dark': '#e8e8e8',
                'panel_light': '#fafafa',
                
                # Text colors
                'text': '#1a1a1a',
                'text_dim': '#666666',
                'text_muted': '#999999',
                
                # Accent colors
                'accent': '#0066cc',
                'accent2': '#00aa00',
                'accent3': '#cc0000',
                
                # UI Elements
                'button': '#e0e0e0',
                'button_hover': '#d0d0d0',
                'button_active': '#c0c0c0',
                
                # Separators & Borders
                'separator': '#0066cc',
                'separator_dim': '#a0c4e8',
                'border': '#d0d0d0',
                'border_light': '#e0e0e0',
                'border_accent': '#0066cc',
                
                # Cards & Sections
                'card_bg': '#ffffff',
                'card_border': '#e0e0e0',
                'card_header': '#f0f0f0',
                'section_bg': '#fafafa',
                
                # Status colors
                'success': '#00aa00',
                'warning': '#cc8800',
                'error': '#cc0000',
                'info': '#0066cc',
                
                # Maze colors
                'wall': '#cccccc',
                'path': '#ffffff',
                'start': '#00aa00',
                'exit': '#cc0000',
                'player': '#0066cc',
                'enemy': '#ff9900',
                'solution': '#9933ff',
                'visited': '#e0e0e0',
                'current': '#ff6600',
                
                # Gradients
                'gradient_primary': ('#0066cc', '#004499'),
                'gradient_secondary': ('#00aa00', '#007700'),
            },
            'Galaxy': {
                # Background colors
                'bg': '#0a0015',
                'panel': '#1a0030',
                'panel_dark': '#0d0020',
                'panel_light': '#250045',
                
                # Text colors
                'text': '#e0d0ff',
                'text_dim': '#9080b0',
                'text_muted': '#6050a0',
                
                # Accent colors
                'accent': '#ff00ff',
                'accent2': '#00ffff',
                'accent3': '#ffff00',
                
                # UI Elements
                'button': '#2a1050',
                'button_hover': '#3a2060',
                'button_active': '#4a3070',
                
                # Separators & Borders
                'separator': '#ff00ff',
                'separator_dim': '#660066',
                'border': '#3a2060',
                'border_light': '#4a3070',
                'border_accent': '#ff00ff',
                
                # Cards & Sections
                'card_bg': '#150025',
                'card_border': '#2a1050',
                'card_header': '#200040',
                'section_bg': '#120020',
                
                # Status colors
                'success': '#00ff88',
                'warning': '#ffaa00',
                'error': '#ff0088',
                'info': '#00ddff',
                
                # Maze colors
                'wall': '#1a0030',
                'path': '#0a0015',
                'start': '#00ff88',
                'exit': '#ff0088',
                'player': '#00ddff',
                'enemy': '#ffaa00',
                'solution': '#ff00ff',
                'visited': '#4a3070',
                'current': '#ffff00',
                
                # Gradients
                'gradient_primary': ('#ff00ff', '#aa00aa'),
                'gradient_secondary': ('#00ffff', '#00aaaa'),
            },
            'Dark': {
                # Background colors
                'bg': '#1a1a2e',
                'panel': '#16213e',
                'panel_dark': '#0f3460',
                'panel_light': '#1e2a4a',
                
                # Text colors
                'text': '#ffffff',
                'text_dim': '#c9ada7',
                'text_muted': '#8a8a9a',
                
                # Accent colors
                'accent': '#00ff41',
                'accent2': '#00d4ff',
                'accent3': '#f72585',
                
                # UI Elements
                'button': '#7b2cbf',
                'button_hover': '#9b4cdf',
                'button_active': '#5b1c9f',
                
                # Separators & Borders
                'separator': '#00ff41',
                'separator_dim': '#0a5a1a',
                'border': '#2a3a5e',
                'border_light': '#3a4a6e',
                'border_accent': '#00ff41',
                
                # Cards & Sections
                'card_bg': '#1e2848',
                'card_border': '#2a3858',
                'card_header': '#243050',
                'section_bg': '#141a30',
                
                # Status colors
                'success': '#00ff41',
                'warning': '#ffb400',
                'error': '#ff0080',
                'info': '#00d4ff',
                
                # Maze colors
                'wall': '#0f3460',
                'path': '#16213e',
                'start': '#00ff41',
                'exit': '#ff0080',
                'player': '#00d4ff',
                'enemy': '#ffb400',
                'solution': '#7b2cbf',
                'visited': '#c9ada7',
                'current': '#f72585',
                
                # Gradients
                'gradient_primary': ('#00ff41', '#00aa2a'),
                'gradient_secondary': ('#00d4ff', '#0099bb'),
            },
            'Ocean': {
                # Background colors
                'bg': '#0a192f',
                'panel': '#112240',
                'panel_dark': '#0a1628',
                'panel_light': '#1a3050',
                
                # Text colors
                'text': '#ccd6f6',
                'text_dim': '#8892b0',
                'text_muted': '#5a6380',
                
                # Accent colors
                'accent': '#64ffda',
                'accent2': '#57cbff',
                'accent3': '#ff6b9d',
                
                # UI Elements
                'button': '#1d4e89',
                'button_hover': '#2d5e99',
                'button_active': '#0d3e79',
                
                # Separators & Borders
                'separator': '#64ffda',
                'separator_dim': '#1a5a4a',
                'border': '#233554',
                'border_light': '#334564',
                'border_accent': '#64ffda',
                
                # Cards & Sections
                'card_bg': '#152238',
                'card_border': '#233554',
                'card_header': '#1a2a48',
                'section_bg': '#0d1a2d',
                
                # Status colors
                'success': '#64ffda',
                'warning': '#ffd93d',
                'error': '#ff6b9d',
                'info': '#57cbff',
                
                # Maze colors
                'wall': '#112240',
                'path': '#0a192f',
                'start': '#64ffda',
                'exit': '#ff6b9d',
                'player': '#57cbff',
                'enemy': '#ffd93d',
                'solution': '#c792ea',
                'visited': '#334564',
                'current': '#ff9f43',
                
                # Gradients
                'gradient_primary': ('#64ffda', '#3eccaa'),
                'gradient_secondary': ('#57cbff', '#3099cc'),
            },
            'Sunset': {
                # Background colors
                'bg': '#1a1423',
                'panel': '#2d1f3d',
                'panel_dark': '#1a1225',
                'panel_light': '#3d2f4d',
                
                # Text colors
                'text': '#ffeaa7',
                'text_dim': '#dda0a0',
                'text_muted': '#aa7080',
                
                # Accent colors
                'accent': '#fd79a8',
                'accent2': '#fdcb6e',
                'accent3': '#74b9ff',
                
                # UI Elements
                'button': '#6c3483',
                'button_hover': '#8c4493',
                'button_active': '#5c2473',
                
                # Separators & Borders
                'separator': '#fd79a8',
                'separator_dim': '#6d3948',
                'border': '#4d3f5d',
                'border_light': '#5d4f6d',
                'border_accent': '#fd79a8',
                
                # Cards & Sections
                'card_bg': '#2a1a35',
                'card_border': '#3d2f4d',
                'card_header': '#352545',
                'section_bg': '#201530',
                
                # Status colors
                'success': '#00cec9',
                'warning': '#fdcb6e',
                'error': '#ff7675',
                'info': '#74b9ff',
                
                # Maze colors
                'wall': '#2d1f3d',
                'path': '#1a1423',
                'start': '#00cec9',
                'exit': '#ff7675',
                'player': '#74b9ff',
                'enemy': '#fdcb6e',
                'solution': '#fd79a8',
                'visited': '#4d3f5d',
                'current': '#ff9f43',
                
                # Gradients
                'gradient_primary': ('#fd79a8', '#cc5988'),
                'gradient_secondary': ('#fdcb6e', '#ccaa5e'),
            }
        }
        # Mặc định sử dụng theme Dark
        self.current_theme = 'Dark'
    
    def get_theme(self, theme_name=None):
        """
        Lấy bảng màu của theme.
        
        Args:
            theme_name: Tên theme cần lấy (None = theme hiện tại)
            
        Returns:
            Dictionary chứa các màu sắc của theme
        """
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes['Dark'])
    
    def set_theme(self, theme_name):
        """
        Đổi theme hiện tại.
        
        Args:
            theme_name: Tên theme muốn đổi sang
            
        Returns:
            True nếu đổi thành công, False nếu theme không tồn tại
        """
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_theme_names(self):
        """
        Lấy danh sách tên các theme có sẵn.
        
        Returns:
            List các tên theme: ['Black', 'White', 'Galaxy', 'Dark', 'Ocean', 'Sunset']
        """
        return list(self.themes.keys())
    
    def get_color(self, color_key, theme_name=None):
        """
        Lấy một màu cụ thể từ theme.
        
        Args:
            color_key: Khóa màu cần lấy (vd: 'bg', 'text', 'accent')
            theme_name: Tên theme (None = theme hiện tại)
            
        Returns:
            Mã màu hex (vd: '#ffffff')
        """
        theme = self.get_theme(theme_name)
        return theme.get(color_key, '#ffffff')
