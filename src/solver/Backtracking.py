class BacktrackingSolver:
    def __init__(self, rules):
        """
        Khởi tạo solver với bộ luật đã định nghĩa.
        """
        self.rules = rules
        self.stats = {"num_expansions": 0}

    def solve(self, initial_state):
        """
        Hàm giao tiếp bên ngoài, nhận vào object State.
        """
        self.stats = {"num_expansions": 0}
        result_state = self._backtrack(initial_state)
        if result_state:
            return result_state.grid
        return None

    def _backtrack(self, state):
        """
        Hàm đệ quy quay lui sử dụng MRV và Forward Checking.
        """
        self.stats["num_expansions"] += 1
        # Base case: Nếu get_mrv_cell trả về None, tức là bảng đã được điền đầy
        if state.get_mrv_cell() is None:
            # Kiểm tra an toàn lần cuối
            if self.rules.is_solved(state.grid):
                return state
            return None

        # state.get_neighbors() đã làm giúp chúng ta việc:
        # - Chọn ô trống tốt nhất (MRV)
        # - Tạo các bản sao trạng thái (Clone)
        # - Chỉ trả về các trạng thái hợp lệ (is_valid == True)
        valid_neighbors = state.get_valid_neighbors(self.rules)
        
        for next_state in valid_neighbors:
            result = self._backtrack(next_state)
            if result is not None:
                return result # Trả về ngay trạng thái đích
                
        return None # Quay lui nếu tất cả neighbor đều dẫn tới ngõ cụt