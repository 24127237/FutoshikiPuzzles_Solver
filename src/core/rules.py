class FutoshikiRules:
    """
    Lớp này chịu trách nhiệm kiểm tra tính hợp lệ của một trạng thái lưới (Grid) 
    dựa trên các luật của trò chơi Futoshiki.
    """
    def __init__(self, n, horizontal_constraints, vertical_constraints):
        self.n = n
        self.horiz_const = horizontal_constraints
        self.vert_const = vertical_constraints

    def is_valid(self, grid):
        """
        Kiểm tra xem lưới hiện tại (có thể chưa điền hết) có vi phạm luật nào không.
        Trả về True nếu hợp lệ (hoặc chưa vi phạm), False nếu sai luật.
        """
        if not self._check_uniqueness(grid):
            return False
        if not self._check_horizontal_inequalities(grid):
            return False
        if not self._check_vertical_inequalities(grid):
            return False
        return True

    def is_solved(self, grid):
        """
        Kiểm tra xem bài toán đã được giải xong chưa (Đã điền kín và hợp lệ).
        """
        # Kiểm tra xem còn ô trống (số 0) không
        for i in range(self.n):
            for j in range(self.n):
                if grid[i][j] == 0:
                    return False
        
        # Nếu đã điền kín, kiểm tra xem có hợp lệ không
        return self.is_valid(grid)

    def _check_uniqueness(self, grid):
        """Kiểm tra tính duy nhất của các số trên hàng và cột."""
        # Kiểm tra hàng
        for i in range(self.n):
            row_vals = [val for val in grid[i] if val != 0]
            if len(row_vals) != len(set(row_vals)):
                return False

        # Kiểm tra cột
        for j in range(self.n):
            col_vals = [grid[i][j] for i in range(self.n) if grid[i][j] != 0]
            if len(col_vals) != len(set(col_vals)):
                return False

        return True

    def _check_horizontal_inequalities(self, grid):
        """
        Kiểm tra ràng buộc ngang.
        1: Trái < Phải
        -1: Trái > Phải
        0: Không có ràng buộc
        """
        for i in range(self.n):
            for j in range(self.n - 1):
                const = self.horiz_const[i][j]
                val_left = grid[i][j]
                val_right = grid[i][j+1]

                # Chỉ kiểm tra khi cả 2 ô đã được điền số
                if const != 0 and val_left != 0 and val_right != 0:
                    if const == 1 and not (val_left < val_right):
                        return False
                    if const == -1 and not (val_left > val_right):
                        return False
        return True

    def _check_vertical_inequalities(self, grid):
        """
        Kiểm tra ràng buộc dọc.
        1: Trên < Dưới
        -1: Trên > Dưới
        0: Không có ràng buộc
        """
        for i in range(self.n - 1):
            for j in range(self.n):
                const = self.vert_const[i][j]
                val_top = grid[i][j]
                val_bot = grid[i+1][j]

                # Chỉ kiểm tra khi cả 2 ô đã được điền số
                if const != 0 and val_top != 0 and val_bot != 0:
                    if const == 1 and not (val_top < val_bot):
                        return False
                    if const == -1 and not (val_top > val_bot):
                        return False
        return True