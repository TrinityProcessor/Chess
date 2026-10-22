# Chess

Chess is primarily a terminal-based chess environment. The board is displayed in the terminal, and moves are entered using **Standard Algebraic Notation (SAN)**.

Chess positions can be loaded using **Forsyth-Edwards Notation (FEN)**.

## Running the Program

Run the program with:

```bash
python chess.py
```

> If your main Python file has a different name, replace `chess.py` with that filename.

## Entering Moves with SAN

SAN describes a chess move using the moving piece and its destination square.

### Piece Letters

| Piece | Letter |
|---|---|
| Pawn | No letter |
| Knight | `N` |
| Bishop | `B` |
| Rook | `R` |
| Queen | `Q` |
| King | `K` |

The letter `K` is reserved for the king, so knights use `N`.

### Board Squares

Each square is identified using:

```text
file + rank
```

- Files are the columns `a` through `h`.
- Ranks are the rows `1` through `8`.

Examples:

- `e4` moves a pawn to e4.
- `Nf3` moves a knight to f3.
- `Bb5` moves a bishop to b5.

### Captures

Captures are written using `x`.

Examples:

- `Nxe5` means that a knight captures the piece on e5.
- `Bxc6` means that a bishop captures the piece on c6.
- `exd5` means that the pawn on the e-file captures a piece on d5.

### Special Moves

- Kingside castling: `O-O`
- Queenside castling: `O-O-O`
- Check: add `+`, such as `Bb5+`
- Checkmate: add `#`, such as `Qh7#`
- Promotion: add the promoted piece, such as `e8=Q`

When two identical pieces can move to the same square, SAN includes extra information to identify the piece:

- `Nbd2`
- `R1e2`

## Loading Boards with FEN

A FEN string describes a complete chess position. It contains six fields:

```text
piece placement active color castling rights en-passant target halfmove clock fullmove number
```

For example, the standard starting position is:

```text
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

### 1. Piece Placement

The board is described rank by rank, starting with rank 8 and ending with rank 1. Each rank is separated by `/`.

```text
8th rank / 7th rank / 6th rank / ... / 1st rank
```

Pieces are represented by letters:

| Piece | White | Black |
|---|---|---|
| Pawn | `P` | `p` |
| Knight | `N` | `n` |
| Bishop | `B` | `b` |
| Rook | `R` | `r` |
| Queen | `Q` | `q` |
| King | `K` | `k` |

A number represents that many consecutive empty squares.

For example:

```text
4K3
```

means:

```text
[empty][empty][empty][empty][King][empty][empty][empty]
```

### 2. Active Color

The active color indicates whose turn it is:

- `w` means White to move.
- `b` means Black to move.

### 3. Castling Rights

Available castling rights are represented by:

- `K`: White can castle kingside.
- `Q`: White can castle queenside.
- `k`: Black can castle kingside.
- `q`: Black can castle queenside.
- `-`: Neither side has castling rights.

For example, `KQkq` means that both players can castle on either side.

### 4. En Passant Target

This field contains the square behind a pawn that has just moved two squares.

For example, after White plays `e4`, the en passant target square is:

```text
e3
```

If there is no en passant target, this field is `-`.

### 5. Halfmove Clock

The halfmove clock counts the number of half-moves since the last pawn move or capture. It is used for the fifty-move rule.

### 6. Fullmove Number

The fullmove number starts at `1` and increases after every Black move.

## Example Starting Position

```text
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

This represents:

- The standard starting arrangement
- White to move
- All castling rights available
- No en passant target
- A halfmove clock of `0`
- Fullmove number `1`
