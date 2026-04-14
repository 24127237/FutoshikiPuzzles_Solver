from queue import PriorityQueue
import itertools

class AstarSolver:
    def __init__(self):
        pass

    def _hashable(self, grid):
        """Chuyển đổi grid (list of lists) thành tuple of tuples để dùng làm key trong dict."""
        return tuple(tuple(row) for row in grid)

    def heuristic(self, state, rules): # must be admissible
        # 1. Đếm số ô chưa điền (số 0)
        h1 = len(state.get_empty_cells())
        
        # 2. Tổng kích thước các cụm bất đẳng thức chưa chốt
        ineq_chains = rules.get_inequality_chain_sizes(state.grid)
        h2 = sum(ineq_chains)

        # 3. Cells with empty domains
        h3 = 0
        for r in range(state.n):
            for c in range(state.n):
                if state.grid[r][c] == 0 and len(state.possible_values[r][c]) == 0:
                    return float('inf') # Cắt nhánh ngay lập tức
        
        return h1 + h2 + h3

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
        
        # frontier lưu: (f_cost, tie_breaker, current_state)
        # f = g + h. Tại trạng thái đầu g = 0
        frontier.put((self.heuristic(initial_state, rules), next(counter), initial_state))
        
        # reached lưu chi phí g (cost từ bước đầu đến hiện tại): { grid_tuple : g_cost }
        reached = {init_grid_tuple: 0}
        
        # parents lưu: { current_grid_tuple : parent_grid_tuple }
        parents = {init_grid_tuple: None}

        while not frontier.empty():
            current_f, _, current_state = frontier.get()
            current_grid_tuple = self._hashable(current_state.grid)
            
            if rules.is_solved(current_state.grid):
                return self.build_path(parents, current_grid_tuple)
                
            cur_g = reached[current_grid_tuple]

            for next_state in current_state.get_valid_neighbors(rules):
                next_grid_tuple = self._hashable(next_state.grid)
                new_g = cur_g + 1 # Mỗi bước điền 1 số ta tốn chi phí 1 (g)
                new_f = new_g + self.heuristic(next_state, rules) # f = g + h
                
                # Nếu chưa từng đến trạng thái này hoặc tìm được đường g rẻ hơn
                if next_grid_tuple not in reached or new_g < reached[next_grid_tuple]:
                    reached[next_grid_tuple] = new_g
                    if new_f != float('inf'):
                        frontier.put((new_f, next(counter), next_state))
                        parents[next_grid_tuple] = current_grid_tuple
                    
        return None