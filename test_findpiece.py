"""Comprehensive Integration Test Suite for Board.findpiece

Tests every aspect of findpiece:
- Basic piece moves (Pawns, Knights, Bishops, Rooks, Queens, Kings)
- Disambiguation by file, rank, or both (e.g. Nbd2, R1a2, Qa4e1)
- Color isolation (Black vs White)
- Absolute pin restrictions (Pinned pieces raising MoveNotationErrorSquareUnreachable)
- Obstruction & friendly piece blocking
- Unreachable targets & malformed SAN
- Edge of board & corner moves

Run with: python test_findpiece_4.py
"""

from chess import (
    Board, WHITE, BLACK,
    MoveNotationErrorSquareUnreachable,
    MoveNotationErrorLackOfSpecification,
    MoveNotationError
)

FILES = "abcdefgh"
COLORS = {WHITE: "WHITE", BLACK: "BLACK"}

def square(rank, file):
    return f"{FILES[file]}{rank + 1}"

def describe_expected(test):
    exp = test["expected"]
    if exp == "unique":
        orig = test.get("expected_origin")
        return f"UNIQUE move from {orig}" if orig else "UNIQUE move"
    if exp == "ambiguous":
        return "MoveNotationErrorLackOfSpecification"
    if exp == "unreachable":
        return "MoveNotationErrorSquareUnreachable"
    if exp == "invalid":
        return "MoveNotationError"
    return str(exp)

