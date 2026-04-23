# FC Experiment and Evaluation Guide

## 1. Muc tieu

Tai lieu nay huong dan:
- Danh gia Forward Chaining (FC) theo huong suy dien, khong chi theo solved/unsolved.
- Setup thi nghiem cong bang giua FC, Backward Chaining, A*, Backtracking.
- Bao dam report day du 3 metric bat buoc:
  - Running time
  - Memory usage
  - Number of inferences/expansions
- Viet phan Discussion: thuat toan nao tot nhat, vi sao, va dieu kien nao nen uu tien tung thuat toan.

## 2. Cac metric bat buoc va dinh nghia

### 2.1 Running time
- Don vi: ms
- Do bang `time.perf_counter()`
- Cong thuc: `(end - start) * 1000`

### 2.2 Memory usage
- Don vi: KB hoac MB
- Do bang `tracemalloc`
- Gia tri bao cao:
  - `peak_memory`: dinh bo nho trong qua trinh chay solver
  - Khuyen nghi them `current_memory` de doi chieu

### 2.3 Number of inferences/expansions
- FC: `num_inferences`
  - So luong ket luan moi duoc suy ra trong Modus Ponens.
  - Kien nghi dem moi literal head duoc them vao tap `inferred`.
- A*: `num_expansions`
  - So state lay ra tu frontier de mo rong (so lan pop PriorityQueue).
- Backtracking: `num_expansions`
  - So node de quy duoc tham (so lan vao ham backtrack voi state hop le).
- Backward Chaining: `num_inferences` va `num_goal_expansions`
  - `num_inferences`: so lan unify thanh cong de tao buoc suy dien moi trong SLD resolution.
  - `num_goal_expansions`: so goal duoc lay ra de mo rong trong cay truy van.

## 3. Cach instrument code (khuyen nghi)

## 3.1 FC (Forward Chaining)
File lien quan: `src/solver/FCHybrid.py`

Can them bo dem thong ke:
- `self.stats = {"num_inferences": 0, "fc_iterations": 0}`

Vi tri tang bo dem:
1. Moi vong lap trong `_forward_chain`: tang `fc_iterations`.
2. Trong `_modus_ponens_closure`, khi co `head not in inferred` va truoc khi `agenda.append(head)`: tang `num_inferences` len 1.

Neu ban muon bao cao chi tiet hon:
- Them `num_positive_applied`
- Them `num_negative_pruned`
- Them `contradictions_detected`

## 3.2 A*
File lien quan: `src/solver/Astar.py`

Them bo dem:
- `self.stats = {"num_expansions": 0}`

Vi tri tang bo dem:
- Moi lan `frontier.get()` thanh cong trong `solve`, tang `num_expansions`.

## 3.3 Backtracking
File lien quan: `src/solver/Backtracking.py`

Them bo dem:
- `self.stats = {"num_expansions": 0}`

Vi tri tang bo dem:
- Dau ham `_backtrack`, tang `num_expansions`.

## 3.4 Backward Chaining
File lien quan: `src/solver/Backward.py`

Them bo dem:
- `self.stats = {"num_inferences": 0, "num_goal_expansions": 0}` trong `BackwardSolver`.

Vi tri tang bo dem (2 lua chon):
1. Cach nhanh, it thay doi:
  - Trong `solve`, wrap ham `sld_resolve(...)` bang mot wrapper generator.
  - Moi lan wrapper nhan duoc 1 subst trung gian/ket qua thi tang bo dem phu hop.
2. Cach dung nghia nhat:
  - Truyen doi tuong stats vao `sld_resolve`.
  - Tang `num_goal_expansions` moi lan vao nhanh co `goal = goals[0]`.
  - Tang `num_inferences` moi lan `unify(goal, fresh.head, subst)` thanh cong (khac None).

Goi y:
- De benchmark cong bang voi FC, uu tien bao cao theo cap:
  - FC: `num_inferences`
  - Backward: `num_inferences` (tuong duong suy dien)
- Dong thoi giu `num_goal_expansions` de phan tich do sau tim kiem logic.

## 3.5 Wrapper do runtime + memory
Ban co the tao script benchmark rieng (vd: `src/test/benchmark_algorithms.py`) voi mau:

```python
import time
import tracemalloc


def run_with_metrics(run_callable):
    tracemalloc.start()
    t0 = time.perf_counter()
    result = run_callable()
    t1 = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "result": result,
        "runtime_ms": (t1 - t0) * 1000,
        "memory_current_kb": current / 1024,
        "memory_peak_kb": peak / 1024,
    }
```

Sau do ghep them thong ke solver:
- FC: `solver.stats["num_inferences"]`
- Backward: `solver.stats["num_inferences"]`, `solver.stats["num_goal_expansions"]`
- A*/BT: `solver.stats["num_expansions"]`

## 4. Setup thi nghiem

### 4.1 Nguyen tac cong bang
- Cung input file.
- Cung may, cung moi truong Python.
- Cung so lan lap cho moi input (vd: 5 lan), lay trung binh.
- Chay warm-up 1 lan truoc khi ghi ket qua.

### 4.2 Tap du lieu
Dung toan bo `Inputs/inputs-01.txt` den `Inputs/inputs-12.txt`.
Nhom theo:
- Kich thuoc ban (4, 5, 6, 7, 8, 9)
- Muc do rang buoc (easy vs extreme)

### 4.3 Cac che do danh gia FC
Nen co it nhat 2 che do:
1. FC-pure:
   - Chi chay suy dien den fixpoint.
