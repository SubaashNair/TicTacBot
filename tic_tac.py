import pygame as pg
import sys
import time
import json
from pathlib import Path
from pygame.locals import *

# Initialize Pygame
pg.init()

# Game Constants
WIDTH = 400
HEIGHT = 400
BACKGROUND = (40, 42, 54)  # Dracula background
LINE_COLOR = (98, 114, 164)  # Dracula comment color
WIN_LINE_COLOR = (255, 85, 85)  # Dracula red
X_COLOR = (80, 250, 123)  # Dracula green
O_COLOR = (189, 147, 249)  # Dracula purple
BUTTON_COLOR = (68, 71, 90)  # Dracula current line
BUTTON_HOVER_COLOR = (98, 114, 164)  # Dracula comment
BUTTON_TEXT_COLOR = (248, 248, 242)  # Dracula foreground
STATUS_BAR_COLOR = (30, 31, 40)  # Darker background for status
MARK_SIZE = 80
GRID_LINE_THICKNESS = 4
MARK_THICKNESS = 6
BUTTON_WIDTH = 90
BUTTON_HEIGHT = 30
BUTTON_RADIUS = 6
BUTTON_MARGIN = 10
WIN_LINE_THICKNESS = 8
INPUT_BOX_COLOR = (68, 71, 90)    # Dracula current line
INPUT_TEXT_COLOR = (248, 248, 242)  # Dracula foreground

# Game Variables
AI_PLAYER = 'o'
HUMAN_PLAYER = 'x'
LEADERBOARD_FILE = "leaderboard.json"
MAX_LEADERBOARD_ENTRIES = 5

# Initialize screen
screen = pg.display.set_mode((WIDTH, HEIGHT + 100))
pg.display.set_caption("Tic Tac Toe")
clock = pg.time.Clock()
FPS = 30

# Game state
username = ""
input_active = True
current_player = HUMAN_PLAYER
current_winner = None
is_draw = False
grid = [[None]*3, [None]*3, [None]*3]
human_wins = 0
ai_wins = 0
draws = 0
leaderboard = {}

def load_leaderboard():
    """Load leaderboard from file"""
    global leaderboard
    try:
        with open(LEADERBOARD_FILE, 'r') as f:
            leaderboard = json.load(f)
    except FileNotFoundError:
        leaderboard = {}

def save_leaderboard():
    """Save leaderboard to file"""
    sorted_leaders = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:MAX_LEADERBOARD_ENTRIES]
    leaderboard_dict = dict(sorted_leaders)
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard_dict, f)

def update_leaderboard():
    """Update leaderboard with current player's wins"""
    global leaderboard
    if username in leaderboard:
        leaderboard[username] = max(leaderboard[username], human_wins)
    else:
        leaderboard[username] = human_wins
    save_leaderboard()

def draw_username_input():
    """Draw username input screen"""
    screen.fill(BACKGROUND)
    font = pg.font.Font(None, 36)
    
    title = font.render("Enter Your Username:", True, BUTTON_TEXT_COLOR)
    title_rect = title.get_rect(center=(WIDTH/2, HEIGHT/3))
    
    input_rect = pg.Rect(WIDTH/4, HEIGHT/2, WIDTH/2, 40)
    pg.draw.rect(screen, INPUT_BOX_COLOR, input_rect, border_radius=BUTTON_RADIUS)
    
    text_surface = font.render(username, True, INPUT_TEXT_COLOR)
    text_rect = text_surface.get_rect(center=input_rect.center)
    
    instruction = pg.font.Font(None, 24).render("Press ENTER to start", True, LINE_COLOR)
    instruction_rect = instruction.get_rect(center=(WIDTH/2, HEIGHT*2/3))
    
    screen.blit(title, title_rect)
    screen.blit(text_surface, text_rect)
    screen.blit(instruction, instruction_rect)
    pg.display.flip()

