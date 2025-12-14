class PrintGrid:
    # Constructor
    def __init__(self):
        pass

    def print_numbers(self, cells):
        """
        Pretty print Sudoku grid from a list of Cell objects
        """
        # Build a 9x9 grid from cell objects
        grid = [[0 for _ in range(9)] for _ in range(9)]

        for cell in cells:
            row = cell.get_row_number() - 1      # convert to 0-based
            col = cell.get_column_number() - 1
            val = cell.get_cell_number()

            grid[row][col] = val if val != "." else 0

        # Reuse your existing printer logic
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