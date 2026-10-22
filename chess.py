import numpy as np
import os
import subprocess

def clear_screen():
    cmd = 'cls' if os.name == 'nt' else 'clear'
    subprocess.run(cmd, shell=True)
VOID = 0
WHITE = 1
BLACK = 2

class GetmovesCallError(Exception):
    def __init__(self, Error_Message):
            self.Error_Message = Error_Message
class FENNotationError(Exception):
    pass
class SquareOccupiedByPlayerError(Exception):
    pass
class MoveViolatesRulesError(Exception):
    pass
class MoveNotationErrorSquareUnreachable(Exception):
    pass
class MoveNotationErrorSquareEmpty(Exception):
    pass
class MoveNotationErrorLackOfSpecification(Exception):
    def __init__(self, candidate_piece_list):
        self.candidate_piece_list = candidate_piece_list
class MoveNotationError(Exception):
    pass

from typing import NamedTuple
class Move(NamedTuple):
    origin: tuple          # (rank, file)
    target: tuple
    piece: object          # the piece that moves
    captured: object = None    # the piece taken, or None
    kind: str = ''         # '', 'check' 'takes', 'castle', 'promotion'
    promotion: object = None   # class chosen on promotion

class Piece():
    def __init__(self, color, rank, file):
        self.color = color #color of placer that owns the piece 
        self.rank = rank
        self.file = file
        self.logsindex = color
        self.iscaptured = 0
        self.movesofpiece = []
        self.control_list = []

#pawn.control(Current_Board): [(Target_rank, Traget_file, Self),]
    def control(self, current_board):
        control_squares = []
        d, Pawn_start_rank = ((-1, 6) if self.color == BLACK else (1, 1))
        for v in self.movement_vectors:
            for r in range(self.movement_range):
                r += 1
                control_rank = self.rank + (v[0] * r * d)
                control_file = self.file + (v[1] * r * d)
                if not(0 <= control_rank < 8 and 0 <= control_file < 8): break
                control_square = current_board.sqrsmatrix[control_rank][control_file]
                # no diagonal movement to void, no captures forward, no double steps from non origin rank
                if (self.name == 'P' and ((control_square.color == VOID and control_file != self.file) or (v[0] == 2 and (self.rank != Pawn_start_rank or current_board.sqrsmatrix[self.rank + d][self.file].color != VOID)) or (control_square.file == self.file and control_square.color != VOID))): continue
                if (control_square.color == self.color): break
                if (control_square.color != VOID): control_squares.append((control_rank, control_file ,self)); break
                control_squares.append((control_rank, control_file ,self))
        return control_squares

    def __str__(self):
        return f'{IntToColor_dict[self.color]} {names_dict[self.name]}, in {MatrixToSAN_file_dict[self.file]}{MatrixToSAN_rank_dict[self.rank]}'
class King(Piece):
    def __init__(self, color, rank, file):
        super().__init__(color, rank, file)
        self.name = 'K'
        self.movement_vectors = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
        self.movement_range = 1
        self.value = 39
        self.logsindex += 10
    def pins(self, board):
        pinned = []
        for v in self.movement_vectors:
            pinned_list = []
            for r in range(self.movement_range+6):
                r += 1
                target_rank = self.rank + v[0] * r
                target_file = self.file + v[1] * r
                if not(0 <= target_rank < 8 and 0 <= target_file < 8): break
                target_square = board.sqrsmatrix[target_rank][target_file]
                if target_square.color == self.color: 
                    pinned_list.append(target_square)
                    if len(pinned_list) > 1: break
                elif target_square.color != VOID:
                    if (target_square.color not in (VOID, self.color)
                        and v in target_square.movement_vectors 
                        and r <= target_square.movement_range 
                        and len(pinned_list) == 1): 
                        pinned_list.append(target_square)
                        pinned_list.append(v)
                        pinned.append(tuple(pinned_list))
                    break
        return pinned

class Queen(Piece):
    def __init__(self, color, rank, file):
        super().__init__(color, rank, file)
        self.name = 'Q'
        self.movement_vectors = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
        self.movement_range = 7
        self.value = 9
        self.logsindex += 8
class Rook(Piece):
    def __init__(self, color, rank, file):
        super().__init__(color, rank, file)
        self.name = 'R'
        self.movement_vectors = [(-1,0),(0,1),(1,0),(0,-1)]
        self.movement_range = 7
        self.value = 5
        self.logsindex += 6
class Bishop(Piece):
    def __init__(self, color, rank, file):
        super().__init__(color, rank, file)
        self.name = 'B'
        self.movement_vectors = [(-1,1),(1,1),(1,-1),(-1,-1)]
        self.movement_range = 7
        self.value = 3
        self.logsindex += 4
class Knight(Piece):
    def __init__(self, color, rank, file):
        super().__init__(color, rank, file)
        self.name = 'N'
        self.movement_vectors = [(-2,1),(-1,2),(1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1)]
        self.movement_range = 1
        self.value = 3
        self.logsindex += 2
