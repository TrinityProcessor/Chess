import Piece

WHITE = 1
BLACK = 2

class Pawn(Piece):
    """Pawn with color-dependent forward movement and diagonal captures."""

    def __init__(self, color, coords):
        super().__init__(color, coords)
        self.name = 'P'

        # These vectors mix movement and captures:
        # (1, 0)  = one-square push
        # (2, 0)  = initial two-square push
        # (1, -1) and (1, 1) = diagonal captures
        self.movement_vectors = [(1,0),(2,0),(1,-1),(1,1)]
        self.movement_range = 1
        self.value = 1
        self.logsindex += 0

    def PseudoLegalMoves(self, current_board):
        """Return the pawn's currently available pseudo-legal destinations.

        Direction and starting rank depend on color. Forward movement requires
        empty squares, while diagonal movement requires an enemy piece.

        Despite the method name, this is not a pure pawn attack map because it
        includes forward pushes and excludes empty diagonal squares. A separate
        attack/PseudoLegalMove method will be needed for king safety and castling.
        The intended tuple shape is (target_rank, target_file, moving_piece, capture_flag).
        """
        PseudoLegalMove_squares = []

        # Black moves toward decreasing matrix ranks from rank 6. White moves
        # toward increasing matrix ranks from rank 1 in this board orientation.
        d, Pawn_start_rank = ((-1, 6) if self.color == BLACK else (1, 1))

        for v in self.movement_vectors:
            for r in range(self.movement_range):
                r += 1
                PseudoLegalMove_coords = (self.coords[0] + (v[0] * r * d), self.coords[1] + (v[1] * r * d))

                # Ignore this vector if its destination is outside the board.
                if not(0 <= PseudoLegalMove_coords[0] < 8 and 0 <= PseudoLegalMove_coords[1] < 8): break

                PseudoLegalMove_square = current_board.sqrsmatrix[PseudoLegalMove_coords[0]][PseudoLegalMove_coords[1]]

                # Intended restrictions:
                # 1. A pawn cannot move diagonally into an empty square.
                # 2. A double push is allowed only from the starting rank and
                #    only if the square directly ahead is also empty.
                # 3. A pawn cannot capture or move into an occupied forward square.
                if (
                    (PseudoLegalMove_square == None and PseudoLegalMove_coords[1] != self.coords[1]) 
                    or (
                        v[0] == 2 
                        and (
                            self.coords[0] != Pawn_start_rank 
                            or current_board.sqrsmatrix[self.coords[0] + d][self.coords[1]] != None
                        )
                    )
                    or (PseudoLegalMove_coords[1] == self.coords[1] and PseudoLegalMove_square != None)
                ): 
                    continue

                #prevent evaluating the color of a square that holds a None value
                if (PseudoLegalMove_square != None): 
                    #Square Occupied by piece of same color
                    if (PseudoLegalMove_square.color == self.color): break
                    # Occupied diagonal target: include the capture and stop.
                    PseudoLegalMove_squares.append((PseudoLegalMove_coords, self, True)); break

                # Empty forward target: include the pawn push.
                PseudoLegalMove_squares.append((PseudoLegalMove_coords, self, False))

        return PseudoLegalMove_squares