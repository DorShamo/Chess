##########################################################################################
board = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
]
##########################################################################################
##########################################################################################
def pawn_moves(board, row, col):
    moves = []
    color = board[row][col][0]   # "w" or "b"

    # White moves up the board, black moves down
    if color == 'w':
        direction = -1
        start_row = 6
    else:
        direction = 1
        start_row = 1

    # One step forward - only if the square is empty
    r = row + direction
    if 0 <= r < 8 and board[r][col] is None:
        moves.append((r, col))

        # Two steps forward - only from the start row, and both squares empty
        r2 = row + direction * 2
        if row == start_row and board[r2][col] is None:
            moves.append((r2, col))

    # Captures - one step diagonally forward, only onto an enemy piece
    for dc in (-1, 1):
        r, c = row + direction, col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            target = board[r][c]
            if target is not None and target[0] != color:
                moves.append((r, c))

    return moves
##########################################################################################
##########################################################################################
def rook_moves(board, row, col):
    moves = []
    color = board[row][col][0]   # "w" or "b"

    # Four directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc

        # Keep walking in this direction while still on the board
        while 0 <= r < 8 and 0 <= c < 8:
            target = board[r][c]

            if target is None:
                # Empty square - can move here, keep going
                moves.append((r, c))
            elif target[0] != color:
                # Enemy piece - can capture it, but stop here
                moves.append((r, c))
                break
            else:
                # Own piece - blocked, stop here
                break

            r += dr
            c += dc

    return moves
##########################################################################################
##########################################################################################
def bishop_moves(board, row, col):
    moves = []
    color = board[row][col][0]   # "w" or "b"

    # Four diagonal directions: up-left, up-right, down-left, down-right
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc

        # Keep walking in this direction while still on the board
        while 0 <= r < 8 and 0 <= c < 8:
            target = board[r][c]

            if target is None:
                # Empty square - can move here, keep going
                moves.append((r, c))
            elif target[0] != color:
                # Enemy piece - can capture it, but stop here
                moves.append((r, c))
                break
            else:
                # Own piece - blocked, stop here
                break

            r += dr
            c += dc

    return moves
##########################################################################################
##########################################################################################
def knight_moves(board, row, col):
    moves = []
    color = board[row][col][0]   # "w" or "b"

    # Eight L-shaped jumps: two squares one way, one square to the side
    jumps = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
             (1, -2), (1, 2), (2, -1), (2, 1)]

    for dr, dc in jumps:
        r, c = row + dr, col + dc

        # Skip jumps that land outside the board
        if 0 <= r < 8 and 0 <= c < 8:
            target = board[r][c]

            # Can land on an empty square or capture an enemy piece
            if target is None or target[0] != color:
                moves.append((r, c))

    return moves
##########################################################################################
##########################################################################################
def king_moves(board, row, col):
    moves = []
    color = board[row][col][0]   # "w" or "b"

    # Eight steps: one squares every direction
    steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for dr, dc in steps:
        r, c = row + dr, col + dc
        # Skip jumps that land outside the board
        if 0 <= r < 8 and 0 <= c < 8:
            target = board[r][c]

            # Can land on an empty square or capture an enemy piece
            if target is None or target[0] != color:
                moves.append((r, c))

    return moves
##########################################################################################
##########################################################################################
def queen_moves(board, row, col):
    return rook_moves(board, row, col) + bishop_moves(board, row, col)
##########################################################################################
##########################################################################################
def get_moves(board, row, col):
    piece = board[row][col]

    # Empty square - no moves
    if piece is None:
        return []

    kind = piece[1]   # "P", "R", "N", "B", "Q" or "K"

    if kind == "P":
        return pawn_moves(board, row, col)
    if kind == "R":
        return rook_moves(board, row, col)
    if kind == "N":
        return knight_moves(board, row, col)
    if kind == "B":
        return bishop_moves(board, row, col)
    if kind == "Q":
        return queen_moves(board, row, col)
    if kind == "K":
        return king_moves(board, row, col)
