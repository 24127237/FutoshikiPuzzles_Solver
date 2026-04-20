import copy

class BruteForceSolver:
    def __init__(self, rules):
        """
        Khởi tạo solver với bộ luật đã được định nghĩa.
        """
        self.rules = rules

    def solve(self, grid):
        """
        Hàm giải chính bằng vét cạn đệ quy.
        Trả về grid đã giải xong, hoặc None nếu không có nghiệm.
        """
        n = len(grid)
        
        # 1. Tìm ô trống đầu tiên (duyệt tuyến tính)
        empty_cell = None
        for i in range(n):
            for j in range(n):
                if grid[i][j] == 0:
                    empty_cell = (i, j)
                    break
            if empty_cell:
                break
                
        # 2. Base case: Nếu không còn ô trống, kiểm tra xem bảng có hợp lệ không
        if not empty_cell:
            if self.rules.is_solved(grid):
                return grid
            return None

        r, c = empty_cell
        
        # 3. Thử điền các giá trị từ 1 đến N
        for val in range(1, n + 1):
            grid[r][c] = val
            
            # Pruning nhẹ: Chỉ tiếp tục đi sâu nếu cấu hình hiện tại chưa vi phạm luật
            if self.rules.is_valid(grid):
                result = self.solve(grid)
                if result is not None:
                    return result  # Trả về ngay khi tìm thấy 1 nghiệm đúng
                    
            # Backtrack: Hủy bỏ giá trị nếu đi vào ngõ cụt
            grid[r][c] = 0
            
        return None