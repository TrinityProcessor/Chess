import Piece 

WHITE = 1
BLACK = 2

class Knight(Piece):
    """Knight: jumps to any of its eight L-shaped target squares."""

    def __init__(self, color, coords):
        super().__init__(color, coords)
        self.name = 'N'
        self.movement_vectors = [(-2,1),(-1,2),(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1)]

        # Range one means each complete knight vector is checked once. Knights
        # do not scan intermediate squares and therefore jump over pieces.
        self.movement_range = 1
        self.value = 3
        self.logsindex += 2