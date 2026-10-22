import Piece 

WHITE = 1
BLACK = 2

class Bishop(Piece):
    """Bishop: slides diagonally."""

    def __init__(self, color, coords):
        super().__init__(color, coords)
        self.name = 'B'
        self.movement_vectors = [(-1,1),(1,1),(1,-1),(-1,-1)]
        self.movement_range = 7
        self.value = 3
        self.logsindex += 4