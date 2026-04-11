import os

def read_input_file(filepath):
    """
    Đọc dữ liệu từ file input.
    Trả về: (n, grid, horizontal_constraints, vertical_constraints)
    """
    with open(filepath, 'r') as f:
        # Bỏ qua các dòng comment (bắt đầu bằng #) và dòng trống
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    
    n = int(lines[0])
    
    # 1. Đọc Grid (N dòng)
    grid = []
    for i in range(1, n + 1):
        grid.append(list(map(int, lines[i].split(','))))
        
    # 2. Đọc Horizontal constraints (N dòng, mỗi dòng N-1 giá trị)
    horiz_idx = n + 1
    horizontal_constraints = []
    for i in range(horiz_idx, horiz_idx + n):
        horizontal_constraints.append(list(map(int, lines[i].split(','))))
        
    # 3. Đọc Vertical constraints (N-1 dòng, mỗi dòng N giá trị)
    vert_idx = horiz_idx + n
    vertical_constraints = []
    for i in range(vert_idx, vert_idx + n - 1):
        vertical_constraints.append(list(map(int, lines[i].split(','))))
        
    return n, grid, horizontal_constraints, vertical_constraints


def write_output_file(filepath, grid, horiz_const, vert_const):
    """
    Ghi kết quả ra file theo đúng format yêu cầu của đồ án (có chứa dấu <, >, v, ^).
    1 = '<' (Trái < Phải hoặc Trên < Dưới)
    -1 = '>' (Trái > Phải hoặc Trên > Dưới)
    """
    # Đảm bảo thư mục tồn tại
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    n = len(grid)
    lines = []
    
    for i in range(n):
        # 1. Tạo dòng chứa số và ràng buộc ngang (Horizontal)
        row_str = ""
        for j in range(n):
            row_str += str(grid[i][j])
            # Nếu chưa phải cột cuối, thêm dấu ràng buộc ngang
            if j < n - 1:
                h_val = horiz_const[i][j]
                if h_val == 1:
                    row_str += " < "
                elif h_val == -1:
                    row_str += " > "
                else:
                    row_str += "   " # Không có ràng buộc thì để khoảng trắng
        lines.append(row_str)
        
        # 2. Tạo dòng chứa ràng buộc dọc (Vertical) nằm giữa các hàng số
        if i < n - 1:
            vert_str = ""
            for j in range(n):
                v_val = vert_const[i][j]
                if v_val == 1:
                    vert_str += "^"  # Trên bé hơn Dưới
                elif v_val == -1:
                    vert_str += "v"  # Trên lớn hơn Dưới
                else:
                    vert_str += " "
                
                # Căn lề cho khớp với các số ở hàng trên
                if j < n - 1:
                    vert_str += "   "
            lines.append(vert_str)
            
    # Ghi ra file
    with open(filepath, 'w') as f:
        f.write("\n".join(lines))
    print(f"[*] Đã lưu kết quả tại: {filepath}")