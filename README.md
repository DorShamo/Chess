# ♟️ Chess vs Stockfish

A desktop chess game built with Python and Pygame. Play against the Stockfish engine at four difficulty levels.

| Start menu | Game | Game over |
|:---:|:---:|:---:|
| ![Start menu](screenshots/menu.png) | ![Board](screenshots/board.png) | ![Checkmate](screenshots/checkmate.png) |

## Features
- Full chess rules: castling, en passant, pawn promotion, check, checkmate and stalemate
- Legal moves highlighted for the selected piece
- Start menu with difficulty picker and a game-over screen with "New Game"
- Four difficulty levels: Easy, Medium, Hard, Expert
- Every finished game is saved as JSON in `games/`

## Tech
Python · Pygame · Stockfish

## How to run
1. Install the Stockfish engine:
   ```bash
   brew install stockfish
   ```
2. Install the Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python3 main.py
   ```

> Tip: with `pygame-ce` instead of `pygame`, the SVG pieces are rendered at full sharpness.

## Project structure
| Path | Purpose |
|---|---|
| `main.py` | Window, drawing, menus, Stockfish moves and game loop |
| `rules.py` | Board state and move rules |
| `pieces/` | SVG piece images |
| `screenshots/` | Images for this README |

## Credits
Chess piece images by [Cburnett](https://en.wikipedia.org/wiki/User:Cburnett),
from [Wikimedia Commons](https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces),
used under the BSD license.
