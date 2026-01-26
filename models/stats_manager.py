"""
==============================================================================
STATS MANAGER - QUẢN LÝ THỐNG KÊ GAME
==============================================================================

Mô tả:
    Class StatsManager quản lý việc lưu trữ và truy xuất thống kê game.
    Dữ liệu được lưu vào file JSON để bảo toàn giữa các phiên chơi.

Chức năng:
    - Ghi nhận kết quả mỗi ván game (thắng/thua)
    - Lưu kỷ lục (thời gian, số bước, điểm cao nhất)
    - Quản lý bảng xếp hạng (top 10)
    - Tính tỷ lệ thắng

Cấu trúc dữ liệu JSON:
    {
        "total_games": int,      - Tổng số ván đã chơi
        "wins": int,             - Số ván thắng
        "losses": int,           - Số ván thua
        "best_time": float,      - Thời gian tốt nhất (giây)
        "best_steps": int,       - Số bước ít nhất
        "best_score": int,       - Điểm cao nhất
        "leaderboard": [...]     - Bảng xếp hạng top 10
    }
==============================================================================
"""

import json
import os
from datetime import datetime


class StatsManager:
    """
    Lớp StatsManager quản lý thống kê và bảng xếp hạng game.
    
    Attributes:
        stats_file: Đường dẫn file JSON lưu thống kê
        stats: Dictionary chứa toàn bộ thống kê
    """
    
    def __init__(self, stats_file='game_stats.json'):
        """
        Khởi tạo Stats Manager.
        
        Args:
            stats_file: Tên file JSON lưu thống kê (mặc định 'game_stats.json')
        """
        self.stats_file = stats_file
        # Load thống kê từ file (nếu có)
        self.stats = self.load_stats()
    
    def load_stats(self):
        """
        Load thống kê từ file JSON.
        
        Returns:
            Dictionary chứa thống kê, hoặc giá trị mặc định nếu file không tồn tại
        """
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                # File bị lỗi, trả về mặc định
                pass
        
        # Giá trị mặc định cho người chơi mới
        return {
            'total_games': 0,      # Tổng số ván
            'wins': 0,             # Số ván thắng
            'losses': 0,           # Số ván thua
            'best_time': None,     # Thời gian tốt nhất
            'best_steps': None,    # Số bước ít nhất
            'best_score': 0,       # Điểm cao nhất
            'leaderboard': []      # Bảng xếp hạng
        }
    
    def save_stats(self):
        """
        Lưu thống kê vào file JSON.
        
        Xử lý exception để tránh crash nếu không ghi được file.
        """
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                # ensure_ascii=False để hỗ trợ tiếng Việt
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi khi lưu thống kê: {e}")
    
    def record_game(self, won, time_seconds, steps, difficulty, score):
        """
        Ghi nhận kết quả một ván game.
        
        Cập nhật:
            - Tổng số ván và số thắng/thua
            - Kỷ lục (nếu là ván thắng)
            - Bảng xếp hạng (top 10)
        
        Args:
            won: True nếu thắng, False nếu thua
            time_seconds: Thời gian chơi (giây)
            steps: Số bước đi
            difficulty: Độ khó (Easy/Medium/Hard)
            score: Điểm số đạt được
        """
        # Tăng tổng số ván
        self.stats['total_games'] += 1
        
        if won:
            # Cập nhật số ván thắng
            self.stats['wins'] += 1
            
            # ===== CẬP NHẬT KỶ LỤC =====
            # Thời gian tốt nhất (càng thấp càng tốt)
            if self.stats['best_time'] is None or time_seconds < self.stats['best_time']:
                self.stats['best_time'] = time_seconds
            
            # Số bước ít nhất (càng thấp càng tốt)
            if self.stats['best_steps'] is None or steps < self.stats['best_steps']:
                self.stats['best_steps'] = steps
            
            # Điểm cao nhất (càng cao càng tốt)
            if score > self.stats['best_score']:
                self.stats['best_score'] = score
            
            # ===== THÊM VÀO BẢNG XẾP HẠNG =====
            entry = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'time': time_seconds,
                'steps': steps,
                'difficulty': difficulty,
                'score': score
            }
            self.stats['leaderboard'].append(entry)
            
            # Sắp xếp theo điểm (giảm dần) và giữ top 10
            self.stats['leaderboard'] = sorted(
                self.stats['leaderboard'], 
                key=lambda x: x['score'], 
                reverse=True
            )[:10]
        else:
            # Cập nhật số ván thua
            self.stats['losses'] += 1
        
        # Lưu vào file
        self.save_stats()
    
    def get_win_rate(self):
        """
        Tính tỷ lệ thắng.
        
        Công thức: win_rate = (wins / total_games) * 100
        
        Returns:
            Tỷ lệ thắng (%) hoặc 0 nếu chưa chơi ván nào
        """
        if self.stats['total_games'] == 0:
            return 0
        return (self.stats['wins'] / self.stats['total_games']) * 100
    
    def get_summary(self):
        """
        Lấy tóm tắt thống kê để hiển thị.
        
        Returns:
            Dictionary chứa các thông tin thống kê chính
        """
        return {
            'total': self.stats['total_games'],      # Tổng số ván
            'wins': self.stats['wins'],              # Số thắng
            'losses': self.stats['losses'],          # Số thua
            'win_rate': self.get_win_rate(),         # Tỷ lệ thắng (%)
            'best_time': self.stats['best_time'],    # Thời gian tốt nhất
            'best_steps': self.stats['best_steps'],  # Số bước ít nhất
            'best_score': self.stats['best_score']   # Điểm cao nhất
        }
