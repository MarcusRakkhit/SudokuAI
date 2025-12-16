from .State import State
from .Cell import Cell

class Backtracking:
    """
    Implements a backtracking solver for Sudoku.
    Uses a stack to store states and expands only valid moves.
    """
    def __init__(self):
        self.f_stack = []  # Stack of states to explore

    # =========================
    # CLONE CELL LIST
    # =========================
    def clone_list(self, original):
        """
        Create a deep copy of a list of Cell objects.
        """
        return [
            Cell(cell.get_cell_number(), cell.get_row_number(),
                 cell.get_column_number(), cell.get_block_number())
            for cell in original
        ]

    # =========================
    # ROW / COLUMN / BLOCK CHECKS
    # =========================
    def get_row(self, state, row, number):
        number = str(number)
        for cell in state.get_current():
            if cell.get_row_number() == row and cell.get_cell_number() == number:
                return False
        return True

    def get_column(self, state, column, number):
        number = str(number)
        for cell in state.get_current():
            if cell.get_column_number() == column and cell.get_cell_number() == number:
                return False
        return True

    def get_block(self, state, block, number):
        number = str(number)
        for cell in state.get_current():
            if cell.get_block_number() == block and cell.get_cell_number() == number:
                return False
        return True

    # =========================
    # ADD INITIAL STATE
    # =========================
    def add_first(self, first_element):
        first_state = State(first_element, None)
        first_state.set_id(1)
        self.f_stack.append(first_state)

    # =========================
    # MAIN BACKTRACKING SEARCH
    # =========================
    def backtracker_search(self):
        id_counter = 2

        while self.f_stack:
            # Check if fully solved
            current_state = self.f_stack.pop(0)
            empty_count = sum(1 for cell in current_state.get_current() if cell.get_cell_number() == ".")
            if empty_count == 0:
                return current_state.get_current()

            # Find first empty cell
            empty_index = next((i for i, c in enumerate(current_state.get_current())
                                if c.get_cell_number() == "."), None)
            if empty_index is None:
                continue  # Safe fallback

            cell = current_state.get_current()[empty_index]
            row, col, block = cell.get_row_number(), cell.get_column_number(), cell.get_block_number()

            new_state_list = []
            for n in range(1, 10):
                # Only create new state if number is valid
                if not (self.get_row(current_state, row, n) and
                        self.get_column(current_state, col, n) and
                        self.get_block(current_state, block, n)):
                    continue

                clone_cells = self.clone_list(current_state.get_current())
                clone_cells[empty_index] = Cell(str(n), row, col, block)
                new_state = State(clone_cells, current_state)
                new_state.set_id(id_counter)
                id_counter += 1
                new_state_list.append(new_state)

            # Depth-first: push new states onto stack
            self.f_stack = new_state_list + self.f_stack

        return None  # No solution