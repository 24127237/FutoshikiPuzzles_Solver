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

    def assign(self, row, col, value):
        """
        Điền một số vào ô và tự động cập nhật (thu hẹp) miền giá trị của hàng/cột tương ứng.
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
        new_state = State(self.n, self.grid)
        new_state.possible_values = copy.deepcopy(self.possible_values)
        return new_state