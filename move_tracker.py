
import json
import os

DATA_FILE = "move_data.json"

def track_move(board, move):

    piece = board.piece_at(move.to_square)

    move_data = {
        "piece": piece.symbol().lower() if piece else None,
        "capture": board.is_capture(move),
        "check": board.is_check(),
        "move_number": board.fullmove_number
    }

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(move_data)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

