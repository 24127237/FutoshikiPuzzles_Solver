import copy

class State:
    """
    Đại diện cho trạng thái của một bàn cờ Futoshiki tại một thời điểm.
    Được sử dụng chủ yếu cho các thuật toán tìm kiếm (A*, Backtracking).
    """
    def __init__(self, n, grid):
        self.n = n
        self.grid = copy.deepcopy(grid) # Deepcopy để không làm hỏng bảng gốc
        
        # possible_values[i][j] lưu danh sách các số có thể điền vào ô (i, j)
        self.possible_values = self._init_possible_values()

    def _init_possible_values(self):
        """
        Khởi tạo miền giá trị cho từng ô.
        Nếu ô đã có số, miền giá trị chỉ chứa số đó.
        Nếu ô trống (0), miền giá trị ban đầu là [1, 2, ..., N].
        """
        domains = []
        for i in range(self.n):
            row_domains = []
            for j in range(self.n):
                if self.grid[i][j] != 0:
                    row_domains.append([self.grid[i][j]])
                else:
                    row_domains.append(list(range(1, self.n + 1)))
            domains.append(row_domains)
        return domains

    def assign(self, row, col, value, rules=None):
        """
        Điền một số vào ô và tự động cập nhật (thu hẹp) miền giá trị của hàng/cột tương ứng và áp dụng AC3.
        """
        self.grid[row][col] = value
        self.possible_values[row][col] = [value]
        
        # Xóa 'value' khỏi các ô cùng hàng
        for j in range(self.n):
            if j != col and value in self.possible_values[row][j]:
                self.possible_values[row][j].remove(value)
                
        # Xóa 'value' khỏi các ô cùng cột
        for i in range(self.n):
            if i != row and value in self.possible_values[i][col]:
                self.possible_values[i][col].remove(value)
        
        if rules:
            self._ac3_propagate(rules)

    def _ac3_propagate(self, rules):
        """
        Propagate constraints using AC3 algorithm.
        Gọt bớt miền giá trị của các ô kề nhau nếu vi phạm dấu < hoặc >.
        """
        changed = True
        while changed:
            changed = False
            for r in range(self.n):
                for c in range(self.n):
                    # Bất đẳng thức ngang
                    if c < self.n - 1:
                        const = rules.horiz_const[r][c]
                        if const == 1:   # Trái < Phải
                            if self._revise(r, c, r, c + 1): changed = True
                        elif const == -1: # Trái > Phải
                            if self._revise(r, c + 1, r, c): changed = True
                            
                    # Bất đẳng thức dọc
                    if r < self.n - 1:
                        const = rules.vert_const[r][c]
                        if const == 1:   # Trên < Dưới
                            if self._revise(r, c, r + 1, c): changed = True
                        elif const == -1: # Trên > Dưới
                            if self._revise(r + 1, c, r, c): changed = True

    def _revise(self, r1, c1, r2, c2):
        """Xóa giá trị vô lý giữa 2 ô (Ô 1 < Ô 2). Trả về True nếu có domain bị thu hẹp."""
        dom_a, dom_b = self.possible_values[r1][c1], self.possible_values[r2][c2]
        if not dom_a or not dom_b: return False
        
        revised = False
        max_b = max(dom_b)
        for val in list(dom_a):
            if val >= max_b:
                dom_a.remove(val)
                revised = True
                
        if dom_a:
            min_a = min(dom_a)
            for val in list(dom_b):
                if val <= min_a:
                    dom_b.remove(val)
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
        Minimum Remaining Values (MRV) Heuristic.
        Tìm ô trống có số lượng 'possible_values' ít nhất.
        Rất hữu ích để chọn ô điền tiếp theo trong A* hoặc Backtracking.
        Trả về: (row, col) hoặc None nếu bảng đã đầy.
        """
        min_len = self.n + 1
        best_cell = None
        
        for i in range(self.n):
            for j in range(self.n):
                if self.grid[i][j] == 0:
                    curr_len = len(self.possible_values[i][j])
                    if curr_len < min_len:
                        min_len = curr_len
                        best_cell = (i, j)
                        # Nếu tìm thấy ô chỉ còn 1 khả năng, chốt luôn không cần tìm thêm
                        if min_len == 1:
                            return best_cell
                            
        return best_cell

    def clone(self):
        """
        Tạo một bản sao của trạng thái hiện tại (Dùng khi rẽ nhánh trong cây tìm kiếm).
        """
        # new_state = State(self.n, self.grid)
        # new_state.possible_values = copy.deepcopy(self.possible_values)

        # Không dùng copy.deepcopy để tiết kiệm bộ nhớ
        # Copy grid (List 2D)
        new_grid = [row[:] for row in self.grid]
        new_state = State(self.n, new_grid)
        
        # Copy possible_values (List 3D)
        new_possible = []
        for i in range(self.n):
            new_row = []
            for j in range(self.n):
                # Copy từng list nhỏ chứa domain
                new_row.append(self.possible_values[i][j][:])
            new_possible.append(new_row)
            
        new_state.possible_values = new_possible
        return new_state

    def get_valid_neighbors(self, rules):
        """
        Sinh ra các trạng thái (nhánh) tiếp theo hợp lệ từ trạng thái hiện tại.
        Sử dụng MRV Heuristic để chọn ô điền tiếp theo.
        """
        neighbors = []
        cell = self.get_mrv_cell()
        if not cell:
            return neighbors # Bảng đã đầy hoặc không còn lựa chọn
            
        row, col = cell
        for val in self.possible_values[row][col]:
            new_state = self.clone()
            new_state.assign(row, col, val, rules)
            
            # Kiểm tra trạng thái mới có hợp lệ luật Futoshiki hay không
            if rules.is_valid(new_state.grid):
                neighbors.append(new_state)
                
        return neighbors