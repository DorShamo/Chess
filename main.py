import json
import os
import shutil
from datetime import datetime

os.environ["SDL_MOUSE_FOCUS_CLICKTHROUGH"] = "1"   # don't swallow the click that focuses the window
import pygame # type: ignore
from stockfish import Stockfish # type: ignore
from rules import board, all_legal_moves, make_move, is_checkmate, is_stalemate

# Sizes
SQUARE = 70                          # size of one square
BOARD = SQUARE * 8                   # 560
INNER = 25                           # width of the slate frame
OUTER = 8                            # width of the black frame
LINE = 3                             # width of the light line around the squares
SIZE = BOARD + INNER * 2 + OUTER * 2 # window size: 626

# Colors
BLACK = (0, 0, 0)
SLATE = (64, 70, 84)                 # dark slate blue-gray
CREAM = (232, 232, 218)              # cream
LABEL = (150, 155, 170)              # color of the numbers and letters
GOLD = (246, 214, 92)                # button when the mouse is over it
HIGHLIGHT = (246, 214, 92, 130)      # selected square: semi-transparent yellow
MOVE_MARK = (30, 30, 30, 90)         # move dots and capture rings: semi-transparent dark
DIM = (20, 22, 28, 170)              # dark see-through layer behind the menus

pygame.init()
screen = pygame.display.set_mode((SIZE, SIZE))
pygame.display.set_caption("Chess")
font = pygame.font.SysFont("arial", 14, bold=True)
title_font = pygame.font.SysFont("arial", 48, bold=True)
subtitle_font = pygame.font.SysFont("arial", 22)
button_font = pygame.font.SysFont("arial", 22, bold=True)
level_font = pygame.font.SysFont("arial", 26, bold=True)

# The board starts after both frames
board_x = OUTER + INNER
board_y = OUTER + INNER

# Center of the board - the menus are built around it
center_x = board_x + BOARD // 2
center_y = board_y + BOARD // 2

# Game state
turn = "w"                           # whose turn: "w" or "b"
selected = None                      # the selected square, or None
moves = []                           # legal moves of the selected piece
moved = set()                        # squares that pieces have left (for castling)
last_move = None                     # the last move (for en passant)
game_over = None                     # end text, e.g. "Checkmate!|White wins"
history = []                         # every move of the game, in order
game_saved = False                   # was this game already saved to a file?
in_menu = True                       # showing the start menu?

# Bot
BOT_COLOR = "b"                      # the bot plays black, you play white
BOT_THINK_MS = 500                   # how long the bot thinks per move, in milliseconds
LEVELS = [("Easy", 1), ("Medium", 5), ("Hard", 10), ("Expert", 20)]   # name, Stockfish skill (0-20)
level_index = 1                      # starts on "Medium"

stockfish_path = shutil.which("stockfish") or "/opt/homebrew/bin/stockfish"
bot = Stockfish(path=stockfish_path)

uci_moves = []                       # the game in the engine's format, e.g. ["e2e4", "e7e5"]

# Saving
GAMES_FOLDER = "games"                    # every game is saved here as game_1.json, game_2.json...
START_BOARD = [row[:] for row in board]   # copy of the starting position, for new games

# Buttons - each is a rectangle, used both to draw it and to check clicks
LEFT_ARROW = pygame.Rect(0, 0, 44, 44)
LEFT_ARROW.center = (center_x - 110, center_y + 20)
RIGHT_ARROW = pygame.Rect(0, 0, 44, 44)
RIGHT_ARROW.center = (center_x + 110, center_y + 20)
START_BUTTON = pygame.Rect(0, 0, 180, 50)
START_BUTTON.center = (center_x, center_y + 100)
NEW_GAME_BUTTON = pygame.Rect(0, 0, 180, 50)
NEW_GAME_BUTTON.center = (center_x, center_y + 75)


##########################################################################################
# Drawing
##########################################################################################
def draw_board():
    # Fill the whole window black - this is the outer frame
    screen.fill(BLACK)

    # Slate frame
    size = BOARD + INNER * 2
    pygame.draw.rect(screen, SLATE, (OUTER, OUTER, size, size))

    # Squares
    for row in range(8):
        for col in range(8):
            if (row + col) % 2 == 0:
                color = CREAM
            else:
                color = SLATE
            x = board_x + col * SQUARE
            y = board_y + row * SQUARE
            pygame.draw.rect(screen, color, (x, y, SQUARE, SQUARE))

    # Light line around the squares
    pygame.draw.rect(screen, CREAM,
                     (board_x - LINE, board_y - LINE, BOARD + LINE * 2, BOARD + LINE * 2),
                     LINE)


