import pygame
import sys
import random
import math

from pause import pause

# --- Constants ---
WIDTH = 1280
HEIGHT = 720
FPS = 30

GRID_SIZE = 3                 # 3x3 grid
CELL_SIZE = 200               # Each cell is 200x200 pixels
BOMB_COUNT = 3
TIME_LIMIT = 30000            # 30 seconds (in milliseconds)

# Colors
BG_COLOR = (28, 28, 36)
CELL_COLOR = (62, 62, 86)
REVEALED_COLOR = (240, 240, 240)
BORDER_COLOR = (44, 44, 56)
TEXT_COLOR = (0, 0, 0)
BOMB_COLOR = (234, 74, 90)
FLAG_COLOR = (98, 182, 203)
ANTIDOTE_COLOR = (132, 224, 172)
TIMER_COLOR = (255, 203, 107)
HEADER_COLOR = (240, 240, 240)

# Board origin so that the grid is centered horizontally and placed below the header/timer.
BOARD_ORIGIN_X = (WIDTH - GRID_SIZE * CELL_SIZE) // 2
BOARD_ORIGIN_Y = 150

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Antidote Hunt")
clock = pygame.time.Clock()

# Use a font that supports emojis – "Segoe UI Emoji" is common on Windows.
try:
    header_font = pygame.font.SysFont("Segoe UI Emoji", 60)
    bold_font = pygame.font.SysFont("Segoe UI Emoji", 60)
    text_font = pygame.font.SysFont("Segoe UI Emoji", 40)
except Exception:
    header_font = pygame.font.Font(None, 60)
    bold_font = pygame.font.Font(None, 60)
    text_font = pygame.font.Font(None, 40)

# --- Cell Class ---
class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_bomb = False
        self.is_antidote = False
        self.revealed = False
        self.flagged = False
        self.adjacent = 0  # number of bombs in adjacent cells

    def get_rect(self):
        x = BOARD_ORIGIN_X + self.col * CELL_SIZE
        y = BOARD_ORIGIN_Y + self.row * CELL_SIZE
        return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

    def draw(self, surface):
        rect = self.get_rect()
        # Draw cell background
        if self.revealed:
            color = ANTIDOTE_COLOR if self.is_antidote else REVEALED_COLOR
            pygame.draw.rect(surface, color, rect, border_radius=12)
        else:
            pygame.draw.rect(surface, CELL_COLOR, rect, border_radius=12)
        # Draw cell border
        pygame.draw.rect(surface, BORDER_COLOR, rect, 4)
        # Draw cell content
        if self.revealed:
            if self.is_bomb:
                bomb_text = bold_font.render("💣", True, BOMB_COLOR)
                bomb_rect = bomb_text.get_rect(center=rect.center)
                surface.blit(bomb_text, bomb_rect)
            elif self.is_antidote:
                antidote_text = bold_font.render("💊", True, TEXT_COLOR)
                antidote_rect = antidote_text.get_rect(center=rect.center)
                surface.blit(antidote_text, antidote_rect)
            elif self.adjacent > 0:
                num_text = bold_font.render(str(self.adjacent), True, TEXT_COLOR)
                num_rect = num_text.get_rect(center=rect.center)
                surface.blit(num_text, num_rect)
        else:
            if self.flagged:
                flag_text = bold_font.render("🚩", True, FLAG_COLOR)
                flag_rect = flag_text.get_rect(center=rect.center)
                surface.blit(flag_text, flag_rect)

# --- Board Functions ---

def calculate_adjacent(board):
    """Recalculate adjacent bomb counts for the entire board."""
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if not board[r][c].is_bomb:
                count = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                            if board[nr][nc].is_bomb:
                                count += 1
                board[r][c].adjacent = count

def create_board(safe_cell):
    """
    Create a new board. The safe_cell (a tuple (row, col)) is guaranteed not to contain a bomb,
    but its neighbors are not protected so that it can have a nonzero adjacent count.
    """
    board = [[Cell(r, c) for c in range(GRID_SIZE)] for r in range(GRID_SIZE)]
    all_positions = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
    # Exclude only the safe cell itself.
    available_positions = [pos for pos in all_positions if pos != safe_cell]

    bomb_positions = random.sample(available_positions, min(BOMB_COUNT, len(available_positions)))
    for r, c in bomb_positions:
        board[r][c].is_bomb = True

    # Place antidote in one safe cell (if possible, not the safe_cell; else, safe_cell)
    safe_positions = [(r, c) for r, c in all_positions if not board[r][c].is_bomb]
    if safe_positions:
        possible = [pos for pos in safe_positions if pos != safe_cell]
        if possible:
            antidote_pos = random.choice(possible)
        else:
            antidote_pos = safe_cell
        board[antidote_pos[0]][antidote_pos[1]].is_antidote = True

    calculate_adjacent(board)

    # --- Enforce first-click is a number ---
    # If the safe cell (first click) has 0 adjacent bombs, then adjust by swapping one bomb.
    first_cell = board[safe_cell[0]][safe_cell[1]]
    if first_cell.adjacent == 0:
        # Get neighbors of safe_cell
        neighbors = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = safe_cell[0] + dr, safe_cell[1] + dc
                if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and (nr, nc) != safe_cell:
                    neighbors.append((nr, nc))
        # Among these, choose one neighbor at random to force a bomb.
        # But first, remove a bomb from somewhere else to keep bomb count constant.
        # Choose a candidate neighbor that is not already a bomb.
        candidate_neighbors = [pos for pos in neighbors if not board[pos[0]][pos[1]].is_bomb]
        if candidate_neighbors:
            chosen_neighbor = random.choice(candidate_neighbors)
            # Now, find a cell (outside safe_cell's neighborhood) that is a bomb.
            safe_zone = {safe_cell} | set(neighbors)
            bomb_candidates = [pos for pos in all_positions if pos not in safe_zone and board[pos[0]][pos[1]].is_bomb]
            if bomb_candidates:
                remove_bomb = random.choice(bomb_candidates)
                board[remove_bomb[0]][remove_bomb[1]].is_bomb = False
                board[chosen_neighbor[0]][chosen_neighbor[1]].is_bomb = True
                calculate_adjacent(board)
                # If still zero (unlikely), we can repeat or leave it.
    return board

