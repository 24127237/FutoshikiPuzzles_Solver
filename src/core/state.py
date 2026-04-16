import copy
import collections

class State:
    """
    Đại diện cho trạng thái của một bàn cờ Futoshiki tại một thời điểm.
    Được sử dụng chủ yếu cho các thuật toán tìm kiếm (A*, Backtracking).
    """
    def __init__(self, n, grid, rules=None, skip_init=False):
        self.n = n
        # self.grid = copy.deepcopy(grid) # Deepcopy để không làm hỏng bảng gốc
        self.grid = [row[:] for row in grid]
        
        if not skip_init:
            mask_all = (2 << self.n) - 2 # Bật các bit từ 1 đến N
            self.possible_values = [[mask_all] * self.n for _ in range(self.n)]
            
            for i in range(self.n):
                for j in range(self.n):
                    if self.grid[i][j] != 0:
                        val = self.grid[i][j]
                        self.possible_values[i][j] = 1 << val
                        mask = ~(1 << val)
                        for k in range(self.n):
                            if k != j: self.possible_values[i][k] &= mask
                            if k != i: self.possible_values[k][j] &= mask

            if rules:
                self._ac3_propagate(rules, None)

    def assign(self, row, col, value, rules=None):
        """
        Điền một số vào ô và tự động cập nhật (thu hẹp) miền giá trị với bitmask và AC3.
        Trả về False nếu phát hiện vi phạm (domain bị thu hẹp về 0).
        """
        self.grid[row][col] = value
        self.possible_values[row][col] = 1 << value
        
        changed_cells = [(row, col)]
        mask = ~(1 << value)
        # Xóa 'value' khỏi các ô cùng hàng và cùng cột
        for k in range(self.n):
            if k != col:
                old_val, new_val = self.possible_values[row][k], self.possible_values[row][k] & mask
                if old_val != new_val:
                    if new_val == 0: return False
                    self.possible_values[row][k] = new_val
                    changed_cells.append((row, k))
            if k != row:
                old_val, new_val = self.possible_values[k][col], self.possible_values[k][col] & mask
                if old_val != new_val:
                    if new_val == 0: return False
                    self.possible_values[k][col] = new_val
                    changed_cells.append((k, col))
        
        if rules:
            return self._ac3_propagate(rules, changed_cells)
        return True

    def _ac3_propagate(self, rules, changed_cells=None):
        """
        Propagate constraints using AC3 algorithm.
        Gọt bớt miền giá trị của các ô kề nhau nếu vi phạm dấu < hoặc >.
        """
        queue = collections.deque()
        in_queue = set()
        
        def add_to_queue(arc):
            if arc not in in_queue:
                queue.append(arc)
                in_queue.add(arc)

        if changed_cells is None:
            # Lúc init: Nạp toàn bộ các ràng buộc có sẵn vào Queue
            for r in range(self.n):
                for c in range(self.n):
                    if c < self.n - 1 and rules.horiz_const[r][c] != 0: add_to_queue((r, c, r, c + 1, rules.horiz_const[r][c]))
                    if r < self.n - 1 and rules.vert_const[r][c] != 0: add_to_queue((r, c, r + 1, c, rules.vert_const[r][c]))
        else:
            # Lúc assign: Chỉ cần nạp các ràng buộc liên quan đến ô vừa thay đổi
            for r, c in changed_cells:
                # Left
                if c > 0 and rules.horiz_const[r][c - 1] != 0: add_to_queue((r, c - 1, r, c, rules.horiz_const[r][c - 1]))
                # Right
                if c < self.n - 1 and rules.horiz_const[r][c] != 0: add_to_queue((r, c, r, c + 1, rules.horiz_const[r][c]))
                # Top
                if r > 0 and rules.vert_const[r - 1][c] != 0: add_to_queue((r - 1, c, r, c, rules.vert_const[r - 1][c]))
                # Bottom
                if r < self.n - 1 and rules.vert_const[r][c] != 0: add_to_queue((r, c, r + 1, c, rules.vert_const[r][c]))

        # Vận hành AC-3 chuẩn
        while queue:
            arc = queue.popleft()
            in_queue.remove(arc)
            r1, c1, r2, c2, const = arc

            revised = False
            if const == 1:   # Trái/Trên < Phải/Dưới
                revised = self._revise(r1, c1, r2, c2)
            elif const == -1: # Trái/Trên > Phải/Dưới
                revised = self._revise(r2, c2, r1, c1)

            if revised == -1:
                return False

            if revised:
                # Nếu _revise làm hẹp domain, nạp lại láng giềng có bất đẳng thức
                for r, c in [(r1, c1), (r2, c2)]:
                    # Left
                    if c > 0 and rules.horiz_const[r][c - 1] != 0: add_to_queue((r, c - 1, r, c, rules.horiz_const[r][c - 1]))
                    # Right
                    if c < self.n - 1 and rules.horiz_const[r][c] != 0: add_to_queue((r, c, r, c + 1, rules.horiz_const[r][c]))
                    # Top
                    if r > 0 and rules.vert_const[r - 1][c] != 0: add_to_queue((r - 1, c, r, c, rules.vert_const[r - 1][c]))
                    # Bottom
                    if r < self.n - 1 and rules.vert_const[r][c] != 0: add_to_queue((r, c, r + 1, c, rules.vert_const[r][c]))
        return True

    def _revise(self, r1, c1, r2, c2):
        """Xóa giá trị vô lý giữa 2 ô (Ô 1 < Ô 2). Trả về True nếu có domain bị thu hẹp bằng Bitmask, -1 nếu vi phạm domain."""
        dom_a, dom_b = self.possible_values[r1][c1], self.possible_values[r2][c2]
        if not dom_a or not dom_b: return -1
        
        revised = False
        max_b = dom_b.bit_length() - 1
        mask_a = (1 << max_b) - 1
        new_a = dom_a & mask_a
        if new_a != dom_a:
            self.possible_values[r1][c1] = new_a
            if new_a == 0: return -1
            revised = True
                
        if new_a:
            min_a = (new_a & -new_a).bit_length() - 1
            mask_b = ~((1 << (min_a + 1)) - 1)
            new_b = dom_b & mask_b
            if new_b != dom_b:
                self.possible_values[r2][c2] = new_b
                if new_b == 0: return -1
                revised = True
        return revised

    def get_empty_cells(self):
        """
        Lấy danh sách tọa độ các ô còn trống.
        """
        empty_cells = []
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        return empty_cells

    def get_mrv_cell(self):
        """
        Minimum Remaining Values (MRV) Heuristic bằng Bitmask.
        """
        min_len = self.n + 1
        best_cell = None
        
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    curr_len = self.possible_values[i][j].bit_count()
                    if curr_len < min_len:
                        min_len = curr_len
                        best_cell = (i, j)
                        if min_len == 1:
                            return best_cell
        return best_cell

    def clone(self):
        """
        Tạo một bản sao của trạng thái hiện tại cực kỳ tĩnh và siêu tốc qua mảng 2D.
        """
        new_grid = [row[:] for row in self.grid]
        new_state = State(self.n, new_grid, skip_init=True)
        new_state.possible_values = [row[:] for row in self.possible_values]
        return new_state

    def get_valid_neighbors(self, rules):
        """
        Sinh ra các trạng thái (nhánh) tiếp theo hợp lệ từ trạng thái hiện tại.
        """
        neighbors = []
        cell = self.get_mrv_cell()
        if not cell:
            return neighbors
            
        row, col = cell
        dom = self.possible_values[row][col]
        for val in range(1, self.n + 1):
            if dom & (1 << val):
                new_state = self.clone()
                is_ok = new_state.assign(row, col, val, rules)
                if is_ok:
                    neighbors.append(new_state)
        return neighbors