##########################################################################################
##########################################################################################
def move_piece(board, start, end):
    sr, sc = start
    er, ec = end

    captured = board[er][ec]          # what was on the target square (or None)
    board[er][ec] = board[sr][sc]     # put the piece on the target
    board[sr][sc] = None              # empty the start square

    return captured
##########################################################################################
##########################################################################################
def find_king(board, color):
    for row in range(8):
        for col in range(8):
            if board[row][col] == color + "K":
                return (row, col)
    return None
##########################################################################################
##########################################################################################
def is_in_check(board, color):

    king = find_king(board, color)  # find the king once

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if (piece is not None and piece[0] != color):
                moves = get_moves(board, row, col)
                if (king in moves):
                    return True
    # Checked every enemy piece - none attacks the king
    return False
##########################################################################################
##########################################################################################
def legal_moves(board, row, col):
    results = []
    color = board[row][col][0]   # "w" or "b"

    for r, c in get_moves(board, row, col):
        # Fresh copy of the board for every move
        test_board = [line[:] for line in board]

        # Try the move on the copy
        move_piece(test_board, (row, col), (r, c))

        # Keep the move only if our king is not in check after it
        if not is_in_check(test_board, color):
            results.append((r, c))

    return results
##########################################################################################
##########################################################################################
def has_any_legal_move(board, color):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]

            # Only our own pieces
            if piece is not None and piece[0] == color:
                if legal_moves(board, row, col) != []:
                    return True

    # No piece has a legal move
    return False
##########################################################################################
##########################################################################################
def is_checkmate(board, color):
    return is_in_check(board, color) and not has_any_legal_move(board, color)
##########################################################################################
##########################################################################################
def is_stalemate(board, color):
    return not is_in_check(board, color) and not has_any_legal_move(board, color)
##########################################################################################
##########################################################################################
def promote_pawn(board, row, col):
    piece = board[row][col]

    # Only pawns get promoted
    if piece is None or piece[1] != "P":
        return False

    # White promotes on row 0, black on row 7
    if (piece[0] == "w" and row == 0) or (piece[0] == "b" and row == 7):
        board[row][col] = piece[0] + "Q"     # same color, becomes a queen
        return True

    return False
##########################################################################################
##########################################################################################
def castling_moves(board, color, moved):
    moves = []
    row = 7 if color == "w" else 0     # the back row of this color

    # The king must be on its start square and never have moved
    if board[row][4] != color + "K" or (row, 4) in moved:
        return moves

    # Can't castle out of check
    if is_in_check(board, color):
        return moves

    # Short castling (king side): rook on column 7, squares 5 and 6 empty
    if (board[row][7] == color + "R" and (row, 7) not in moved
            and board[row][5] is None and board[row][6] is None):
        # The king may not pass through or land on an attacked square
        if square_is_safe(board, color, (row, 4), (row, 5)) and \
           square_is_safe(board, color, (row, 4), (row, 6)):
            moves.append((row, 6))

    # Long castling (queen side): rook on column 0, squares 1, 2 and 3 empty
    if (board[row][0] == color + "R" and (row, 0) not in moved
            and board[row][1] is None and board[row][2] is None and board[row][3] is None):
        if square_is_safe(board, color, (row, 4), (row, 3)) and \
           square_is_safe(board, color, (row, 4), (row, 2)):
            moves.append((row, 2))

    return moves


def square_is_safe(board, color, king_pos, square):
    # Put the king on the square (on a copy) and check if it would be in check
    test_board = [line[:] for line in board]
    move_piece(test_board, king_pos, square)
    return not is_in_check(test_board, color)
##########################################################################################
##########################################################################################
def en_passant_moves(board, row, col, last_move):
    moves = []
    piece = board[row][col]

    # Only a pawn, and only if there was a previous move
    if piece is None or piece[1] != "P" or last_move is None:
        return moves

    color = piece[0]
    direction = -1 if color == "w" else 1

    (sr, sc), (er, ec) = last_move
    last_piece = board[er][ec]

    # The last move must be an enemy pawn that moved two squares...
    if last_piece is None or last_piece[1] != "P" or last_piece[0] == color:
        return moves
    if abs(sr - er) != 2:
        return moves

    # ...and landed right next to our pawn, on the same row
    if er != row or abs(ec - col) != 1:
        return moves

    # The target square is diagonally forward, behind the enemy pawn
    target = (row + direction, ec)

    # Make sure the capture does not leave our king in check
    test_board = [line[:] for line in board]
    move_piece(test_board, (row, col), target)
    test_board[er][ec] = None                 # the captured pawn is removed separately
    if not is_in_check(test_board, color):
        moves.append(target)

    return moves