def draw_labels():
    letters = "abcdefgh"
    for i in range(8):
        # Numbers on the left: 8 at the top, 1 at the bottom
        num = font.render(str(8 - i), True, LABEL)
        x = board_x - INNER // 2 - num.get_width() // 2
        y = board_y + i * SQUARE + SQUARE // 2 - num.get_height() // 2
        screen.blit(num, (x, y))

        # Letters at the bottom
        letter = font.render(letters[i], True, LABEL)
        x = board_x + i * SQUARE + SQUARE // 2 - letter.get_width() // 2
        y = board_y + BOARD + INNER // 2 - letter.get_height() // 2
        screen.blit(letter, (x, y))


def load_images():
    images = {}
    for color in "wb":
        for kind in "KQRBNP":
            code = color + kind                              # e.g. "wR"
            path = f"pieces/{code}.svg"

            if hasattr(pygame.image, "load_sized_svg"):
                # pygame-ce: load the SVG straight at the right size - sharp
                images[code] = pygame.image.load_sized_svg(path, (SQUARE, SQUARE))
            else:
                # regular pygame: load at the SVG's own size, then scale
                image = pygame.image.load(path).convert_alpha()
                images[code] = pygame.transform.smoothscale(image, (SQUARE, SQUARE))
    return images


images = load_images()


def draw_pieces(board):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]

            # Empty square - nothing to draw
            if piece is None:
                continue

            x = board_x + col * SQUARE
            y = board_y + row * SQUARE
            screen.blit(images[piece], (x, y))