class Pawn(Piece):
    def __init__(self, color, rank, file):
        super().__init__(color, rank, file)
        self.name = 'P'
        self.movement_vectors = [(1,0),(2,0),(1,-1),(1,1)]
        self.movement_range = 1
        self.value = 1
        self.logsindex += 0

class Void(Piece):
    def __init__(self, color, rank, file):
        super().__init__(color, rank, file)
        self.name = 'Void'
        self.movement_vectors = []
        self.movement_range = range(1,1)
        self.logsindex += 0
        self.value = 0

class Board():
    def __init__(self, name):
            self.name = name
            self.sqrsmatrix = np.empty((8, 8), dtype=object)
            self.BoardFromFEN(FEN_Initial_Position) 
            self.P1LegalMoves = []
            self.P2LegalMoves = []
            self.LastMove = ['Move', 'Piece']

    def legalmovesplayer(self, PlayerColor):
        self.P1LegalMoves, self.P2LegalMoves = [], []
        for piecetype in reversed(self.logs[1:]):
            for piece in piecetype[1:]:
                if piecetype[1].color != PlayerColor: break
                if piece.name == 'K': pins = piece.pins(self)
                piece_pseudomoves = piece.control(self)
                for pseudomove in piece_pseudomoves:
                        Pseudomove_vector = (pseudomove[0]-piece.rank, pseudomove[1]-piece.file)
                        if (piece.color != PlayerColor) or (len(pins) > 0 and piece.name != 'K' and any(pin[0] is piece for pin in pins) and not any(pin[0] is piece and Pseudomove_vector ==(pin[2][0] * n, pin[2][1] * n, ) for pin in pins for n in range(-7,8) if n != 0)): continue
                        self.P1LegalMoves.append(pseudomove) if PlayerColor == WHITE else self.P2LegalMoves.append(pseudomove)
        if PlayerColor == WHITE: return self.P1LegalMoves
        if PlayerColor == BLACK: return self.P2LegalMoves

    def BoardFromFEN(self, FEN):
        self.logs = [
            [('Void',VOID),],
            [('P',WHITE),],[('P',BLACK),],
            [('N',WHITE),],[('N',BLACK),],
            [('B',WHITE),],[('B',BLACK),],
            [('R',WHITE),],[('R',BLACK),],
            [('Q',WHITE),],[('Q',BLACK),],
            [('K',WHITE),],[('K',BLACK),],
            ]
        placement = FEN.split(' ')[0]
        FEN_list = placement.split('/')
        if len(FEN_list) != 8:
            raise FENNotationError(f"Expected 8 ranks, got {len(FEN_list)}")
        for rank, row in enumerate(FEN_list[::-1]):
            file = 0
            for char in row:
                if char in '12345678': width = int(char)
                elif char in pieces_dict: width = 1
                else: raise FENNotationError(f"Invalid character '{char}' in rank {rank + 1}")
                if file + width > 8: raise FENNotationError(f"Rank {rank + 1} has more than 8 squares")
                if char in pieces_dict:
                    piece_class, color = pieces_dict[char]
                    piece = piece_class(color, rank, file)
                    self.sqrsmatrix[rank][file] = piece
                    self.logs[piece.logsindex].append(piece)
                else:
                    for i in range(width): self.sqrsmatrix[rank][file + i] = Void(VOID, rank, file + i)
                file += width
            if file != 8: raise FENNotationError(f"Rank {rank + 1} has only {file} squares")
    def findpiece(self, PlayerColor, MSANI): #MSANI is the move after being interpreted by the SAN interpreter
        self.legalmovesplayer(PlayerColor)
        typeop, target_square, origin_rank, origin_file = MSANI[0], (MSANI[1], MSANI[2]), MSANI[3], MSANI[4]
        MovesCandidates = []
        LegalMovesForPlayer = self.P1LegalMoves if PlayerColor == WHITE else self.P2LegalMoves
        for LegalMove in LegalMovesForPlayer:
            if target_square == (LegalMove[0], LegalMove[1]) and (typeop == LegalMove[2].name):
                if ((origin_rank !=None) and (LegalMove[2].rank != origin_rank) or (origin_file !=None) and (LegalMove[2].file != origin_file)): continue
                MovesCandidates.append((LegalMove))
            else: continue
        if len(MovesCandidates) == 0: raise MoveNotationErrorSquareUnreachable  
        if len(MovesCandidates) > 1: raise MoveNotationErrorLackOfSpecification(MovesCandidates)
        return MovesCandidates[0]
    def SAN_interpreter(self, user_SAN):
        user_SAN_pfrtt = user_SAN.replace('x','').replace('+','').replace('#','')
        if len(user_SAN_pfrtt) < 2: raise MoveNotationError
        if user_SAN_pfrtt[-2] in files and user_SAN_pfrtt[-1] in ranks:
            if user_SAN_pfrtt[-2] not in notation_SAN_dict or user_SAN_pfrtt[-1] not in notation_SAN_dict: raise MoveNotationError
            target_rank, target_file, user_SAN_pfr = notation_SAN_dict[user_SAN_pfrtt[-2:][1]], notation_SAN_dict[user_SAN_pfrtt[-2:][0]], user_SAN_pfrtt[:-2] 
            typeop, user_SAN_fr = (user_SAN_pfr[:1], user_SAN_pfr[1:]) if user_SAN_pfr[:1] in ('N','B','R','Q','K') else ('P', user_SAN_pfr)
            if len(user_SAN_fr) == 2 and user_SAN_fr[0] in files and user_SAN_fr[1] in ranks:
                origin_file, origin_rank = notation_SAN_dict[user_SAN_fr[0]], notation_SAN_dict[user_SAN_fr[1]]
            elif len(user_SAN_fr) == 1 and user_SAN_fr[0] in files: origin_rank, origin_file = None, notation_SAN_dict[user_SAN_fr[:1]]
            elif len(user_SAN_fr) == 1 and user_SAN_fr[0] in ranks: origin_rank, origin_file = notation_SAN_dict[user_SAN_fr[:1]], None
            elif len(user_SAN_fr) == 0: origin_rank, origin_file = None, None
            else: raise MoveNotationError
        else:
            raise MoveNotationError
        return (typeop, target_rank, target_file, origin_rank, origin_file)
    def move_piece(self, PlayerColor, User_move):
        try:
            target_rank, target_file, piece = self.findpiece(PlayerColor, self.SAN_interpreter(User_move))
            target_square = (target_rank, target_file)
            self.sqrsmatrix[piece.rank][piece.file] = Void(VOID,piece.rank,piece.file)
            victim = self.sqrsmatrix[target_square[0]][target_square[1]] if self.sqrsmatrix[target_square[0]][target_square[1]].name != 'Void' else None
            if victim != None: self.logs[victim.logsindex].remove(victim)
            self.sqrsmatrix[target_square[0]][target_square[1]] = piece
            piece.rank = target_square[0]
            piece.file = target_square[1]
            return 1
        except MoveNotationErrorLackOfSpecification: raise MoveNotationErrorSquareUnreachable
        except MoveNotationErrorSquareUnreachable: raise MoveNotationErrorSquareUnreachable
        except MoveNotationErrorSquareEmpty: raise MoveNotationErrorSquareEmpty
        except MoveNotationError: raise MoveNotationError