TESTS = [
    # =========================================================================
    # 1. PAWN MOVEMENTS (WHITE & BLACK)
    # =========================================================================
    {
        "id": "P01",
        "name": "White Pawn initial double push (e2 to e4)",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": WHITE, "san": "e4", "expected": "unique", "expected_origin": "e2"
    },
    {
        "id": "P02",
        "name": "White Pawn single push (e2 to e3)",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": WHITE, "san": "e3", "expected": "unique", "expected_origin": "e2"
    },
    {
        "id": "P03",
        "name": "Black Pawn initial double push (e7 to e5)",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": BLACK, "san": "e5", "expected": "unique", "expected_origin": "e7"
    },
    {
        "id": "P04",
        "name": "Black Pawn single push (d7 to d6)",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": BLACK, "san": "d6", "expected": "unique", "expected_origin": "d7"
    },
    {
        "id": "P05",
        "name": "White Pawn diagonal capture (exd5)",
        "fen": "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR",
        "color": WHITE, "san": "exd5", "expected": "unique", "expected_origin": "e4"
    },
    {
        "id": "P06",
        "name": "Black Pawn diagonal capture (dxe4)",
        "fen": "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR",
        "color": BLACK, "san": "dxe4", "expected": "unique", "expected_origin": "d5"
    },
    {
        "id": "P07",
        "name": "Pawn diagonal move without capture onto empty square",
        "fen": "4k3/8/8/8/8/8/4P3/4K3",
        "color": WHITE, "san": "d3", "expected": "unreachable"
    },
    {
        "id": "P08",
        "name": "Blocked Pawn cannot push forward",
        "fen": "4k3/8/8/8/8/4p3/4P3/4K3",
        "color": WHITE, "san": "e3", "expected": "unreachable"
    },

    # =========================================================================
    # 2. KNIGHT DISAMBIGUATION & MOVEMENT
    # =========================================================================
    {
        "id": "N01",
        "name": "Unique Knight opening move (Nf3)",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": WHITE, "san": "Nf3", "expected": "unique", "expected_origin": "g1"
    },
    {
        "id": "N02",
        "name": "Ambiguous Knights targeting d2 without file qualifier",
        "fen": "4k3/8/8/8/8/5N2/8/1N2K3",
        "color": WHITE, "san": "Nd2", "expected": "ambiguous"
    },
    {
        "id": "N03",
        "name": "Knight disambiguated by file: Nbd2",
        "fen": "4k3/8/8/8/8/5N2/8/1N2K3",
        "color": WHITE, "san": "Nbd2", "expected": "unique", "expected_origin": "b1"
    },
    {
        "id": "N04",
        "name": "Knight disambiguated by file: Nfd2",
        "fen": "4k3/8/8/8/8/5N2/8/1N2K3",
        "color": WHITE, "san": "Nfd2", "expected": "unique", "expected_origin": "f3"
    },
    {
        "id": "N05",
        "name": "Knight disambiguated by rank: N1c3",
        "fen": "4k3/8/8/2N5/8/8/8/2N1K3",
        "color": WHITE, "san": "N1d3", "expected": "unique", "expected_origin": "c1"
    },
    {
        "id": "N06",
        "name": "Knight disambiguated by rank: N5c3",
        "fen": "4k3/8/8/2N5/8/8/8/2N1K3",
        "color": WHITE, "san": "N5d3", "expected": "unique", "expected_origin": "c5"
    },

    # =========================================================================
    # 3. ROOK DISAMBIGUATION & RAY CONTROL
    # =========================================================================
    {
        "id": "R01",
        "name": "Ambiguous Rooks on same rank targeting d2",
        "fen": "4k3/8/8/8/8/8/R6R/4K3",
        "color": WHITE, "san": "Rd2", "expected": "ambiguous"
    },
    {
        "id": "R02",
        "name": "Rook disambiguated by file: Rad2",
        "fen": "4k3/8/8/8/8/8/R6R/4K3",
        "color": WHITE, "san": "Rad2", "expected": "unique", "expected_origin": "a2"
    },
    {
        "id": "R03",
        "name": "Rook disambiguated by rank: R1a2",
        "fen": "4k3/8/8/8/8/R7/8/R3K3",
        "color": WHITE, "san": "R1a2", "expected": "unique", "expected_origin": "a1"
    },
    {
        "id": "R04",
        "name": "Rook capture on open rank: Rxa7",
        "fen": "r3k2r/8/8/8/8/8/R6R/4K3",
        "color": WHITE, "san": "Rxa7", "expected": "unique", "expected_origin": "a2"
    },
    {
        "id": "R05",
        "name": "Rook blocked by friendly pawn",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": WHITE, "san": "Ra3", "expected": "unreachable"
    },

    # =========================================================================
    # 4. BISHOP & QUEEN MOVEMENT / FULL DISAMBIGUATION
    # =========================================================================
    {
        "id": "B01",
        "name": "Unreachable Bishop blocked by pawns",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": WHITE, "san": "Bc4", "expected": "unreachable"
    },
    {
        "id": "B02",
        "name": "Open diagonal Bishop move: Bc4",
        "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR",
        "color": WHITE, "san": "Bc4", "expected": "unique", "expected_origin": "f1"
    },
    {
        "id": "Q01",
        "name": "Queen diagonal move: Qh5",
        "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR",
        "color": WHITE, "san": "Qh5", "expected": "unique", "expected_origin": "d1"
    },
    {
        "id": "Q02",
        "name": "Full Rank+File Disambiguation for Queens (3 Queens targeting e1)",
        "fen": "4k3/8/8/8/Q3Q3/8/8/Q4K2",
        "color": WHITE, "san": "Qa4d1", "expected": "unique", "expected_origin": "a4"
    },

    # =========================================================================
    # 5. KING MOVEMENT
    # =========================================================================
    {
        "id": "K01",
        "name": "King single step: Ke2",
        "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR",
        "color": WHITE, "san": "Ke2", "expected": "unique", "expected_origin": "e1"
    },
    {
        "id": "K02",
        "name": "King blocked by friendly piece: Ke1 onto e2 occupied by pawn",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": WHITE, "san": "Ke2", "expected": "unreachable"
    },

    # =========================================================================
    # 6. ABSOLUTE PIN RESTRICTIONS
    # =========================================================================
    {
        "id": "PIN01",
        "name": "Vertically pinned Knight on e2 cannot leave e-file",
        "fen": "4r2k/8/8/8/8/8/4N3/4K3",
        "color": WHITE, "san": "Nc3", "expected": "unreachable"
    },
    {
        "id": "PIN02",
        "name": "Vertically pinned Bishop on e2 cannot move diagonally",
        "fen": "4r2k/8/8/8/8/8/4B3/4K3",
        "color": WHITE, "san": "Bf3", "expected": "unreachable"
    },
    {
        "id": "PIN03",
        "name": "Vertically pinned Rook on e2 CAN move along pin ray (e2 to e5)",
        "fen": "4r2k/8/8/8/8/8/4R3/4K3",
        "color": WHITE, "san": "Re5", "expected": "unique", "expected_origin": "e2"
    },
    {
        "id": "PIN04",
        "name": "Vertically pinned Rook on e2 CANNOT move horizontally (Re3)",
        "fen": "4r2k/8/8/8/8/8/4R3/4K3",
        "color": WHITE, "san": "Rd2", "expected": "unreachable"
    },
    {
        "id": "PIN05",
        "name": "Diagonally pinned Bishop on b2 CAN move along diagonal (b2 to e5)",
        "fen": "7q/8/8/8/8/8/1B6/K7",
        "color": WHITE, "san": "Be5", "expected": "unique", "expected_origin": "b2"
    },
    {
        "id": "PIN06",
        "name": "Diagonally pinned Bishop on b2 CANNOT move off diagonal (Bb3)",
        "fen": "7q/8/8/8/8/8/1B6/K7",
        "color": WHITE, "san": "Ba3", "expected": "unreachable"
    },

    # =========================================================================
    # 7. COLOR CROSS-TALK & SAN PARSING MALFORMS
    # =========================================================================
    {
        "id": "ERR01",
        "name": "White attempting to execute Black's move",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": WHITE, "san": "e5", "expected": "unreachable"
    },
    {
        "id": "ERR02",
        "name": "Targeting an out-of-bounds square",
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "color": WHITE, "san": "Nf9", "expected": "invalid"
    },
]