def flood_fill_reveal(board, row, col):
    if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
        return
    cell = board[row][col]
    if cell.revealed or cell.flagged:
        return
    cell.revealed = True
    if cell.adjacent == 0 and not cell.is_bomb and not cell.is_antidote:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr != 0 or dc != 0:
                    flood_fill_reveal(board, row + dr, col + dc)

def reveal_extra_neighbor(board, row, col):
    # Reveal one safe neighboring cell if not already revealed.
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            nr, nc = row + dr, col + dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                neighbor = board[nr][nc]
                if not neighbor.revealed and not neighbor.flagged and not neighbor.is_bomb:
                    neighbor.revealed = True
                    if neighbor.adjacent == 0 and not neighbor.is_antidote:
                        flood_fill_reveal(board, nr, nc)
                    return

def check_win(board):
    # The player wins if the antidote cell is revealed.
    for row in board:
        for cell in row:
            if cell.is_antidote and cell.revealed:
                return True
    return False

def draw_timer(remaining_time):
    timer_text = header_font.render(f"{remaining_time // 1000}s", True, TIMER_COLOR)
    screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 20))

# --- Main Minigame Function ---
def run_antidote_hunt():
    board = None  # Board is created on the first click (safe-first-click)
    first_click = True
    start_time = pygame.time.get_ticks()
    final_elapsed = None  # Will be set when game_over is triggered
    game_over = False
    win = False

    while True:
        dt = clock.tick(FPS)
        # If the game is not over, update elapsed time; else freeze timer.
        if not game_over:
            elapsed = pygame.time.get_ticks() - start_time
        else:
            if final_elapsed is None:
                final_elapsed = pygame.time.get_ticks() - start_time
            elapsed = final_elapsed

        remaining_time = max(0, TIME_LIMIT - elapsed)

        screen.fill(BG_COLOR)
        title_text = header_font.render("Antidote Hunt", True, HEADER_COLOR)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 80))
        draw_timer(remaining_time)

        # Draw grid
        if board:
            for row in board:
                for cell in row:
                    cell.draw(screen)
        else:
            # Draw empty grid for visual feedback
            for r in range(GRID_SIZE):
                for c in range(GRID_SIZE):
                    rect = pygame.Rect(BOARD_ORIGIN_X + c * CELL_SIZE,
                                       BOARD_ORIGIN_Y + r * CELL_SIZE,
                                       CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, CELL_COLOR, rect, border_radius=12)
                    pygame.draw.rect(screen, BORDER_COLOR, rect, 4)

        pygame.display.flip()

        # Check win condition
        if board and check_win(board):
            win = True
            game_over = True

        # Time out check
        if remaining_time <= 0 and not game_over:
            game_over = True
            win = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Press 'P' to pause
                    pause(screen)
            if not game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    grid_rect = pygame.Rect(BOARD_ORIGIN_X, BOARD_ORIGIN_Y, GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
                    if grid_rect.collidepoint(mx, my):
                        col = (mx - BOARD_ORIGIN_X) // CELL_SIZE
                        row = (my - BOARD_ORIGIN_Y) // CELL_SIZE
                        if first_click:
                            board = create_board(safe_cell=(row, col))
                            first_click = False
                        cell = board[row][col]
                        if event.button == 1:  # Left click to reveal
                            if not cell.flagged:
                                cell.revealed = True
                                if cell.is_bomb:
                                    game_over = True
                                    win = False
                                elif cell.is_antidote:
                                    win = True
                                    game_over = True
                                else:
                                    # Reveal adjacent safe cells (neighbors that are not bombs or antidote)
                                    for dr in (-1, 0, 1):
                                        for dc in (-1, 0, 1):
                                            nr, nc = row + dr, col + dc
                                            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                                                neighbor = board[nr][nc]
                                                if (not neighbor.revealed and not neighbor.flagged and
                                                    not neighbor.is_bomb and not neighbor.is_antidote):
                                                    neighbor.revealed = True
                                                    if neighbor.adjacent == 0:
                                                        flood_fill_reveal(board, nr, nc)
                        elif event.button == 3:  # Right click to flag/unflag
                            if not cell.revealed:
                                cell.flagged = not cell.flagged
            else:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        board = None
                        first_click = True
                        start_time = pygame.time.get_ticks()
                        final_elapsed = None
                        game_over = False
                        win = False

        if game_over:
            if win:
                result_msg = "💊 Antidote Acquired! You Win!"
                msg_color = TIMER_COLOR
            else:
                result_msg = "💣 BOOM! You Failed!"
                msg_color = BOMB_COLOR
            result_text = header_font.render(result_msg, True, msg_color)
            restart_text = text_font.render("Press R to Retry", True, TEXT_COLOR)
            screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT - 150))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT - 100))
            pygame.display.flip()

        clock.tick(FPS)


if __name__ == "__main__":
    outcome = run_antidote_hunt()
    print(f"Minigame result: {'Won' if outcome else 'Lost'}")
    pygame.quit()
    sys.exit()