notation_SAN_dict = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7,
                     '1':0, '2':1, '3':2, '4':3, '5':4, '6':5, '7':6, '8':7}
MatrixToSAN_rank_dict = {0:'1', 1:'2', 2:'3', 3:'4', 4:'5', 5:'6', 6:'7', 7:'8'}
MatrixToSAN_file_dict = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
IntToColor_dict = {0:'Void', 1:'White', 2:'Black'}
names_dict = {'P':'Pawn','N':'Knight','B':'Bishop','R':'Rook','Q':'Queen','K':'King',}

files = ('a','b','c','d','e','f','g','h')
ranks = ('1','2','3','4','5','6','7','8')
    
pieces_dict = {'P': (Pawn,WHITE),'N': (Knight,WHITE),'B': (Bishop,WHITE),'R': (Rook,WHITE),'Q': (Queen,WHITE,),'K': (King,WHITE),
               'p': (Pawn,BLACK),'n': (Knight,BLACK),'b': (Bishop,BLACK),'r': (Rook,BLACK),'q': (Queen,BLACK),'k': (King,BLACK)}
FEN_Initial_Position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'
FEN_pieces = ['K','k','Q','q','R','r','B','b','N','n','P','p',]
    
def show(board):
    symbols = {
        (WHITE, Pawn): '♟', (WHITE, Knight): '♞', (WHITE, Bishop): '♝',
        (WHITE, Rook): '♜', (WHITE, Queen): '♛',  (WHITE, King): '♚',
        (BLACK, Pawn): '♙', (BLACK, Knight): '♘', (BLACK, Bishop): '♗',
        (BLACK, Rook): '♖', (BLACK, Queen): '♕',  (BLACK, King): '♔',
    }
    print(board.name)
    for row in board.sqrsmatrix[::-1]:
        row_str = []
        for cell in row:
            if isinstance(cell, Void):
                cell_str = '■' if (cell.rank + cell.file) % 2 else '□'
            else:
                cell_str = symbols[(cell.color, type(cell))]
            row_str.append(cell_str)
        print(' '.join(row_str))
    print()


Playing_Board = Board("Playing board")
for _ in Playing_Board.logs[1:]:
    for piece in _[1:]:
        print(piece)

Player = 0
while True:
    HasMoved = False
    Player = (Player) %2 + 1
    error_message = ""
    while HasMoved == False:
        clear_screen()
        show(Playing_Board)
        try:
            User_move = input(
                f'Input your move in standart SAN noation\n'
                f'{error_message}'
                f'{IntToColor_dict[Player]} to move\n'
                )
            Playing_Board.move_piece(Player, User_move)
            HasMoved = True
        except MoveNotationErrorLackOfSpecification:
            error_message = '2 pieces can move to that square, specify which piece you want to move\n'
        except MoveNotationErrorSquareUnreachable: 
            error_message = 'None of your pieces can reach that square, select another move\n'
        except MoveNotationErrorSquareEmpty: 
            error_message = 'There is no piece on the square you specified\n'
        except MoveNotationError: 
            error_message = 'Move notaion invalid\n'