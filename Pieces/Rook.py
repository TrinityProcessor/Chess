import Piece 

WHITE = 1
BLACK = 2

class Rook(Piece):
    """Rook: slides horizontally and vertically."""

    def __init__(self, color, coords):
        super().__init__(color, coords)
        self.name = 'R'
        self.movement_vectors = [(-1,0),(0,1),(1,0),(0,-1)]
        self.movement_range = 7
        self.value = 5
        self.logsindex += 6