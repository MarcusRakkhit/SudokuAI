class State:
    def __init__(self, current, parent):
        # private int id;
        self._id = None

        # private List<Cell> currentState = new List<Cell>();
        self._current_state = current

        # private State parentState;
        self._parent_state = parent

    def set_id(self, ident):
        self._id = ident

    def set_current(self, current):
        self._current_state = current

    def set_parent(self, parent):
        self._parent_state = parent

    def get_current(self):
        return self._current_state

    def get_parent(self):
        return self._parent_state