##########################################################################################
##########################################################################################
def all_legal_moves(board, row, col, moved, last_move):
    piece = board[row][col]

    # Empty square - no moves
    if piece is None:
        return []

    # Regular moves that don't leave the king in check
    moves = legal_moves(board, row, col)

    # Pawn - add en passant
    if piece[1] == "P":
        moves += en_passant_moves(board, row, col, last_move)

    # King - add castling
    if piece[1] == "K":
        moves += castling_moves(board, piece[0], moved)

    return moves
##########################################################################################
##########################################################################################
def make_move(board, start, end, moved):
    sr, sc = start
    er, ec = end
    piece = board[sr][sc]

    # The basic move
    captured = move_piece(board, start, end)

    # Castling: the king moved two columns - move the rook too
    if piece[1] == "K" and abs(ec - sc) == 2:
        if ec == 6:
            move_piece(board, (er, 7), (er, 5))    # short: rook jumps to column 5
        else:
            move_piece(board, (er, 0), (er, 3))    # long: rook jumps to column 3

    # En passant: a pawn moved diagonally onto an empty square - remove the pawn beside it
    if piece[1] == "P" and sc != ec and captured is None:
        captured = board[sr][ec]
        board[sr][ec] = None

    # Promotion
    promote_pawn(board, er, ec)

    # Remember that a piece left this square (for castling)
    moved.add((sr, sc))

    # Return the new last move (for en passant)
    return (start, end)

