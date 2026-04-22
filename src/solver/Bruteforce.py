import copy

class BruteForceSolver:
    def __init__(self, rules, limit=1000000): # Giới hạn 1 triệu bước thử
        self.rules = rules
        self.limit = limit
        self.nodes_visited = 0

    def solve(self, grid):
        self.nodes_visited += 1
        
        # Nếu vượt quá giới hạn, trả về một chuỗi đặc biệt để GUI nhận biết
        if self.nodes_visited > self.limit:
            return "LIMIT_EXCEEDED"

        n = len(grid)
        
        empty_cell = None
        for i in range(n):
            for j in range(n):
                if grid[i][j] == 0:
                    empty_cell = (i, j)
                    break
            if empty_cell: break
                
        if not empty_cell:
            return grid if self.rules.is_solved(grid) else None

        r, c = empty_cell
        for val in range(1, n + 1):
            grid[r][c] = val
            if self.rules.is_valid(grid):
                result = self.solve(grid)
                if result is not None:
                    return result
            
            grid[r][c] = 0
            
        return None