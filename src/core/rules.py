class FutoshikiRules:
    """
    Lớp này chịu trách nhiệm kiểm tra tính hợp lệ của một trạng thái lưới (Grid) 
    dựa trên các luật của trò chơi Futoshiki.
    """

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

    def get_inequality_chain_sizes(self, grid):
        """
        Trả về danh sách kích thước của các chuỗi bất đẳng thức chưa được giải quyết
        (những cụm ô có liên kết với nhau bằng dấu < hoặc >, và ít nhất 1 ô trong cạnh đó còn trống).
        """
        visited = set()
        chain_sizes = []
        
        for i in range(self.n):
            for j in range(self.n):
                if (i, j) not in visited:
                    # Chỉ bắt đầu loang nếu ô này thực sự dính líu tới một ràng buộc chưa chốt
                    if self._is_part_of_unresolved_constraint(grid, i, j):
                        size = self._spread_unresolved(grid, visited, i, j)
                        if size > 1: # Một chuỗi thì phải có từ 2 ô trở lên
                            chain_sizes.append(size)
                            
        return chain_sizes

    def _is_part_of_unresolved_constraint(self, grid, r, c):
        """Kiểm tra ô (r, c) có kết nối với ô lân cận bằng ràng buộc mà 1 trong 2 ô là 0 không."""
        # Left
        if c > 0 and self.horiz_const[r][c - 1] != 0:
            if grid[r][c] == 0 or grid[r][c - 1] == 0: return True
        # Right
        if c < self.n - 1 and self.horiz_const[r][c] != 0:
            if grid[r][c] == 0 or grid[r][c + 1] == 0: return True
        # Top
        if r > 0 and self.vert_const[r - 1][c] != 0:
            if grid[r][c] == 0 or grid[r - 1][c] == 0: return True
        # Bottom
        if r < self.n - 1 and self.vert_const[r][c] != 0:
            if grid[r][c] == 0 or grid[r + 1][c] == 0: return True
            
        return False

    def _spread_unresolved(self, grid, visited, start_r, start_c):
        """
        Dùng BFS loang ra để đếm số lượng ô nằm trong cụm ràng buộc chưa giải quyết.
        """
        queue = [(start_r, start_c)]
        visited.add((start_r, start_c))
        size = 0

        while queue:
            r, c = queue.pop(0)
            size += 1

            # Left
            if c > 0 and self.horiz_const[r][c - 1] != 0:
                if (r, c - 1) not in visited and (grid[r][c] == 0 or grid[r][c - 1] == 0):
                    visited.add((r, c - 1))
                    queue.append((r, c - 1))
            # Right
            if c < self.n - 1 and self.horiz_const[r][c] != 0:
                if (r, c + 1) not in visited and (grid[r][c] == 0 or grid[r][c + 1] == 0):
                    visited.add((r, c + 1))
                    queue.append((r, c + 1))
            # Top
            if r > 0 and self.vert_const[r - 1][c] != 0:
                if (r - 1, c) not in visited and (grid[r][c] == 0 or grid[r - 1][c] == 0):
                    visited.add((r - 1, c))
                    queue.append((r - 1, c))
            # Bottom
            if r < self.n - 1 and self.vert_const[r][c] != 0:
                if (r + 1, c) not in visited and (grid[r][c] == 0 or grid[r + 1][c] == 0):
                    visited.add((r + 1, c))
                    queue.append((r + 1, c))

        return size