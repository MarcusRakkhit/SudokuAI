from .State import State
from .Cell import Cell

class Backtracking:
    def __init__(self):
        self.f_stack = []
        self.cell_data = []

    def expand_state(self, expand):
        return None

    # Clone a list of Cell objects
    def clone_list(self, original):
        new_cell_list = []
        for element in original:
            new_cell = Cell(
                element.get_cell_number(),
                element.get_row_number(),
                element.get_column_number(),
                element.get_block_number()
            )
            new_cell_list.append(new_cell)
        return new_cell_list

    # Clone a State object
    def clone_state(self, expand):
        new_cell_list = []
        for element in expand.get_current():
            new_cell = Cell(
                element.get_cell_number(),
                element.get_row_number(),
                element.get_column_number(),
                element.get_block_number()
            )
            new_cell_list.append(new_cell)
        clone = State(new_cell_list, expand.get_parent())
        return clone

    # Fast row check
    def get_row(self, expand, row, number):
        number = str(number)
        for cell in expand.get_current():
            if cell.get_row_number() == row and cell.get_cell_number() == number:
                return False
        return True

    # Fast column check
    def get_column(self, expand, column, number):
        number = str(number)
        for cell in expand.get_current():
            if cell.get_column_number() == column and cell.get_cell_number() == number:
                return False
        return True

    # Fast block check
    def get_block(self, expand, block, number):
        number = str(number)
        for cell in expand.get_current():
            if cell.get_block_number() == block and cell.get_cell_number() == number:
                return False
        return True

    # Add the initial state to the stack
    def add_first(self, first_element):
        first_stack = State(first_element, None)
        first_stack.set_id(1)
        self.f_stack.append(first_stack)

    # Main backtracking search
    def backtracker_search(self):
        id_counter = 2

        while len(self.f_stack) != 0:

            # Check if fully solved
            empty = sum(1 for cell in self.f_stack[0].get_current()
                         if cell.get_cell_number() == ".")
            if empty == 0:
                return self.f_stack[0].get_current()

            # Get first state
            expand_state = self.f_stack.pop(0)

            # Find first empty cell
            current_cells = expand_state.get_current()
            empty_index = None

            for idx in range(81):
                if current_cells[idx].get_cell_number() == ".":
                    empty_index = idx
                    break

            if empty_index is None:
                continue  # Should not happen but safe

            row = current_cells[empty_index].get_row_number()
            col = current_cells[empty_index].get_column_number()
            block = current_cells[empty_index].get_block_number()

            # Create only VALID successor states
            new_state_list = []

            for n in range(1, 10):

                # Validate BEFORE cloning (huge speed boost)
                if not (self.get_row(expand_state, row, n) and
                        self.get_column(expand_state, col, n) and
                        self.get_block(expand_state, block, n)):
                    continue

                # If valid → now clone
                new_cell = Cell(str(n), row, col, block)
                clone_cells = self.clone_list(current_cells)
                clone_cells[empty_index] = new_cell

                new_state = State(clone_cells, expand_state)
                new_state.set_id(id_counter)
                id_counter += 1
                new_state_list.append(new_state)

            # Depth-first: push new states on stack in correct order
            self.f_stack = new_state_list + self.f_stack

        return None  # No solution