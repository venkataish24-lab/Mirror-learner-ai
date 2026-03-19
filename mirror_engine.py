import random

def mirror_move_adjustment(board, best_move, style):

    if not best_move:
        return best_move

    aggression = style.get("aggression", 0)
    captures = style.get("capture_frequency", 0)

    legal_moves = list(board.legal_moves)

    # Aggressive player mirror
    if aggression > 10:

        capture_moves = []

        for move in legal_moves:
            if board.is_capture(move):
                capture_moves.append(move)

        if capture_moves and random.random() < 0.6:
            return random.choice(capture_moves).uci()

    # Passive player mirror
    if aggression < 4:

        quiet_moves = []

        for move in legal_moves:
            if not board.is_capture(move):
                quiet_moves.append(move)

        if quiet_moves and random.random() < 0.5:
            return random.choice(quiet_moves).uci()

    return best_move