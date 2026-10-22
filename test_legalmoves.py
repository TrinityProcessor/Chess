from chess import Board, WHITE


def moves(board, color=WHITE):
    return board.legalmovesplayer(color)[color - 1][1:]


def targets(board, rank, file, color=WHITE):
    piece = board.sqrsmatrix[rank][file]
    return {(m[0], m[1]) for m in moves(board, color) if m[2] is piece}


FILES = "abcdefgh"


def square_name(square):
    if not (isinstance(square, tuple) and len(square) >= 2):
        return repr(square)
    rank, file = square[0], square[1]
    if isinstance(rank, int) and isinstance(file, int) and 0 <= rank < 8 and 0 <= file < 8:
        return f"{FILES[file]}{rank + 1}"
    return f"OUT_OF_BOUNDS({rank}, {file})"


def pretty_value(value):
    if isinstance(value, set) and all(isinstance(x, tuple) and len(x) >= 2 for x in value):
        ordered = sorted(value)
        return f"{ordered} = {[square_name(x) for x in ordered]}"
    return repr(value)


def print_board(board):
    print("  Board:")
    print("      a b c d e f g h")
    for rank in range(7, -1, -1):
        symbols = []
        for file in range(8):
            square = board.sqrsmatrix[rank][file]
            if getattr(square, "color", 0) == 0:
                symbol = "."
            else:
                symbol = square.name if square.color == WHITE else square.name.lower()
            symbols.append(symbol)
        print(f"    {rank + 1} " + " ".join(symbols) + f" {rank + 1}")
    print("      a b c d e f g h")


def print_generated_moves(board):
    generated = moves(board)
    print(f"  All generated White moves ({len(generated)}):")
    if not generated:
        print("    <none>")
        return
    grouped = {}
    for move in generated:
        if not (isinstance(move, tuple) and len(move) >= 3):
            print(f"    MALFORMED MOVE: {move!r}")
            continue
        target_rank, target_file, piece = move[:3]
        origin = (getattr(piece, "rank", None), getattr(piece, "file", None))
        key = (getattr(piece, "name", "?"), origin)
        grouped.setdefault(key, []).append((target_rank, target_file))
    for (name, origin), destinations in grouped.items():
        labels = [square_name(x) for x in sorted(destinations)]
        print(f"    {name} {square_name(origin)} -> {labels}")


def print_pin_diagnostics(board):
    kings = []
    for row in board.sqrsmatrix:
        for piece in row:
            if getattr(piece, "name", None) == "K" and piece.color == WHITE:
                kings.append(piece)
    if not kings:
        print("  White pin data: no White king found")
        return
    for king in kings:
        try:
            pins = king.pins(board)
            print(f"  Pins detected by king on {square_name((king.rank, king.file))}: {len(pins)}")
            if not pins:
                print("    <none>")
            for index, pin in enumerate(pins, 1):
                pinned, pinner, vector = pin
                print(
                    f"    {index}. pinned={pinned.name}@{square_name((pinned.rank, pinned.file))}, "
                    f"pinner={pinner.name}@{square_name((pinner.rank, pinner.file))}, "
                    f"vector={vector}"
                )
        except Exception as exc:
            print(f"  Pin diagnostic failed: {type(exc).__name__}: {exc}")


def run(case_id, description, fen, check, expected):
    import traceback

    print("=" * 78)
    print(f"TEST {case_id}: {description}")
    print(f"FEN: {fen}")
    try:
        board = Board(case_id)
        board.BoardFromFEN(fen)
        actual = check(board)
        ok = actual == expected

        print(f"RESULT: {'PASS' if ok else 'FAIL'}")
        print(f"Expected: {pretty_value(expected)}")
        print(f"Actual:   {pretty_value(actual)}")

        if not ok:
            if isinstance(expected, set) and isinstance(actual, set):
                missing = expected - actual
                extra = actual - expected
                print(f"Missing moves: {pretty_value(missing)}")
                print(f"Extra moves:   {pretty_value(extra)}")
            elif isinstance(expected, bool):
                print("Boolean mismatch: the tested forbidden/required condition had the opposite result.")

            print_board(board)
            print_pin_diagnostics(board)
            print_generated_moves(board)

        return ok
    except Exception as exc:
        print("RESULT: ERROR")
        print(f"Exception: {type(exc).__name__}: {exc}")
        print("Full traceback:")
        traceback.print_exc()
        try:
            print_board(board)
            print_pin_diagnostics(board)
        except Exception as diagnostic_exc:
            print(f"Additional diagnostics failed: {type(diagnostic_exc).__name__}: {diagnostic_exc}")
        return False


