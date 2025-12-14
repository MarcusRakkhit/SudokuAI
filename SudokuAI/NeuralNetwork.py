import sys
import cv2
import numpy as np
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"


class SudokuImageToGrid:

    # =========================
    # OCR EXTRACTION
    # =========================
    def extract_sudoku_grid(image_path, existing_grid=None):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        if existing_grid is not None:
            sudoku_grid = [row[:] for row in existing_grid]
            print("\nUsing existing grid as base...")
        else:
            sudoku_grid = [[0 for _ in range(9)] for _ in range(9)]

        cell_h = h // 9
        cell_w = w // 9

        for row in range(9):
            for col in range(9):
                if existing_grid is not None and existing_grid[row][col] != 0:
                    continue

                cell_y = y + row * cell_h
                cell_x = x + col * cell_w
                padding = 5

                cell = gray[
                    cell_y + padding: cell_y + cell_h - padding,
                    cell_x + padding: cell_x + cell_w - padding
                ]

                _, cell_thresh = cv2.threshold(cell, 128, 255, cv2.THRESH_BINARY_INV)

                if np.sum(cell_thresh) > 100:
                    config = '--psm 10 --oem 3 -c tessedit_char_whitelist=123456789'
                    text = pytesseract.image_to_string(cell, config=config).strip()

                    if text.isdigit():
                        sudoku_grid[row][col] = int(text)

        return sudoku_grid

    # =========================
    # GRID PRINTER
    # =========================
    def print_sudoku_grid(grid):
        print("\n    0 1 2   3 4 5   6 7 8")
        print("  " + "-" * 25)
        for i, row in enumerate(grid):
            if i % 3 == 0 and i != 0:
                print("  " + "-" * 25)

            row_str = f"{i} | "
            for j, val in enumerate(row):
                if j % 3 == 0 and j != 0:
                    row_str += "| "
                row_str += str(val if val != 0 else ".") + " "
            print(row_str + "|")

        print("  " + "-" * 25)

    # =========================
    # VALIDATION
    # =========================
    def validate_no_duplicates(grid):
        errors = []

        # Rows
        for r in range(9):
            seen = {}
            for c in range(9):
                val = grid[r][c]
                if val != 0:
                    if val in seen:
                        errors.append(
                            f"Duplicate {val} in row {r} (cols {seen[val]} and {c})"
                        )
                    else:
                        seen[val] = c

        # Columns
        for c in range(9):
            seen = {}
            for r in range(9):
                val = grid[r][c]
                if val != 0:
                    if val in seen:
                        errors.append(
                            f"Duplicate {val} in column {c} (rows {seen[val]} and {r})"
                        )
                    else:
                        seen[val] = r

        # Blocks
        for br in range(3):
            for bc in range(3):
                seen = {}
                for r in range(br * 3, br * 3 + 3):
                    for c in range(bc * 3, bc * 3 + 3):
                        val = grid[r][c]
                        if val != 0:
                            if val in seen:
                                pr, pc = seen[val]
                                errors.append(
                                    f"Duplicate {val} in block ({br},{bc}) "
                                    f"at ({pr},{pc}) and ({r},{c})"
                                )
                            else:
                                seen[val] = (r, c)

        return errors

    def count_filled_cells(grid):
        return sum(1 for r in range(9) for c in range(9) if grid[r][c] != 0)

    # =========================
    # INTERACTIVE EDITOR
    # =========================
    @staticmethod
    def edit_grid_interactive(grid, image_path):
        print("\n=== Interactive Grid Editor ===")
        print("Commands:")
        print("  R C V          → set cell")
        print("  R C 0          → clear cell")
        print("  R C V, ...     → multiple cells")
        print("  row R v1..v9   → entire row")
        print("  clear R C")
        print("  show | help | undo | done | quit\n")

        history = []

        while True:
            SudokuImageToGrid.print_sudoku_grid(grid)
            cmd = input("\nEnter command: ").strip().lower()

            # ===== DONE (VALIDATE) =====
            if cmd == 'done':
                errors = SudokuImageToGrid.validate_no_duplicates(grid)
                filled_count = SudokuImageToGrid.count_filled_cells(grid)

                if filled_count < 17:
                    print(
                        f"\n❌ Cannot finish — only {filled_count} numbers filled."
                        "\nA valid Sudoku requires at least 17 clues."
                    )
                    continue

                if errors:
                    print("\n❌ Cannot finish — duplicates detected:")
                    for err in errors:
                        print("  -", err)
                    print("\nFix the errors and try again.")
                    continue

                print(
                    f"\n✅ Final grid valid "
                    f"({filled_count} filled cells, no duplicates):"
                )
                SudokuImageToGrid.print_sudoku_grid(grid)
                break

            elif cmd == 'show':
                continue

            elif cmd == 'quit':
                sys.exit()

            elif cmd == 'help':
                print("Commands:")
                print("  R C V          → set cell")
                print("  R C 0          → clear cell")
                print("  R C V, ...     → multiple cells")
                print("  row R v1..v9   → entire row")
                print("  clear R C")
                print("  show | help | undo | done | quit\n")

            elif cmd == 'undo':
                if history:
                    grid = history.pop()
                    print("Undid last change")
                else:
                    print("Nothing to undo")
                continue

            elif cmd.startswith('row'):
                try:
                    parts = cmd.split()
                    if len(parts) != 11:
                        print("Use: row R v1 v2 ... v9")
                        continue

                    r = int(parts[1])
                    history.append([row[:] for row in grid])

                    for c in range(9):
                        grid[r][c] = int(parts[c + 2])

                except Exception:
                    print("Invalid row command")

            elif cmd.startswith('clear'):
                try:
                    _, r, c = cmd.split()
                    history.append([row[:] for row in grid])
                    grid[int(r)][int(c)] = 0
                except Exception:
                    print("Use: clear R C")

            elif ',' in cmd:
                history.append([row[:] for row in grid])
                try:
                    for part in cmd.split(','):
                        r, c, v = map(int, part.strip().split())
                        grid[r][c] = v
                except Exception:
                    grid = history.pop()
                    print("Invalid multi-cell command")

            else:
                try:
                    r, c, v = map(int, cmd.split())
                    history.append([row[:] for row in grid])
                    grid[r][c] = v
                except Exception:
                    print("Invalid command")

        return grid