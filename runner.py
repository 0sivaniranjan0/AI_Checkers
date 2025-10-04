import pygame
import sys
import time
import os
from checkers import *

# Initialize pygame
pygame.init()

# Set constants - NEW DIMENSIONS 850x700
WIDTH, HEIGHT = 748, 750
Constants.SQUARE_SIZE = HEIGHT // Constants.ROWS  # Calculate based on rows to keep squares proper


# Try to load crown image
try:
    CROWN = pygame.transform.scale(pygame.image.load('crown.png'), (44, 25))
except:
    CROWN = pygame.Surface((44, 25))
    CROWN.fill((255, 255, 0))

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('Arial', 30)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, Constants.BLACK, self.rect, 2, border_radius=10)
        
        text_surf = self.font.render(self.text, True, Constants.BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Game:
    def __init__(self, win):
        self.win = win
        self.font = pygame.font.SysFont('Arial', 24)
        self.title_font = pygame.font.SysFont('Arial', 50, bold=True)
        self.ai_type = None
        self._init_menu()
        self.history = []

    def _init_menu(self):
        self.in_menu = True
        center_x = WIDTH // 2
        button_width, button_height = 300, 60
        spacing = 20
        
        self.minimax_btn = Button(center_x - 150, 200, button_width, button_height, 
                                 "Minimax AI (Slow)", Constants.GREY, Constants.WHITE)
        self.alphabeta_btn = Button(center_x - 150, 200 + button_height + spacing, 
                                   button_width, button_height, 
                                   "Alpha-Beta AI (Fast)", Constants.GREY, Constants.WHITE)
        
    def _init_game(self):
        self.in_menu = False
        self.selected = None
        self.board = Board()
        self.turn = Constants.RED
        self.valid_moves = {} #set -> unique elements
        self.message = ""
        self.game_over = False
        self.ai_time = 0

    def draw_menu(self):
        self.win.fill(Constants.BLACK)
        
        title = self.title_font.render("CHECKERS", True, Constants.WHITE)
        title_rect = title.get_rect(center=(WIDTH//2, 100))
        self.win.blit(title, title_rect)
        
        subtitle = self.font.render("Select AI Difficulty:", True, Constants.WHITE)
        subtitle_rect = subtitle.get_rect(center=(WIDTH//2, 160))
        self.win.blit(subtitle, subtitle_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        self.minimax_btn.check_hover(mouse_pos)
        self.alphabeta_btn.check_hover(mouse_pos)
        
        self.minimax_btn.draw(self.win)
        self.alphabeta_btn.draw(self.win)
        
        pygame.display.update()

    def update(self):
        self.win.fill(Constants.BLACK)
        
        # Draw board area (centered horizontally)
        board_x = (WIDTH - HEIGHT) // 2
        board_surface = pygame.Surface((HEIGHT, HEIGHT))
        self.board.draw(board_surface)
        self.win.blit(board_surface, (board_x, 0))
        
        self.draw_valid_moves(self.valid_moves)
        self.draw_ui()
        pygame.display.update()

    def draw_ui(self):
        # Turn indicator
        turn_text = "Your turn (RED)" if self.turn == Constants.RED else f"{self.ai_type} thinking..."
        text_surface = self.font.render(turn_text, True, Constants.WHITE)
        pygame.draw.rect(self.win, Constants.BLACK, (0, HEIGHT-50, WIDTH, 50))
        self.win.blit(text_surface, (20, HEIGHT-40))
        
        # Time taken display
        if hasattr(self, 'ai_time'):
            time_text = f"Time: {self.ai_time:.2f}s"
            time_surface = self.font.render(time_text, True, Constants.WHITE)
            self.win.blit(time_surface, (WIDTH - 150, HEIGHT-40))
        
        # Game message
        if self.message:
            msg_surface = self.font.render(self.message, True, Constants.WHITE)
            self.win.blit(msg_surface, (WIDTH//2 - msg_surface.get_width()//2, HEIGHT-80))

    def draw_valid_moves(self, moves):
        board_x = (WIDTH - HEIGHT) // 2
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, Constants.BLUE, 
                             (board_x + col * Constants.SQUARE_SIZE + Constants.SQUARE_SIZE//2, 
                              row * Constants.SQUARE_SIZE + Constants.SQUARE_SIZE//2), 
                             15)

    def select(self, row, col):
        if self.selected:
            result = self._move(row, col)
            if not result:
                self.selected = None
                self.select(row, col)
        
        board_x = (WIDTH - HEIGHT) // 2
        if 0 <= row < Constants.ROWS and 0 <= col < Constants.COLS:
            piece = self.board.get_piece(row, col)
            if piece and piece.color == self.turn:
                self.selected = piece
                self.valid_moves = self.board.get_valid_moves(piece)
                return True
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece is None and (row, col) in self.valid_moves:
            # Save current board state before making a move
            self.history.append(self.board.copy())
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False
        return True
    def undo_move(self):
        if self.history:
            self.board = self.history.pop()  # Revert to the last board state
            self.valid_moves = {}  # Clear valid moves
            self.selected = None  # Clear selection
            self.message = ""  # Clear any game messages

        # Adjust the turn to the correct player
        if self.turn == Constants.WHITE and self.ai_type:  # If it's AI's turn, revert to RED
            self.turn = Constants.RED
        elif self.turn == Constants.RED and self.ai_type:  # If it's RED's turn, revert to AI
            self.turn = Constants.WHITE
        else:
            print("No moves to undo!")  # Debug message

    def change_turn(self):
        self.selected = None
        self.valid_moves = {}
        if self.turn == Constants.RED:
            self.turn = Constants.WHITE
        else:
            self.turn = Constants.RED
        
        winner = self.board.winner()
        if winner is not None:
            self.game_over = True
            self.message = "You win!" if winner == Constants.RED else f"{self.ai_type} wins!"

    def ai_move(self):
        # Show thinking message immediately
        self.update()
        pygame.display.flip()  # Force update
        
        # Time the AI move
        start_time = time.time()
        
        if self.ai_type == "Minimax AI (Easy)":
            _, new_board = minimax(self.board, 5, True)
        elif self.ai_type == "Alpha-Beta AI (Hard)":
            _, new_board = alphabeta(self.board, 5, -math.inf, math.inf, True)
        else:
            print(f"Error: Unknown AI type '{self.ai_type}'")
            return
        
        end_time = time.time()
        self.ai_time = end_time - start_time
        print(f"{self.ai_type} took {self.ai_time:.2f} seconds")
        # Save the current board state before applying the AI's move
        self.history.append(self.board.copy())
        self.board = new_board
        self.change_turn()

def main():
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers AI")
    game = Game(WIN)
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game.in_menu:
                mouse_pos = pygame.mouse.get_pos()
                if game.minimax_btn.is_clicked(mouse_pos, event):
                    game.ai_type = "Minimax AI (Easy)"
                    game._init_game()
                elif game.alphabeta_btn.is_clicked(mouse_pos, event):
                    game.ai_type = "Alpha-Beta AI (Hard)"
                    game._init_game()
            else:
                if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                    if game.turn == Constants.RED:
                        pos = pygame.mouse.get_pos()
                        board_x = (WIDTH - HEIGHT) // 2
                        if board_x <= pos[0] < board_x + HEIGHT:
                            col = (pos[0] - board_x) // Constants.SQUARE_SIZE
                            row = pos[1] // Constants.SQUARE_SIZE
                            game.select(row, col)
                
                # Check for undo key press
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:  # Press 'U' to undo
                        game.undo_move()
                    if event.key == pygame.K_r:  # Restart game
                        game._init_menu()

        if game.in_menu:
            game.draw_menu()
        else:
            if not game.game_over and game.turn == Constants.WHITE:
                game.ai_move()
            game.update()

    pygame.quit()
    sys.exit()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()