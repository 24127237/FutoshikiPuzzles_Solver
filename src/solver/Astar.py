from queue import PriorityQueue
import itertools

class AstarSolver:
    def __init__(self):
        self.stats = {"num_expansions": 0}

    def heuristic(self, state, rules): # must be admissible
        # Cells with empty domains
        for r in range(state.n):
            for c in range(state.n):
                if state.grid[r][c] == 0 and state.possible_values[r][c] == 0:
                    return float('inf') # Cắt nhánh ngay lập tức

        # Đếm số ô chưa điền (số 0)
        h1 = len(state.get_empty_cells())
        return h1
    
    def heuristic_2(self, state, rules):
        # Cells with empty domains
        for r in range(state.n):
            for c in range(state.n):
                if state.grid[r][c] == 0 and state.possible_values[r][c] == 0:
                    return float('inf') # Cắt nhánh ngay lập tức
        
        # Tổng kích thước các cụm bất đẳng thức chưa chốt
        ineq_chains = rules.get_inequality_chain_sizes(state.grid)
        h2 = sum(ineq_chains)
        return h2

    def heuristic_3(self, state, rules):
        # Cells with empty domains
        for r in range(state.n):
            for c in range(state.n):
                if state.grid[r][c] == 0 and state.possible_values[r][c] == 0:
                    return float('inf') # Cắt nhánh ngay lập tức
        
        # Degree (Độ thắt chặt ràng buộc)
        # Bảng càng bị thắt chặt miền giá trị tổng thể thì càng dễ giải
        h3, cnt_unfilled = 0, 0
        for r in range(state.n):
            for c in range(state.n):
                if state.grid[r][c] == 0:
                    h3 += state.possible_values[r][c].bit_count()
                    cnt_unfilled += 1
        # h3 là tổng số lựa chọn CÒN LẠI trên toàn bàn cờ.
        # h3 CÀNG NHỎ nghĩa là ta đã thu hẹp được rất nhiều lựa chọn (Pruning tốt).
        
        return h3 / cnt_unfilled if cnt_unfilled != 0 else h3

    def build_path(self, goal_state):
        """Tái tạo đường đi từ trạng thái đích ngược về trạng thái ban đầu."""
        path = []
        curr = goal_state
        while curr is not None:
            path.append([list(row) for row in curr.grid])
            curr = getattr(curr, 'parent_state', None)
        return path[::-1] # Trả về đường đi từ trạng thái đầu đến đích

    def solve(self, initial_state, rules):
        self.stats = {"num_expansions": 0}
        frontier = PriorityQueue()
        counter = itertools.count() # Dùng làm tie-breaker cho PriorityQueue
        
        # frontier lưu: (f_cost, -g_cost, counter, current_state)
        init_h = self.heuristic(initial_state, rules)
        frontier.put((init_h, 0, next(counter), initial_state))
        
        initial_state.parent_state = None

        while not frontier.empty():
            current_f, neg_cur_g, _, current_state = frontier.get()
            self.stats["num_expansions"] += 1
            cur_g = -neg_cur_g
            
            if rules.is_solved(current_state.grid):
                return self.build_path(current_state)

            for next_state in current_state.get_valid_neighbors(rules):
                new_g = cur_g + 1 # Mỗi bước điền 1 số ta tốn chi phí 1 (g)
                new_h = self.heuristic(next_state, rules)

                if new_h == float('inf'):
                    continue
                
                new_f = new_g + new_h
                
                next_state.parent_state = current_state
                frontier.put((new_f, -new_g, next(counter), next_state))
                    
        return None