def draw_game_board():
    """Draws the initial game board"""
    screen.fill(BACKGROUND)
    pg.draw.line(screen, LINE_COLOR, (WIDTH/3, 20), (WIDTH/3, HEIGHT-20), GRID_LINE_THICKNESS)
    pg.draw.line(screen, LINE_COLOR, (WIDTH/3*2, 20), (WIDTH/3*2, HEIGHT-20), GRID_LINE_THICKNESS)
    pg.draw.line(screen, LINE_COLOR, (20, HEIGHT/3), (WIDTH-20, HEIGHT/3), GRID_LINE_THICKNESS)
    pg.draw.line(screen, LINE_COLOR, (20, HEIGHT/3*2), (WIDTH-20, HEIGHT/3*2), GRID_LINE_THICKNESS)
    draw_status()

def draw_status():
    """Updates the status bar"""
    if current_winner is None:
        message = current_player.upper() + "'s Turn"
    else:
        message = current_winner.upper() + " won!"
    if is_draw:
        message = "Game Draw!"

    status_bar_rect = pg.Rect(0, 400, WIDTH, 100)
    pg.draw.rect(screen, STATUS_BAR_COLOR, status_bar_rect)
    
    font = pg.font.Font(None, 28)
    scores_text = f"Human: {human_wins} | AI: {ai_wins} | Draws: {draws}"
    scores = font.render(scores_text, True, BUTTON_TEXT_COLOR)
    scores_rect = scores.get_rect(center=(WIDTH/2, 460))
    
    status_font = pg.font.Font(None, 34)
    status_surface = status_font.render(message, True, BUTTON_TEXT_COLOR)
    text_rect = status_surface.get_rect(center=(WIDTH/2, 425))
    
    new_game_rect = pg.Rect(WIDTH - BUTTON_WIDTH - BUTTON_MARGIN, 405, BUTTON_WIDTH, BUTTON_HEIGHT)
    leaders_rect = pg.Rect(BUTTON_MARGIN, 405, BUTTON_WIDTH, BUTTON_HEIGHT)
    
    mouse_pos = pg.mouse.get_pos()
    
    for button_rect, text in [(new_game_rect, "New Game"), (leaders_rect, "Leaders")]:
        button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pg.draw.rect(screen, button_color, button_rect, border_radius=BUTTON_RADIUS)
        button_font = pg.font.Font(None, 24)
        button_text = button_font.render(text, True, BUTTON_TEXT_COLOR)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)
    
    screen.blit(status_surface, text_rect)
    screen.blit(scores, scores_rect)
    pg.display.update()

