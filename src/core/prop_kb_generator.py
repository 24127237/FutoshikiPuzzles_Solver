class FutoshikiKBGenerator:
    def __init__(self, n):
        self.n = n

    def get_var(self, r, c, v):
        """
        Mã hóa tọa độ (row r, col c, value v) thành một số nguyên dương duy nhất.
        r, c trong khoảng [0, n-1]. v trong khoảng [1, n].
        """
        # Công thức tính ID biến. Trả về ID từ 1 đến N^3
        return r * (self.n * self.n) + c * self.n + v

    def decode_var(self, var_id):
        """
        Giải mã ID biến propositional về (row, col, value).
        """
        idx = var_id - 1
        r = idx // (self.n * self.n)
        rem = idx % (self.n * self.n)
        c = rem // self.n
        v = (rem % self.n) + 1
        return r, c, v

    def generate_cell_constraints(self):
        """
        A1 & A2: Ràng buộc mỗi ô chứa ĐÚNG MỘT giá trị từ 1 đến N.
        """
        clauses = []
        for r in range(self.n):
            for c in range(self.n):
                # A1: Mỗi ô phải có ÍT NHẤT 1 giá trị (v1 OR v2 OR ... OR vn)
                at_least_one = [self.get_var(r, c, v) for v in range(1, self.n + 1)]
                clauses.append(at_least_one)

                # A2: Mỗi ô có TỐI ĐA 1 giá trị. 
                # (Nếu có giá trị v1 thì KHÔNG được có v2) => NOT v1 OR NOT v2
                for v1 in range(1, self.n + 1):
                    for v2 in range(v1 + 1, self.n + 1):
                        clauses.append([-self.get_var(r, c, v1), -self.get_var(r, c, v2)])
        return clauses

    def generate_row_col_constraints(self):
        """
        A3 & A4: Tính duy nhất trên hàng và cột.
        """
        clauses = []
        for v in range(1, self.n + 1):
            for i in range(self.n):
                for j1 in range(self.n):
                    for j2 in range(j1 + 1, self.n):
                        # A3: Cùng một hàng i, không thể có hai cột j1 và j2 cùng mang giá trị v
                        clauses.append([-self.get_var(i, j1, v), -self.get_var(i, j2, v)])
                        
                        # A4: Cùng một cột i (ở đây dùng i như chỉ mục cột), không thể có 2 hàng j1, j2 mang giá trị v
                        clauses.append([-self.get_var(j1, i, v), -self.get_var(j2, i, v)])
        return clauses

    def generate_given_clues(self, grid):
        """
        A5: Ràng buộc các ô đã cho sẵn (Given).
        """
        clauses = []
        for r in range(self.n):
            for c in range(self.n):
                val = grid[r][c]
                if val != 0:
                    # Nếu ô đã điền số, ép biến đó phải bằng True (Mệnh đề đơn - Unit Clause)
                    clauses.append([self.get_var(r, c, val)])
        return clauses

    def generate_horizontal_inequalities(self, horiz_const):
        """
        A6: Bất đẳng thức ngang (Trái < Phải hoặc Trái > Phải)
        """
        clauses = []
        for r in range(self.n):
            for c in range(self.n - 1):
                const = horiz_const[r][c]
                if const == 0:
                    continue
                
                # Logic chuyển đổi: Nếu Ô(Trái) = v1, thì Ô(Phải) phải thỏa mãn điều kiện.
                # Do đó: NOT (Ô(Trái) = v1) OR (Ô(Phải) = v2 hợp lệ) OR (Ô(Phải) = v3 hợp lệ) ...
                for v1 in range(1, self.n + 1):
                    valid_right_vars = []
                    for v2 in range(1, self.n + 1):
                        if (const == 1 and v1 < v2) or (const == -1 and v1 > v2):
                            valid_right_vars.append(self.get_var(r, c + 1, v2))
                    
                    # Nếu v1 không có v2 nào thỏa mãn (vd: v1=N mà Trái < Phải => Vô lý)
                    # Thì NOT (Ô(Trái) = v1) phải là True (tức là v1 không được phép xuất hiện ở ô Trái)
                    clause = [-self.get_var(r, c, v1)] + valid_right_vars
                    clauses.append(clause)
        return clauses

    def generate_vertical_inequalities(self, vert_const):
        """
        A7: Bất đẳng thức dọc (Trên < Dưới hoặc Trên > Dưới)
        Logic CNF giống với bất đẳng thức ngang, nhưng áp dụng cho cặp ô (r, c) và (r + 1, c).
        """
        clauses = []
        for r in range(self.n - 1):
            for c in range(self.n):
                const = vert_const[r][c]
                if const == 0:
                    continue

                # Nếu Ô(Trên) = v1, thì Ô(Dưới) phải thuộc tập giá trị hợp lệ.
                for v1 in range(1, self.n + 1):
                    valid_bottom_vars = []
                    for v2 in range(1, self.n + 1):
                        if (const == 1 and v1 < v2) or (const == -1 and v1 > v2):
                            valid_bottom_vars.append(self.get_var(r + 1, c, v2))

                    clause = [-self.get_var(r, c, v1)] + valid_bottom_vars
                    clauses.append(clause)
        return clauses

    def generate_full_kb(self, grid, horiz_const, vert_const):
        """
        Hàm chính tổng hợp toàn bộ các mệnh đề CNF lại thành một Knowledge Base duy nhất.
        """
        kb = []
        kb.extend(self.generate_cell_constraints())
        kb.extend(self.generate_row_col_constraints())
        kb.extend(self.generate_given_clues(grid))
        kb.extend(self.generate_horizontal_inequalities(horiz_const))
        kb.extend(self.generate_vertical_inequalities(vert_const))
        
        return kb

    def generate_horn_facts_from_grid(self, grid):
        """
        Ground facts cho Horn KB từ các ô đã cho sẵn.
        Mỗi fact là một literal dương Val(r,c,v).
        """
        facts = set()
        for r in range(self.n):
            for c in range(self.n):
                val = grid[r][c]
                if val != 0:
                    facts.add(self.get_var(r, c, val))
        return facts

    def generate_horn_rules(self, horiz_const, vert_const):
        """
        Sinh Horn rules dạng (body_literals, head_literal).

        Quy ước literal:
        - +X(r,c,v): ô (r,c) có giá trị v
        - -X(r,c,v): ô (r,c) KHÔNG có giá trị v

        Mỗi rule là một tuple (body, head), trong đó:
        - body: tuple các literal phải đúng
        - head: literal suy ra theo Modus Ponens
        """
        rules = []

        def add_rule(body, head):
            rules.append((tuple(body), head))

        # R1: Nếu ô có giá trị v thì ô đó không thể nhận giá trị khác v.
        for r in range(self.n):
            for c in range(self.n):
                for v in range(1, self.n + 1):
                    var_v = self.get_var(r, c, v)
                    for u in range(1, self.n + 1):
                        if u == v:
                            continue
                        add_rule((var_v,), -self.get_var(r, c, u))

        # R2: Tính duy nhất theo hàng/cột (A3/A4) dưới dạng Horn implication.
        for v in range(1, self.n + 1):
            for r in range(self.n):
                for c1 in range(self.n):
                    for c2 in range(self.n):
                        if c1 != c2:
                            add_rule((self.get_var(r, c1, v),), -self.get_var(r, c2, v))

            for c in range(self.n):
                for r1 in range(self.n):
                    for r2 in range(self.n):
                        if r1 != r2:
                            add_rule((self.get_var(r1, c, v),), -self.get_var(r2, c, v))

        # R3: Bất đẳng thức ngang/dọc -> loại bỏ giá trị không hợp lệ ở ô kề.
        for r in range(self.n):
            for c in range(self.n - 1):
                const = horiz_const[r][c]
                if const == 0:
                    continue

                for v_left in range(1, self.n + 1):
                    left_var = self.get_var(r, c, v_left)
                    for v_right in range(1, self.n + 1):
                        right_var = self.get_var(r, c + 1, v_right)
                        is_valid = (const == 1 and v_left < v_right) or (const == -1 and v_left > v_right)
                        if not is_valid:
                            add_rule((left_var,), -right_var)
                            add_rule((right_var,), -left_var)

        for r in range(self.n - 1):
            for c in range(self.n):
                const = vert_const[r][c]
                if const == 0:
                    continue

                for v_top in range(1, self.n + 1):
                    top_var = self.get_var(r, c, v_top)
                    for v_bottom in range(1, self.n + 1):
                        bottom_var = self.get_var(r + 1, c, v_bottom)
                        is_valid = (const == 1 and v_top < v_bottom) or (const == -1 and v_top > v_bottom)
                        if not is_valid:
                            add_rule((top_var,), -bottom_var)
                            add_rule((bottom_var,), -top_var)

        return rules

    def generate_horn_kb(self, grid, horiz_const, vert_const):
        """
        Sinh Horn KB đầy đủ gồm facts + rules để dùng cho forward chaining (Modus Ponens).
        """
        facts = self.generate_horn_facts_from_grid(grid)
        rules = self.generate_horn_rules(horiz_const, vert_const)
        return facts, rules