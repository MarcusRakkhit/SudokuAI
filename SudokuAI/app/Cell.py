class Cell:
    # Number in the cell (can also be empty)
    def __init__(self, cell_number=".", row_number=0, column_number=0, block_number=0):
        self._cell_number = cell_number  # string
        self._row_number = row_number    # int
        self._column_number = column_number  # int
        self._block_number = block_number    # int

    # Getters
    def get_cell_number(self):
        return self._cell_number

    def get_row_number(self):
        return self._row_number

    def get_column_number(self):
        return self._column_number

    def get_block_number(self):
        return self._block_number

    # Setters
    def set_cell_number(self, number):
        self._cell_number = str(number)