def draw_move(row, col):
    """Draws X or O on the board"""
    global grid, current_player
    
    pos_x = 30 + (col * WIDTH//3)
    pos_y = 30 + (row * HEIGHT//3)
    
    grid[row][col] = current_player
    
    if current_player == 'x':
        pg.draw.line(screen, X_COLOR,
                    (pos_x + 15, pos_y + 15),
                    (pos_x + MARK_SIZE - 15, pos_y + MARK_SIZE - 15), MARK_THICKNESS)
        pg.draw.line(screen, X_COLOR,
                    (pos_x + 15, pos_y + MARK_SIZE - 15),
                    (pos_x + MARK_SIZE - 15, pos_y + 15), MARK_THICKNESS)
        current_player = 'o'
    else:
        center = (pos_x + MARK_SIZE//2, pos_y + MARK_SIZE//2)
        radius = MARK_SIZE//2 - 15
        pg.draw.circle(screen, O_COLOR, center, radius, MARK_THICKNESS)
        current_player = 'x'

def check_win():
    """Checks for win conditions"""
    global grid, current_winner, is_draw
    
    for row in range(3):
        if grid[row][0] == grid[row][1] == grid[row][2] and grid[row][0]:
            current_winner = grid[row][0]
            start_pos = (20, (row + 1)*HEIGHT/3 - HEIGHT/6)
            end_pos = (WIDTH-20, (row + 1)*HEIGHT/3 - HEIGHT/6)
            pg.draw.line(screen, WIN_LINE_COLOR, start_pos, end_pos, WIN_LINE_THICKNESS)
            return

    for col in range(3):
        if grid[0][col] == grid[1][col] == grid[2][col] and grid[0][col]:
            current_winner = grid[0][col]
            start_pos = ((col + 1)*WIDTH/3 - WIDTH/6, 20)
            end_pos = ((col + 1)*WIDTH/3 - WIDTH/6, HEIGHT-20)
            pg.draw.line(screen, WIN_LINE_COLOR, start_pos, end_pos, WIN_LINE_THICKNESS)
            return

    if grid[0][0] == grid[1][1] == grid[2][2] and grid[0][0]:
        current_winner = grid[0][0]
        pg.draw.line(screen, WIN_LINE_COLOR, (20, 20), (WIDTH-20, HEIGHT-20), WIN_LINE_THICKNESS)
    
    if grid[0][2] == grid[1][1] == grid[2][0] and grid[0][2]:
        current_winner = grid[0][2]
        pg.draw.line(screen, WIN_LINE_COLOR, (WIDTH-20, 20), (20, HEIGHT-20), WIN_LINE_THICKNESS)

    if all(all(row) for row in grid) and not current_winner:
        is_draw = True
    
    draw_status()

def minimax(board, depth, is_maximizing):
    """Implements the minimax algorithm for AI moves"""
    scores = {'x': -10, 'o': 10, 'draw': 0}
    
    winner = get_winner(board)
    if winner:
        return scores[winner], None
    if is_board_full(board):
        return scores['draw'], None
        
    best_pos = None
    if is_maximizing:
        best_score = float('-inf')
        player = AI_PLAYER
    else:
        best_score = float('inf')
        player = HUMAN_PLAYER
    
    for row in range(3):
        for col in range(3):
            if board[row][col] is None:
                board[row][col] = player
                score, _ = minimax(board, depth + 1, not is_maximizing)
                board[row][col] = None
                
                if is_maximizing and score > best_score:
                    best_score = score
                    best_pos = (row, col)
                elif not is_maximizing and score < best_score:
                    best_score = score
                    best_pos = (row, col)
                    
    return best_score, best_pos

def get_winner(board):
    """Helper function to check winner for minimax"""
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0]:
            return board[row][0]
    
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col]:
            return board[0][col]
    
    if board[0][0] == board[1][1] == board[2][2] and board[0][0]:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2]:
        return board[0][2]
    
    return None

def is_board_full(board):
    """Helper function to check if board is full"""
    return all(all(row) for row in board)

def ai_move():
    """Makes the AI move using minimax algorithm"""
    _, best_pos = minimax(grid, 0, True)
    if best_pos:
        row, col = best_pos
        draw_move(row, col)
        check_win()

def reset_game(update_scores=True):
    """Resets the game after win/draw"""
    global grid, current_winner, current_player, is_draw, human_wins, ai_wins, draws
    
    if update_scores:
        if current_winner:
            if current_winner == HUMAN_PLAYER:
                human_wins += 1
                update_leaderboard()
            else:
                ai_wins += 1
        elif is_draw:
            draws += 1
    
    current_player = HUMAN_PLAYER
    current_winner = None
    is_draw = False
    grid = [[None]*3, [None]*3, [None]*3]
    draw_game_board()

def handle_click():
    """Processes mouse clicks"""
    x, y = pg.mouse.get_pos()
    
    new_game_rect = pg.Rect(WIDTH - BUTTON_WIDTH - BUTTON_MARGIN, 405, BUTTON_WIDTH, BUTTON_HEIGHT)
    leaders_rect = pg.Rect(BUTTON_MARGIN, 405, BUTTON_WIDTH, BUTTON_HEIGHT)
    
    if new_game_rect.collidepoint(x, y):
        reset_game(update_scores=False)
        return
    elif leaders_rect.collidepoint(x, y):
        draw_leaderboard_window()
        waiting_for_click = True
        while waiting_for_click:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN or event.type == pg.KEYDOWN:
                    waiting_for_click = False
                elif event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
        draw_game_board()
        return
    
    if y >= HEIGHT:
        return
        
    row = y // (HEIGHT//3)
    col = x // (WIDTH//3)
    
    if grid[row][col] is None:
        draw_move(row, col)
        check_win()