def test_suite():
    cases = [
        # PINS
        ('P1', 'vertically pinned knight has no moves',
         '4r3/8/8/8/8/8/4N3/4K3', lambda b: targets(b,1,4), set()),
        ('P2', 'vertically pinned bishop cannot leave the file',
         '4r3/8/8/8/8/8/4B3/4K3', lambda b: targets(b,1,4), set()),
        ('P3', 'vertically pinned rook may move along the pin line',
         '4r3/8/8/8/8/8/4R3/4K3', lambda b: targets(b,1,4),
         {(2,4),(3,4),(4,4),(5,4),(6,4),(7,4)}),
        ('P4', 'vertically pinned rook never moves sideways',
         '4r3/8/8/8/8/8/4R3/4K3',
         lambda b: any(f != 4 for r,f in targets(b,1,4)), False),
        ('P5', 'diagonally pinned bishop may move along pin line',
         '7q/8/8/8/8/8/1B6/K7', lambda b: targets(b,1,1),
         {(2,2),(3,3),(4,4),(5,5),(6,6),(7,7)}),
        ('P6', 'diagonally pinned rook has no moves',
         '7b/8/8/8/8/8/1R6/K7', lambda b: targets(b,1,1), set()),
        ('P7', 'two allied pieces mean the nearer piece is not pinned',
         '4r3/8/8/8/8/4B3/4R3/4K3', lambda b: len(targets(b,1,4)) > 0, True),
        ('P8', 'enemy blocker prevents a pin',
         '4r3/4p3/8/8/8/8/4N3/4K3', lambda b: len(targets(b,1,4)) > 0, True),

        # BOUNDS
        ('B1', 'corner knight has only two in-bounds moves',
         '8/8/8/8/8/8/7K/N7', lambda b: targets(b,0,0), {(2,1),(1,2)}),
        ('B2', 'corner rook has fourteen in-bounds moves',
         '8/8/8/8/8/8/7K/R7', lambda b: len(targets(b,0,0)), 14),
        ('B3', 'corner bishop has seven in-bounds moves',
         '8/8/8/8/8/8/7K/B7', lambda b: len(targets(b,0,0)), 7),
        ('B4', 'corner king returns only in-bounds coordinates',
         '8/8/8/8/8/8/8/7K',
         lambda b: all(0 <= r < 8 and 0 <= f < 8 for r,f in targets(b,0,7)), True),
        ('B5', 'all queen moves stay inside the board',
         '8/8/8/8/3Q4/8/8/K7',
         lambda b: all(0 <= m[0] < 8 and 0 <= m[1] < 8 for m in moves(b)), True),

        # ALLIED PIECES CANNOT BE TAKEN
        ('A1', 'rook cannot take allied blocker',
         '8/8/8/8/8/P7/8/R6K', lambda b: (2,0) in targets(b,0,0), False),
        ('A2', 'bishop cannot take allied blocker',
         '8/8/8/8/3P4/8/1B6/K7', lambda b: (3,3) in targets(b,1,1), False),
        ('A3', 'knight cannot take allied piece',
         '8/8/8/8/8/2P5/8/N6K', lambda b: (2,2) in targets(b,0,0), False),
        ('A4', 'king cannot take allied piece',
         '8/8/8/8/8/8/4P3/4K3', lambda b: (1,4) in targets(b,0,4), False),
        ('A5', 'pawn cannot capture allied piece diagonally',
         '8/8/8/8/8/3P4/4P3/4K3', lambda b: (2,3) in targets(b,1,4), False),
        ('A6', 'pawn cannot move forward onto allied piece',
         '8/8/8/8/8/4P3/4P3/4K3', lambda b: targets(b,1,4), set()),


        # NO PHASING THROUGH PIECES
        ('O1', 'rook captures enemy blocker but cannot pass it',
         '8/8/8/r7/8/8/8/R6K',
         lambda b: {(r,f) for r,f in targets(b,0,0) if f == 0},
         {(1,0),(2,0),(3,0),(4,0)}),
        ('O2', 'rook stops before allied blocker',
         '8/8/8/P7/8/8/8/R6K',
         lambda b: {(r,f) for r,f in targets(b,0,0) if f == 0},
         {(1,0),(2,0),(3,0)}),
        ('O3', 'bishop captures enemy blocker but cannot pass it',
         '8/8/8/8/3p4/8/1B6/K7',
         lambda b: {(r,f) for r,f in targets(b,1,1) if r == f}, {(2,2),(3,3)}),
        ('O4', 'queen cannot phase through allied diagonal blocker',
         '8/8/8/8/3P4/8/1Q6/K7',
         lambda b: any(r == f and r >= 3 for r,f in targets(b,1,1)), False),
        ('O5', 'pawn double push blocked by occupied intermediate square',
         '8/8/8/8/8/4n3/4P3/4K3', lambda b: targets(b,1,4), set()),
        ('O6', 'pawn may move one but not two when destination is blocked',
         '8/8/8/8/4n3/8/4P3/4K3', lambda b: targets(b,1,4), {(2,4)}),


         # MULTIPLE PIECES TARGETING SAME SQUARE
        ('A7', 'two knights on b1 and f3 can both target d2',
         'r1bqkbnr/pppppppp/8/8/8/5N2/8/RNBQKB1R',
         lambda b: (1,3) in targets(b,0,1) and (1,3) in targets(b,2,5), True),
        ('A8', 'black pawn on e7 can double push to e5',
         '4k3/4p3/8/8/8/8/8/4K3',
         lambda b: (4,4) in targets(b,6,4), True),
    ]

    passed = sum(run(*case) for case in cases)
    print('=' * 65)
    print(f'SUMMARY: {passed}/{len(cases)} passed')
    print('=' * 65)
    return passed == len(cases)


if __name__ == '__main__':
    test_suite()