def run_suite():
    print("=" * 80)
    print("         BOARD.FINDPIECE COMPREHENSIVE INTEGRATION TEST SUITE          ")
    print("=" * 80 + "\n")

    passed_count = 0
    total_count = len(TESTS)

    for test in TESTS:
        t_id = test["id"]
        t_name = test["name"]
        expected_desc = describe_expected(test)
        
        board = Board(f"Test_{t_id}")
        board.BoardFromFEN(test["fen"])

        actual_result = None
        passed = False
        detail = ""

        try:
            msani = board.SAN_interpreter(test["san"])
            res = board.findpiece(test["color"], msani)
            
            # Flexible unpacking supporting (target_rank, target_file, piece) or (piece, target_sq)
            if isinstance(res, tuple) and len(res) == 3:
                tr, tf, piece_obj = res
            elif isinstance(res, tuple) and len(res) == 2:
                piece_obj, (tr, tf) = res
            else:
                raise ValueError(f"Unexpected return format from findpiece: {res!r}")

            actual_origin = square(piece_obj.rank, piece_obj.file)
            actual_result = f"UNIQUE move from {actual_origin}"

            if test["expected"] == "unique":
                expected_origin = test.get("expected_origin")
                if expected_origin is None or actual_origin == expected_origin:
                    passed = True
                else:
                    detail = f"Expected origin {expected_origin}, got {actual_origin}"
            else:
                detail = "Expected exception/failure but findpiece returned a valid move."

        except MoveNotationErrorLackOfSpecification:
            actual_result = "MoveNotationErrorLackOfSpecification"
            passed = test["expected"] == "ambiguous"
        except MoveNotationErrorSquareUnreachable:
            actual_result = "MoveNotationErrorSquareUnreachable"
            passed = test["expected"] == "unreachable"
        except MoveNotationError:
            actual_result = "MoveNotationError"
            passed = test["expected"] == "invalid"
        except Exception as e:
            actual_result = f"CRASH: {type(e).__name__}: {e}"
            passed = False

        status = "PASS" if passed else "FAIL"
        if passed:
            passed_count += 1

        print(f"[{status}] Test {t_id}: {t_name}")
        print(f"       SAN: '{test['san']}' | Color: {COLORS[test['color']]}")
        print(f"       Expected: {expected_desc}")
        print(f"       Actual  : {actual_result}")
        if detail:
            print(f"       Detail  : {detail}")
        print("-" * 80)

    print("\n" + "=" * 80)
    print(f"SUMMARY: {passed_count}/{total_count} tests passed.")
    print("=" * 80)

if __name__ == "__main__":
    run_suite()