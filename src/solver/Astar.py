from queue import PriorityQueue
import itertools

class AstarSolver:
    def __init__(self):
        pass

    def _hashable(self, grid):
        """Chuyển đổi grid (list of lists) thành tuple of tuples để dùng làm key trong dict."""
        return tuple(tuple(row) for row in grid)

    def heuristic(self, state, rules): # must be admissible
        # Cells with empty domains
        for r in range(state.n):
            for c in range(state.n):
                if state.grid[r][c] == 0 and len(state.possible_values[r][c]) == 0:
                    return float('inf'), 0, 0 # Cắt nhánh ngay lập tức

        # 1. Đếm số ô chưa điền (số 0)
        h1 = len(state.get_empty_cells())
        
        # 2. Tổng kích thước các cụm bất đẳng thức chưa chốt
        ineq_chains = rules.get_inequality_chain_sizes(state.grid)
        h2 = sum(ineq_chains)

        # 3. Tie-breaker 2: Degree (Độ thắt chặt ràng buộc)
        # Bảng càng bị thắt chặt miền giá trị tổng thể thì càng dễ giải
        h3 = 0
        for r in range(state.n):
            for c in range(state.n):
                if state.grid[r][c] == 0:
                    h3 += len(state.possible_values[r][c]) 
        # h3 là tổng số lựa chọn CÒN LẠI trên toàn bàn cờ.
        # h3 CÀNG NHỎ nghĩa là ta đã thu hẹp được rất nhiều lựa chọn (Pruning tốt).
        
        return h1, h2, h3

    def build_path(self, parents, current_grid_tuple):
        """Tái tạo đường đi từ trạng thái đích ngược về trạng thái ban đầu."""
        path = [list(list(row) for row in current_grid_tuple)]
        while current_grid_tuple in parents:
            current_grid_tuple = parents[current_grid_tuple]
            if current_grid_tuple is not None:
                path.append(list(list(row) for row in current_grid_tuple))
        return path[::-1] # Trả về đường đi từ trạng thái đầu đến đích

    def solve(self, initial_state, rules):
        frontier = PriorityQueue()
        counter = itertools.count() # Dùng làm tie-breaker cho PriorityQueue
        
        init_grid_tuple = self._hashable(initial_state.grid)
        
        # frontier lưu: (f_cost, -h2_tiebreaker, h3_tiebreaker, -counter, current_state)
        init_h1, init_h2, init_h3 = self.heuristic(initial_state, rules)
        frontier.put((init_h1, -init_h2, init_h3, -next(counter), initial_state))
        
        # reached lưu chi phí g (cost từ bước đầu đến hiện tại): { grid_tuple : g_cost }
        reached = {init_grid_tuple: 0}
        
        # parents lưu: { current_grid_tuple : parent_grid_tuple }
        parents = {init_grid_tuple: None}

        while not frontier.empty():
            current_f, _, _, _, current_state = frontier.get()
            current_grid_tuple = self._hashable(current_state.grid)
            
            if rules.is_solved(current_state.grid):
                return self.build_path(parents, current_grid_tuple)
                
            cur_g = reached[current_grid_tuple]

            for next_state in current_state.get_valid_neighbors(rules):
                next_grid_tuple = self._hashable(next_state.grid)
                new_g = cur_g + 1 # Mỗi bước điền 1 số ta tốn chi phí 1 (g)
                new_h1, new_h2, new_h3 = self.heuristic(next_state, rules)

                if new_h1 == float('inf'):
                    continue
                
                new_f = new_g + new_h1
                # Nếu chưa từng đến trạng thái này hoặc tìm được đường g rẻ hơn
                if next_grid_tuple not in reached or new_g < reached[next_grid_tuple]:
                    reached[next_grid_tuple] = new_g
                    frontier.put((new_f, -new_h2, new_h3, -next(counter), next_state))
                    parents[next_grid_tuple] = current_grid_tuple
                    
        return None