import Piece

WHITE = 1
BLACK = 2

class King(Piece):
    """King: moves one square in any direction."""

    def __init__(self, color, coords):
        super().__init__(color, coords)
        self.name = 'K'

        # All eight adjacent directions.
        self.movement_vectors = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
        self.movement_range = 1
        self.value = 39
        self.logsindex += 10

    def pins(self, board):
        """Find allied pieces aligned between this king and an enemy slider.

        Each returned tuple contains the single allied piece blocking the line,
        the enemy sliding piece behind it, and the direction vector from the
        king. This checks ranks, files, and diagonals in all eight directions.

        This method detects geometric absolute pins only. The Board should still
        determine legal moves by checking king safety after a simulated move.
        """
        pinned = []

        # Reuse the king's eight directions as rays extending from the king.
        for v in self.movement_vectors:
            pinned_list = []

            # The king moves one square, but pin detection must inspect the rest
            # of the ray, so movement_range + 6 gives a maximum distance of 7.
            for r in range(self.movement_range+6):
                r += 1
                target_coords = (self.coords[0] + v[0] * r,self.coords[1] + v[1] * r)

                # Stop scanning this ray at the board edge.
                if not(0 <= target_coords[0] < 8 and 0 <= target_coords[1] < 8): break

                target_square = board.sqrsmatrix[target_coords[0]][target_coords[1]]\

                if target_square == None: continue
                if target_square.color == self.color:
                    # The first allied piece is a possible pinned piece.
                    pinned_list.append(target_square)

                    # Two allied pieces block the ray, so neither is pinned to
                    # the king by a piece farther along this direction.
                    if len(pinned_list) > 1: break

                # An enemy piece creates a pin only when exactly one allied
                # piece stands between it and the king, and when the enemy
                # can slide toward the king along this vector.
                if (
                    target_square.color != self.color
                    and v in target_square.movement_vectors 
                    and r <= target_square.movement_range 
                    and len(pinned_list) == 1
                ): 
                    pinned_list.append(target_square)
                    pinned_list.append(v)
                    pinned.append(tuple(pinned_list))
                break
        return pinned