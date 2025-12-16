from .Cell import Cell

class StoreCells:
    # Sudoku size is 81 cells
    def __init__(self):
        self.grid_size = 81

    def createList(self, grid):
        """
        Convert a 9x9 sudoku grid into a list of Cell objects
        """
        cells = []

        for row in range(9):
            for col in range(9):
                value = grid[row][col]

                # Convert 0 to "." for empty cells
                cell_value = "." if value == 0 else str(value)

                block = (row // 3) * 3 + (col // 3) + 1

                cell = Cell(
                    cell_number=cell_value,
                    row_number=row + 1,      # 1-based indexing
                    column_number=col + 1,   # 1-based indexing
                    block_number=block
                )

                cells.append(cell)

        return cells