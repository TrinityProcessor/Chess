WHITE = 1
BLACK = 2

class Piece():
    """Base class containing state and shared movement generation."""

    def __init__(self, color, coords):
        # Color of the player who owns this piece.
        self.color = color 

        # Current zero-based position as (rank, file). Keeping both values in
        # one tuple makes positions easy to compare, pass into moves, and use
        # for NumPy indexing.
        self.coords = coords

        # Index used by the old piece-log system. This may become unnecessary
        # once each Player owns a collection of its active pieces.
        self.logsindex = color

        # Capture state. A bool would communicate this more clearly than 0/1.
        self.iscaptured = False

        # These lists appear intended as cached results. If they remain, they
        # must be invalidated whenever the position changes.
        self.movesofpiece = []
        self.PseudoLegalMove_list = []

    def PseudoLegalMoves(self, current_board): 
        """Return reachable squares along this piece's movement vectors.

        For each vector, the method advances one square at a time until it
        reaches the piece's maximum range, the board edge, or another piece.
        Empty squares are included. An enemy-occupied square is included as a
        capture, then the scan stops. An allied piece blocks the line.

        This shared implementation suits queens, rooks, bishops, knights, and
        basic king movement. Pawns override it because their movement and
        capture rules are different.
        The intended tuple shape is (target_coords, moving_piece, capture_flag).
        """
        PseudoLegalMove_squares = []

        # A movement vector describes one direction or jump available to the
        # piece, such as (-1, 0) for one rank upward.
        for v in self.movement_vectors:
            # Sliding pieces inspect as many as seven squares in each direction;
            # kings and knights inspect only one target per vector.
            for r in range(self.movement_range):
                r += 1
                PseudoLegalMove_coords = (self.coords[0] + (v[0] * r), self.coords[1] + (v[1] * r))

                # Stop following this vector after it leaves the board.
                if not(0 <= PseudoLegalMove_coords[0] < 8 and 0 <= PseudoLegalMove_coords[1] < 8): break

                PseudoLegalMove_square = current_board.sqrsmatrix[PseudoLegalMove_coords[0]][PseudoLegalMove_coords[1]]

                
                #prevent evaluating the color of a square that holds a None value
                if (PseudoLegalMove_square != None): 
                    # An ally piece may NOT be captured, nor must a piece move beyond it.
                    if (PseudoLegalMove_square.color == self.color): break
                    # An enemy piece may be captured, but no piece can move beyond it.
                    PseudoLegalMove_squares.append((PseudoLegalMove_coords, self, True)); break
                
                # Empty target square: add it and continue for sliding pieces.
                PseudoLegalMove_squares.append((PseudoLegalMove_coords, self, True))

        return PseudoLegalMove_squares