def draw_leaderboard_window():
    """Draw separate leaderboard window"""
    LEADERBOARD_WIDTH = 300
    LEADERBOARD_HEIGHT = 400
    LEADERBOARD_TITLE_HEIGHT = 60
    ENTRY_HEIGHT = 50
    ENTRY_MARGIN = 10
    
    leaderboard_surface = pg.Surface((LEADERBOARD_WIDTH, LEADERBOARD_HEIGHT))
    leaderboard_surface.fill(BACKGROUND)
    
    title_font = pg.font.Font(None, 36)
    title = title_font.render("Leaderboard", True, BUTTON_TEXT_COLOR)
    title_rect = title.get_rect(center=(LEADERBOARD_WIDTH/2, LEADERBOARD_TITLE_HEIGHT/2))
    
    pg.draw.line(leaderboard_surface, LINE_COLOR, 
                 (20, LEADERBOARD_TITLE_HEIGHT),
                 (LEADERBOARD_WIDTH-20, LEADERBOARD_TITLE_HEIGHT), 2)
    
    entry_font = pg.font.Font(None, 28)
    sorted_leaders = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)[:MAX_LEADERBOARD_ENTRIES]
    
    for i, (name, wins) in enumerate(sorted_leaders):
        y_pos = LEADERBOARD_TITLE_HEIGHT + (i * ENTRY_HEIGHT) + ENTRY_MARGIN
        
        rank_text = f"#{i+1}"
        rank = entry_font.render(rank_text, True, LINE_COLOR)
        rank_rect = rank.get_rect(left=30, centery=y_pos + ENTRY_HEIGHT/2)
        
        name_text = name[:15]
        name = entry_font.render(name_text, True, BUTTON_TEXT_COLOR)
        name_rect = name.get_rect(left=80, centery=y_pos + ENTRY_HEIGHT/2)
        
        wins_text = f"{wins} wins"
        wins = entry_font.render(wins_text, True, X_COLOR)
        wins_rect = wins.get_rect(right=LEADERBOARD_WIDTH-30, centery=y_pos + ENTRY_HEIGHT/2)
        
        leaderboard_surface.blit(rank, rank_rect)
        leaderboard_surface.blit(name, name_rect)
        leaderboard_surface.blit(wins, wins_rect)
        
        if i < len(sorted_leaders) - 1:
            pg.draw.line(leaderboard_surface, LINE_COLOR, 
                        (40, y_pos + ENTRY_HEIGHT),
                        (LEADERBOARD_WIDTH-40, y_pos + ENTRY_HEIGHT), 1)
    
    main_center = (WIDTH/2, (HEIGHT+100)/2)
    leaderboard_pos = (main_center[0] - LEADERBOARD_WIDTH/2,
                      main_center[1] - LEADERBOARD_HEIGHT/2)
    
    screen.blit(leaderboard_surface, leaderboard_pos)
    pg.display.update()

def main():
    global username, input_active, current_player
    
    load_leaderboard()
    
    while input_active:
        draw_username_input()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN and username.strip():
                    input_active = False
                elif event.key == pg.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 15 and event.unicode.isprintable():
                        username += event.unicode
    
    draw_game_board()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if current_winner or is_draw:
                    time.sleep(1)
                    reset_game()
                elif current_player == HUMAN_PLAYER:
                    handle_click()
                    if not current_winner and not is_draw and current_player == AI_PLAYER:
                        ai_move()
        
        pg.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main() 