import pygame
import math
import copy
from collections import defaultdict

class Constants:
    ROWS = 8
    COLS = 8
    SQUARE_SIZE = None
    RED = (255, 0, 0)         # Player pieces
    WHITE = (255, 255, 255)   # AI pieces
    BLACK = (0, 0, 0)         # Dark squares
    GREY = (200, 200, 200)    # Light squares
    BLUE = (100, 100, 255)    # Move indicators
    GREEN = (100, 255, 100)   # Selection highlight

CROWN = pygame.transform.scale(pygame.image.load('crown.png'), (44, 25))

class Piece:
    PADDING = 20
    OUTLINE = 3

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = Constants.SQUARE_SIZE * self.col + Constants.SQUARE_SIZE // 2
        self.y = Constants.SQUARE_SIZE * self.row + Constants.SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = Constants.SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, Constants.GREY, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width()//2, self.y - CROWN.get_height()//2))

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

class Board:
    
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()


    def copy(self):
        # Create a deep copy of the board
        new_board = Board()
        new_board.board = [row[:] for row in self.board]
        new_board.red_left = self.red_left
        new_board.white_left = self.white_left
        new_board.red_kings = self.red_kings
        new_board.white_kings = self.white_kings
        return new_board


    def draw_squares(self, win):
        win.fill(Constants.GREY)
        for row in range(Constants.ROWS):
            for col in range(row % 2, Constants.COLS, 2):
                pygame.draw.rect(win, Constants.BLACK, 
                               (row * Constants.SQUARE_SIZE, 
                                col * Constants.SQUARE_SIZE, 
                                Constants.SQUARE_SIZE, 
                                Constants.SQUARE_SIZE))

    def draw(self, win):
        self.draw_squares(win)
        for row in range(Constants.ROWS):
            for col in range(Constants.COLS):
                piece = self.board[row][col]
                if piece:
                    piece.draw(win)

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)
        if row == Constants.ROWS - 1 or row == 0:
            piece.make_king()
            if piece.color == Constants.WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def create_board(self):
        for row in range(Constants.ROWS):
            self.board.append([])
            for col in range(Constants.COLS):
                if col % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, col, Constants.WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, Constants.RED))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == Constants.RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))

        if piece.color == Constants.WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, Constants.ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, Constants.ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break
            current = self.board[r][left]
            if current is None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last
                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, Constants.ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            left -= 1
        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= Constants.COLS:
                break
            current = self.board[r][right]
            if current is None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last
                if last:
                    if step == -1:
                        row = max(r - 3, 0)
                    else:
                        row = min(r + 3, Constants.ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]
            right += 1
        return moves

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = None
            if piece is not None:
                if piece.color == Constants.RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.red_left <= 0:
            return Constants.WHITE
        elif self.white_left <= 0:
            return Constants.RED
        
        red_moves = self.get_all_valid_moves(Constants.RED)
        white_moves = self.get_all_valid_moves(Constants.WHITE)

        if not red_moves:
            return Constants.WHITE
        elif not white_moves:
            return Constants.RED

        return None

    def get_all_valid_moves(self, color):
        moves = []
        for piece in self.get_all_pieces(color):
            valid_moves = self.get_valid_moves(piece)
            moves.extend(valid_moves.keys())
        return moves

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece and piece.color == color:
                    pieces.append(piece)
        return pieces

    def evaluate(self):
        return (self.white_left - self.red_left + 
                (self.white_kings * 0.5 - self.red_kings * 0.5))

def minimax(position, depth, maximizing_player):
    if depth == 0 or position.winner() is not None:
        return position.evaluate(), position

    if maximizing_player:
        return max_value(position, depth)
    else:
        return min_value(position, depth)

def max_value(position, depth):
    max_eval = -math.inf
    best_move = None
    
    for move in get_all_moves(position, Constants.WHITE):
        evaluation, _ = minimax(move, depth - 1, False)
        if evaluation > max_eval:
            max_eval = evaluation
            best_move = move
            
    return max_eval, best_move

def min_value(position, depth):
    min_eval = math.inf
    best_move = None
    
    for move in get_all_moves(position, Constants.RED):
        evaluation, _ = minimax(move, depth - 1, True)
        if evaluation < min_eval:
            min_eval = evaluation
            best_move = move
            
    return min_eval, best_move

def alphabeta(position, depth, alpha, beta, maximizing_player):
    if depth == 0 or position.winner() is not None:
        return position.evaluate(), position

    if maximizing_player:
        return max_value_ab(position, depth, alpha, beta)
    else:
        return min_value_ab(position, depth, alpha, beta)

def max_value_ab(position, depth, alpha, beta):
    max_eval = -math.inf
    best_move = None
    
    for move in get_all_moves(position, Constants.WHITE):
        evaluation, _ = (alphabeta(move, depth - 1, alpha, beta, False))
        if evaluation > max_eval:
            max_eval = evaluation
            best_move = move
        alpha = max(alpha, evaluation)
        if beta <= alpha:
            break
            
    return max_eval, best_move

def min_value_ab(position, depth, alpha, beta):
    min_eval = math.inf
    best_move = None
    
    for move in get_all_moves(position, Constants.RED):
        evaluation, _ = (alphabeta(move, depth - 1, alpha, beta, True))
        if evaluation < min_eval:
            min_eval = evaluation
            best_move = move
        beta = min(beta, evaluation)
        if beta <= alpha:
            break
            
    return min_eval, best_move

def get_all_moves(board, color):
    moves = []
    for piece in board.get_all_pieces(color):
        valid_moves = board.get_valid_moves(piece)
        for move, skip in valid_moves.items():
            temp_board = copy.deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            new_board = simulate_move(temp_piece, move, temp_board, skip)
            moves.append(new_board)
    return moves

def simulate_move(piece, move, board, skip):
    board.move(piece, move[0], move[1])
    if skip:
        board.remove(skip)
    return board