2. FC+fallback:
   - Chay FC truoc, neu chua solved thi fallback A* hoac Backtracking.
  - Trong benchmark script, co 2 bien the ro rang:
    - `forward_chaining_fallback_astar`
    - `forward_chaining_fallback_backtracking`

Muc dich:
- FC-pure danh gia suc manh suy dien.
- FC+fallback danh gia gia tri FC nhu bo tien xu ly.
- Co the bao cao them `fallback_usage_rate` de biet tan suat FC can goi fallback.

### 4.4 Cac che do danh gia Backward Chaining
Nen co it nhat 2 che do:
1. BC-first-solution:
  - Dung ngay khi tim thay loi giai dau tien (`next(solutions)`).
2. BC-limited-search:
  - Dat gioi han depth hoac so buoc suy dien de tranh no chi phi qua muc.

Muc dich:
- BC-first-solution danh gia kha nang tim nghiem nhanh.
- BC-limited-search danh gia tinh kha dung trong gioi han tai nguyen.

## 5. Mau bang ket qua

Luu ket qua CSV voi cot toi thieu:

- `input_id`
- `n`
- `difficulty`
- `algorithm`
- `solved` (0/1)
- `runtime_ms`
- `memory_peak_kb`
- `num_inferences_or_expansions`
- `num_goal_expansions` (bat buoc cho Backward Chaining)

Mau table tong hop trong report:

| Algorithm | Solve Rate | Avg Runtime (ms) | Avg Peak Memory (KB) | Avg Inferences/Expansions |
|---|---:|---:|---:|---:|
| Forward Chaining |  |  |  |  |
| Backward Chaining |  |  |  |  |
| A* |  |  |  |  |
| Backtracking |  |  |  |  |

## 6. Cac cau hoi phan tich bat buoc (Discussion)

Ban can tra loi ro cac cau sau:

1. Thuat toan nao perform tot nhat tong the?
- Dua tren can bang solve rate + runtime + memory + do on dinh theo kich thuoc.

2. Vi sao thuat toan do tot nhat?
- FC: co uu diem prune nhanh neu rang buoc manh.
- Backward Chaining: linh hoat theo truy van logic, phu hop khi can giai thich duong suy dien, nhung co the tang chi phi neu khong co gioi han tim kiem.
- A*: tim kiem co huong dan, thuong on dinh hon FC-pure tren bai can phan nhanh.
- Backtracking: don gian, manh neu ket hop MRV/forward checking tot, nhung co the no node o bai kho.

3. Dieu kien nao nen uu tien moi cach?
- Uu tien FC khi:
  - Bai co nhieu rang buoc, clue manh, de suy dien den singleton.
  - Can phat hien mau thuan som voi chi phi nho.
- Uu tien A* khi:
  - Can nghiem day du va bai can tim kiem.
  - Muon can bang chat luong ket qua va toc do.
- Uu tien Backward Chaining khi:
  - Can truy vet va giai thich qua trinh suy dien theo logic query.
  - Bai toan co query muc tieu cu the, khong nhat thiet phai liet ke toan bo khong gian trang thai.
- Uu tien Backtracking khi:
  - Can baseline de doi chieu.
  - Cau truc de phu hop voi MRV/forward checking.

4. Khi nao FC that bai khong co nghia la FC sai?
- Khi FC dung o fixpoint nhung bai van co nghiem (can branching).
- Do la gioi han tinh day du cua suy dien thuan, khong nhat thiet la bug.

5. Dau hieu bug that su trong FC
- FC suy ra mau thuan tren bai ma A*/BT tim duoc nghiem hop le.
- FC loai bo gia tri dung (over-pruning).

## 7. Khung ket luan goi y cho bao cao

Ban co the viet theo mau:

- "Forward Chaining dat hieu qua cao tren nhom bai co rang buoc day dac, the hien qua runtime thap va so inferences vua phai. Tuy nhien, tren bai yeu rang buoc hoac can branching, FC-pure dung som o fixpoint va khong dat solved state."
- "Backward Chaining huu ich khi bai toan can lap luan theo truy van va can kha nang giai thich; doi lai so goal expansions co the tang nhanh neu de bai khong du rang buoc."
- "A* la lua chon on dinh nhat de tim nghiem day du trong bo du lieu nay, doi lai chi phi expansions va memory cao hon FC tren mot so bai de."
- "Backtracking phu hop lam baseline va co the canh tranh tren bai nho/trung binh, nhung de bi tang expansions o cac bai kho hon neu heuristic khong du manh."

## 8. Checklist truoc khi nop

- [ ] Co report runtime cho tat ca input va tat ca algorithm.
- [ ] Co report memory usage cho tat ca input va tat ca algorithm.
- [ ] Co report number of inferences/expansions cho tat ca input va tat ca algorithm.
- [ ] Co bieu do hoac table tong hop theo kich thuoc/de kho.
- [ ] Co phan Discussion tra loi day du: best algorithm, why, and preferred conditions.
- [ ] Co neu ro han che va threat to validity (noise may, warm-up, variance runtime).

## 9. Lenh chay goi y

Tu thu muc goc project:

```powershell
uv run .\src\test\test_forward_chaining.py
uv run .\src\test\test_backward_chaining.py
uv run .\src\test\test_astar.py
uv run .\src\test\test_backtracking.py
```

Neu tao benchmark script rieng:

```powershell
uv run .\src\test\benchmark_algorithms.py
```

Tang do tin cay:
- Chay moi case >= 5 lan
- Bao cao trung binh + do lech chuan