##########################################################################################
##########################################################################################
# Tests - run only when this file is run directly
if __name__ == "__main__":
    ##########################################################################################
    # Rook test 1: rook at the start is blocked by its own pieces
    result = rook_moves(board, 7, 0)
    print("Rook 1:", result)
    assert result == [], "Rook should have no moves at the start"

    # Rook test 2: remove the pawn in front - rook can go up to the black pawn
    test_board = [r[:] for r in board]   # copy, so the real board is not changed
    test_board[6][0] = None
    result = rook_moves(test_board, 7, 0)
    print("Rook 2:", result)
    assert result == [(6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0)]

    # Rook test 3: rook alone in the middle of an empty board - 14 moves
    empty = [[None] * 8 for _ in range(8)]
    empty[4][4] = "wR"
    result = rook_moves(empty, 4, 4)
    print("Rook 3:", len(result), "moves")
    assert len(result) == 14, "Rook in the middle should have 14 moves"
    ##########################################################################################
    # Pawn test 1: white pawn at the start can move 1 or 2 squares
    result = pawn_moves(board, 6, 4)
    print("Pawn 1:", result)
    assert result == [(5, 4), (4, 4)]

    # Pawn test 2: black pawn moves down
    result = pawn_moves(board, 1, 3)
    print("Pawn 2:", result)
    assert result == [(2, 3), (3, 3)]

    # Pawn test 3: blocked pawn can't move forward or capture forward
    empty = [[None] * 8 for _ in range(8)]
    empty[4][4] = "wP"
    empty[3][4] = "bP"
    result = pawn_moves(empty, 4, 4)
    print("Pawn 3:", result)
    assert result == []

    # Pawn test 4: captures an enemy diagonally, not its own piece
    empty = [[None] * 8 for _ in range(8)]
    empty[4][4] = "wP"
    empty[3][3] = "bN"   # enemy - can capture
    empty[3][5] = "wN"   # own piece - can't capture
    result = pawn_moves(empty, 4, 4)
    print("Pawn 4:", result)
    assert result == [(3, 4), (3, 3)]
    ##########################################################################################
    # Bishop test 1: bishop in the middle of an empty board - 13 moves
    empty = [[None] * 8 for _ in range(8)]
    empty[4][4] = "wB"
    result = bishop_moves(empty, 4, 4)
    print("Bishop 1:", len(result), "moves")
    assert len(result) == 13, "Bishop in the middle should have 13 moves"

    # Bishop test 2: check every diagonal is reachable
    assert (0, 0) in result, "up-left missing"
    assert (1, 7) in result, "up-right missing"
    assert (7, 1) in result, "down-left missing"
    assert (7, 7) in result, "down-right missing"
    print("Bishop 2: all 4 diagonals OK")
    ##########################################################################################
    # Knight test 1: knight in the middle of an empty board - 8 moves
    empty = [[None] * 8 for _ in range(8)]
    empty[4][4] = "wN"
    result = knight_moves(empty, 4, 4)
    print("Knight 1:", len(result), "moves")
    assert len(result) == 8

    # Knight test 2: knight in the corner - only 2 moves
    empty = [[None] * 8 for _ in range(8)]
    empty[7][0] = "wN"
    result = knight_moves(empty, 7, 0)
    print("Knight 2:", result)
    assert sorted(result) == [(5, 1), (6, 2)]

    # Knight test 3: at the start, knight jumps over the pawns
    result = knight_moves(board, 7, 1)
    print("Knight 3:", result)
    assert sorted(result) == [(5, 0), (5, 2)]
    ##########################################################################################
    # Queen test 1: queen in the middle of an empty board - 27 moves (14 rook + 13 bishop)
    empty = [[None] * 8 for _ in range(8)]
    empty[4][4] = "wQ"
    result = queen_moves(empty, 4, 4)
    print("Queen 1:", len(result), "moves")
    assert len(result) == 27

    # Queen test 2: at the start, the queen is blocked by her own pieces
    result = queen_moves(board, 7, 3)
    print("Queen 2:", result)
    assert result == []
    ##########################################################################################
    # King test 1: king in the middle of an empty board - 8 moves
    empty = [[None] * 8 for _ in range(8)]
    empty[4][4] = "wK"
    result = king_moves(empty, 4, 4)
    print("King 1:", len(result), "moves")
    assert len(result) == 8

    # King test 2: king in the corner - only 3 moves
    empty = [[None] * 8 for _ in range(8)]
    empty[7][0] = "wK"
    result = king_moves(empty, 7, 0)
    print("King 2:", sorted(result))
    assert sorted(result) == [(6, 0), (6, 1), (7, 1)]

    # King test 3: at the start, the king is surrounded by his own pieces
    result = king_moves(board, 7, 4)
    print("King 3:", result)
    assert result == []
    ##########################################################################################
    # get_moves test 1: empty square has no moves
    result = get_moves(board, 4, 4)
    print("get_moves 1:", result)
    assert result == []

    # get_moves test 2: calls the right function for each piece
    assert get_moves(board, 6, 4) == pawn_moves(board, 6, 4)
    assert get_moves(board, 7, 1) == knight_moves(board, 7, 1)
    assert get_moves(board, 0, 6) == knight_moves(board, 0, 6)
    print("get_moves 2: OK")

    ##########################################################################################
    # move_piece test: move the white pawn from e2 to e4
    test_board = [r[:] for r in board]
    move_piece(test_board, (6, 4), (4, 4))
    print("move_piece:", test_board[4][4], test_board[6][4])
    assert test_board[4][4] == "wP"    # pawn arrived
    assert test_board[6][4] is None    # old square is empty

    # move_piece test 2: capture returns the captured piece
    test_board = [r[:] for r in board]
    test_board[2][3] = "bP"                                  # black pawn at d6
    captured = move_piece(test_board, (6, 3), (2, 3))        # white pawn "jumps" there (just for the test)
    print("move_piece 2: captured", captured)
    assert captured == "bP"
    assert test_board[2][3] == "wP"
    ##########################################################################################
    # is_in_check test 1: nobody is in check at the start
    assert is_in_check(board, "w") == False
    assert is_in_check(board, "b") == False
    print("is_in_check 1: OK")

    # is_in_check test 2: rook attacks the king in a straight line
    empty = [[None] * 8 for _ in range(8)]
    empty[7][4] = "wK"
    empty[0][4] = "bR"
    assert is_in_check(empty, "w") == True
    print("is_in_check 2: OK")

    # is_in_check test 3: same rook, but a piece blocks the way
    empty[4][4] = "wP"
    assert is_in_check(empty, "w") == False
    print("is_in_check 3: OK")

    # is_in_check test 4: knight attacks over other pieces
    empty = [[None] * 8 for _ in range(8)]
    empty[7][4] = "wK"
    empty[5][3] = "bN"
    assert is_in_check(empty, "w") == True
    print("is_in_check 4: OK")
    ##########################################################################################
    # legal_moves test 1: king can't step into an attacked square
    empty = [[None] * 8 for _ in range(8)]
    empty[7][4] = "wK"
    empty[0][3] = "bR"          # black rook controls the whole d-file
    result = legal_moves(empty, 7, 4)
    print("legal_moves 1:", sorted(result))
    assert (7, 3) not in result and (6, 3) not in result

    # legal_moves test 2: pinned piece can't move off the line
    empty = [[None] * 8 for _ in range(8)]
    empty[7][4] = "wK"
    empty[5][4] = "wN"          # knight between king and rook
    empty[0][4] = "bR"
    result = legal_moves(empty, 5, 4)
    print("legal_moves 2:", result)
    assert result == []         # every knight move exposes the king
    ##########################################################################################
    # has_any_legal_move test 1: at the start both sides can move
    assert has_any_legal_move(board, "w") == True
    assert has_any_legal_move(board, "b") == True
    print("has_any_legal_move 1: OK")

    # has_any_legal_move test 2: back-rank mate - white has no legal move
    empty = [[None] * 8 for _ in range(8)]
    empty[7][6] = "wK"
    empty[6][5] = "wP"
    empty[6][6] = "wP"
    empty[6][7] = "wP"
    empty[7][0] = "bR"          # rook gives check on the back rank
    assert has_any_legal_move(empty, "w") == False
    print("has_any_legal_move 2: OK")
    ##########################################################################################
    # is_checkmate test 1: no checkmate at the start
    assert is_checkmate(board, "w") == False
    print("is_checkmate 1: OK")

    # is_checkmate test 2: back-rank mate
    empty = [[None] * 8 for _ in range(8)]
    empty[7][6] = "wK"
    empty[6][5] = "wP"
    empty[6][6] = "wP"
    empty[6][7] = "wP"
    empty[7][0] = "bR"
    assert is_checkmate(empty, "w") == True
    print("is_checkmate 2: OK")

    # is_checkmate test 3: same position, but a white rook can block - not mate
    empty[7][3] = "wR"
    assert is_checkmate(empty, "w") == False
    print("is_checkmate 3: OK")
    ##########################################################################################
    # is_stalemate test 1: no stalemate at the start
    assert is_stalemate(board, "w") == False
    print("is_stalemate 1: OK")

    # is_stalemate test 2: classic stalemate - black king in the corner, not in check, can't move
    empty = [[None] * 8 for _ in range(8)]
    empty[0][0] = "bK"          # black king at a8
    empty[2][1] = "wQ"          # white queen at b6 covers a7, b7, b8
    empty[7][7] = "wK"
    assert is_stalemate(empty, "b") == True
    assert is_checkmate(empty, "b") == False
    print("is_stalemate 2: OK")

    # is_stalemate test 3: back-rank mate is checkmate, not stalemate
    empty = [[None] * 8 for _ in range(8)]
    empty[7][6] = "wK"
    empty[6][5] = "wP"
    empty[6][6] = "wP"
    empty[6][7] = "wP"
    empty[7][0] = "bR"
    assert is_stalemate(empty, "w") == False
    print("is_stalemate 3: OK")
    ##########################################################################################
    # promote_pawn test: pawns on the last row become queens
    empty = [[None] * 8 for _ in range(8)]
    empty[0][3] = "wP"
    empty[7][2] = "bP"
    empty[3][3] = "wP"
    assert promote_pawn(empty, 0, 3) and empty[0][3] == "wQ"
    assert promote_pawn(empty, 7, 2) and empty[7][2] == "bQ"
    assert not promote_pawn(empty, 3, 3) and empty[3][3] == "wP"
    print("promote_pawn: OK")
    ##########################################################################################
    # castling_moves tests
    empty = [[None] * 8 for _ in range(8)]
    empty[7][4] = "wK"
    empty[7][7] = "wR"
    empty[7][0] = "wR"
    empty[0][4] = "bK"
    assert sorted(castling_moves(empty, "w", set())) == [(7, 2), (7, 6)]   # both sides
    assert castling_moves(empty, "w", {(7, 4)}) == []                      # king moved
    assert castling_moves(empty, "w", {(7, 7)}) == [(7, 2)]                # short rook moved
    test_board = [r[:] for r in empty]
    test_board[0][5] = "bR"                                                # attacks f1
    assert castling_moves(test_board, "w", set()) == [(7, 2)]
    test_board = [r[:] for r in empty]
    test_board[3][4] = "bR"                                                # king in check
    assert castling_moves(test_board, "w", set()) == []
    assert castling_moves(board, "w", set()) == []                         # start: pieces in the way
    print("castling_moves: OK")
    ##########################################################################################
    # en_passant_moves tests
    empty = [[None] * 8 for _ in range(8)]
    empty[7][4] = "wK"
    empty[0][4] = "bK"
    empty[3][4] = "wP"                  # white pawn on e5
    empty[3][3] = "bP"                  # black pawn on d5
    assert en_passant_moves(empty, 3, 4, ((1, 3), (3, 3))) == [(2, 3)]    # d7-d5 just happened
    assert en_passant_moves(empty, 3, 4, ((2, 3), (3, 3))) == []          # only moved one square
    assert en_passant_moves(empty, 3, 4, None) == []                      # no last move
    print("en_passant_moves: OK")
    ##########################################################################################
    # all_legal_moves test 1: at the start, same as legal_moves
    assert all_legal_moves(board, 6, 4, set(), None) == legal_moves(board, 6, 4)
    assert all_legal_moves(board, 4, 4, set(), None) == []
    print("all_legal_moves 1: OK")

    # all_legal_moves test 2: king gets castling moves
    empty = [[None] * 8 for _ in range(8)]
    empty[7][4] = "wK"
    empty[7][7] = "wR"
    empty[0][4] = "bK"
    assert (7, 6) in all_legal_moves(empty, 7, 4, set(), None)
    print("all_legal_moves 2: OK")

    # all_legal_moves test 3: pawn gets en passant
    empty = [[None] * 8 for _ in range(8)]
    empty[7][4] = "wK"
    empty[0][4] = "bK"
    empty[3][4] = "wP"
    empty[3][3] = "bP"
    assert (2, 3) in all_legal_moves(empty, 3, 4, set(), ((1, 3), (3, 3)))
    print("all_legal_moves 3: OK")
    ##########################################################################################
    # make_move test 1: short castling moves the rook too
    empty = [[None] * 8 for _ in range(8)]
    empty[7][4] = "wK"
    empty[7][7] = "wR"
    moved = set()
    last_move = make_move(empty, (7, 4), (7, 6), moved)
    assert empty[7][6] == "wK" and empty[7][5] == "wR" and empty[7][7] is None
    assert (7, 4) in moved
    assert last_move == ((7, 4), (7, 6))
    print("make_move 1: OK")

    # make_move test 2: en passant removes the captured pawn
    empty = [[None] * 8 for _ in range(8)]
    empty[3][4] = "wP"
    empty[3][3] = "bP"
    make_move(empty, (3, 4), (2, 3), set())
    assert empty[2][3] == "wP" and empty[3][3] is None
    print("make_move 2: OK")

    # make_move test 3: pawn reaching the last row becomes a queen
    empty = [[None] * 8 for _ in range(8)]
    empty[1][0] = "wP"
    make_move(empty, (1, 0), (0, 0), set())
    assert empty[0][0] == "wQ"
    print("make_move 3: OK")
    ##########################################################################################
    print("All tests passed!")