def draw_highlights(selected, moves):
    # Nothing selected - nothing to highlight
    if selected is None:
        return

    # Selected square: fill it with a see-through color
    row, col = selected
    overlay = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
    overlay.fill(HIGHLIGHT)
    screen.blit(overlay, (board_x + col * SQUARE, board_y + row * SQUARE))

    # Legal moves: a dot on empty squares, a ring around enemy pieces
    for row, col in moves:
        mark = pygame.Surface((SQUARE, SQUARE), pygame.SRCALPHA)
        center = (SQUARE // 2, SQUARE // 2)

        if board[row][col] is None:
            pygame.draw.circle(mark, MOVE_MARK, center, SQUARE // 6)          # small dot
        else:
            pygame.draw.circle(mark, MOVE_MARK, center, SQUARE // 2 - 2, 5)   # ring, 5 px thick

        screen.blit(mark, (board_x + col * SQUARE, board_y + row * SQUARE))


##########################################################################################
# Menus: start screen and game over screen
##########################################################################################
def draw_dim():
    # Dark see-through layer over the squares
    overlay = pygame.Surface((BOARD, BOARD), pygame.SRCALPHA)
    overlay.fill(DIM)
    screen.blit(overlay, (board_x, board_y))


def draw_text(text, text_font, color, center):
    # Draw text centered around a point
    image = text_font.render(text, True, color)
    screen.blit(image, image.get_rect(center=center))


def draw_button(rect, text):
    # Gold when the mouse is over the button, cream otherwise
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    color = GOLD if hovered else CREAM

    pygame.draw.rect(screen, color, rect, border_radius=8)
    draw_text(text, button_font, SLATE, rect.center)


def draw_menu():
    draw_dim()

    draw_text("Chess", title_font, CREAM, (center_x, center_y - 110))
    draw_text("You play White", subtitle_font, LABEL, (center_x, center_y - 65))

    # Difficulty: < Medium >
    draw_text("Difficulty", subtitle_font, LABEL, (center_x, center_y - 20))
    draw_button(LEFT_ARROW, "<")
    draw_button(RIGHT_ARROW, ">")
    level_name = LEVELS[level_index][0]
    draw_text(level_name, level_font, CREAM, (center_x, center_y + 20))

    draw_button(START_BUTTON, "Start")


def draw_game_over(text):
    title, subtitle = text.split("|")

    draw_dim()
    draw_text(title, title_font, CREAM, (center_x, center_y - 45))
    draw_text(subtitle, subtitle_font, LABEL, (center_x, center_y))
    draw_button(NEW_GAME_BUTTON, "New Game")


def handle_menu_click(pos):
    global level_index, in_menu

    if LEFT_ARROW.collidepoint(pos):
        level_index = (level_index - 1) % len(LEVELS)     # wraps from Easy to Expert
    elif RIGHT_ARROW.collidepoint(pos):
        level_index = (level_index + 1) % len(LEVELS)     # wraps from Expert to Easy
    elif START_BUTTON.collidepoint(pos):
        bot.set_skill_level(LEVELS[level_index][1])
        in_menu = False


def handle_game_over_click(pos):
    if NEW_GAME_BUTTON.collidepoint(pos):
        new_game()


##########################################################################################
# Game logic
##########################################################################################
def mouse_to_square(pos):
    x, y = pos

    # Position relative to the top-left corner of the squares
    col = (x - board_x) // SQUARE
    row = (y - board_y) // SQUARE

    # Clicked on the frame, not on a square
    if not (0 <= row < 8 and 0 <= col < 8):
        return None

    return (row, col)


def check_game_over():
    # Is the player whose turn it is now checkmated or stalemated?
    global game_over

    if is_checkmate(board, turn):
        winner = "White" if turn == "b" else "Black"
        game_over = f"Checkmate!|{winner} wins"
        save_game()
    elif is_stalemate(board, turn):
        game_over = "Stalemate|Draw"
        save_game()


def play_move(start, end):
    # Make a move on the board - used by both you and the bot
    global selected, moves, turn, last_move

    uci_moves.append(to_uci(start, end))     # must be before make_move - it looks at the piece
    last_move = make_move(board, start, end, moved)
    history.append((start, end))
    selected = None
    moves = []

    # Switch turns, then check if the game ended
    turn = "b" if turn == "w" else "w"
    check_game_over()


def handle_click(pos):
    global selected, moves

    # It's the bot's turn - ignore clicks
    if turn == BOT_COLOR:
        return

    square = mouse_to_square(pos)

    # Clicked on the frame
    if square is None:
        return

    row, col = square
    piece = board[row][col]

    # A piece is selected and the click is on one of its legal moves - make the move
    if selected is not None and square in moves:
        play_move(selected, square)
        return

    # Clicked on one of our own pieces - select it
    if piece is not None and piece[0] == turn:
        selected = square
        moves = all_legal_moves(board, row, col, moved, last_move)
    else:
        # Anything else - cancel the selection
        selected = None
        moves = []


##########################################################################################
# Bot
##########################################################################################
def to_uci(start, end):
    # ((6, 4), (4, 4)) -> "e2e4", and a pawn reaching the last row gets "q" (queen)
    text = square_name(start) + square_name(end)
    piece = board[start[0]][start[1]]
    if piece[1] == "P" and end[0] in (0, 7):
        text += "q"
    return text


def from_uci(text):
    # "e7e5" -> ((1, 4), (3, 4))
    start = (8 - int(text[1]), "abcdefgh".index(text[0]))
    end = (8 - int(text[3]), "abcdefgh".index(text[2]))
    return start, end


def bot_move():
    # Give the engine all the moves so far (newer versions renamed set_position)
    if hasattr(bot, "make_moves_from_start"):
        bot.make_moves_from_start(uci_moves)
    else:
        bot.set_position(uci_moves)

    best = bot.get_best_move_time(BOT_THINK_MS)

    # No move - the game is over
    if best is None:
        return

    start, end = from_uci(best)
    play_move(start, end)


##########################################################################################
# New game and saving
##########################################################################################
def new_game():
    # Reset everything and go back to the start menu
    global turn, selected, moves, last_move, game_over, game_saved, in_menu

    board[:] = [row[:] for row in START_BOARD]   # back to the starting position
    moved.clear()
    history.clear()
    uci_moves.clear()
    turn = "w"
    selected = None
    moves = []
    last_move = None
    game_over = None
    game_saved = False
    in_menu = True


def square_name(square):
    # (6, 4) -> "e2"
    row, col = square
    return "abcdefgh"[col] + str(8 - row)


def next_game_number():
    # Look at the files already saved and return the next free number
    if not os.path.exists(GAMES_FOLDER):
        return 1

    numbers = []
    for name in os.listdir(GAMES_FOLDER):
        if name.startswith("game_") and name.endswith(".json"):
            numbers.append(int(name[5:-5]))      # "game_12.json" -> 12

    return max(numbers) + 1 if numbers else 1


def save_game():
    global game_saved

    # Nothing to save, or this game was already saved
    if not history or game_saved:
        return

    os.makedirs(GAMES_FOLDER, exist_ok=True)
    number = next_game_number()

    # Result: the end text, or "Unfinished" if the window was closed mid-game
    if game_over is not None:
        result = game_over.replace("|", " - ")
    else:
        result = "Unfinished"

    bot_name = f"Stockfish ({LEVELS[level_index][0]})"

    record = {
        "game": number,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "white": "You" if BOT_COLOR == "b" else bot_name,
        "black": "You" if BOT_COLOR == "w" else bot_name,
        "result": result,
        "moves": [square_name(start) + "-" + square_name(end) for start, end in history],
    }

    with open(f"{GAMES_FOLDER}/game_{number}.json", "w") as f:
        json.dump(record, f, indent=2)

    game_saved = True


##########################################################################################
# Main loop
##########################################################################################
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        # Closing the window - save the game if it has moves
        if event.type == pygame.QUIT:
            save_game()
            running = False

        # Clicks go to the menu, the game over screen, or the board
        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_menu:
                handle_menu_click(event.pos)
            elif game_over is not None:
                handle_game_over_click(event.pos)
            else:
                handle_click(event.pos)

        # N - save the current game and go back to the start menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
            save_game()
            new_game()

    draw_board()
    draw_labels()
    draw_highlights(selected, moves)
    draw_pieces(board)

    if in_menu:
        draw_menu()
    elif game_over is not None:
        draw_game_over(game_over)

    pygame.display.flip()
    clock.tick(60)          # at most 60 frames per second

    # The bot plays after the screen shows your move
    if not in_menu and game_over is None and turn == BOT_COLOR:
        bot_move()

pygame.quit()