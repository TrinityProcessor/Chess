import Piece

WHITE = 1
BLACK = 2

class Queen(Piece):
    """Queen: slides along ranks, files, and diagonals."""

    def __init__(self, color, coords):
        super().__init__(color, coords)
        self.name = 'Q'
        self.movement_vectors = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
        self.movement_range = 7
        self.value = 9
        self.logsindex += 8