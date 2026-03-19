import json
import os

DATA_FILE = "blunder_data.json"


def track_blunder(board, move):

    if not os.path.exists(DATA_FILE):
        data = []
    else:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

    piece = board.piece_at(move.to_square)

    # simple blunder logic
    blunder = False

    if piece:
        # agar move ke baad piece attack me aa gaya
        if board.is_attacked_by(not board.turn, move.to_square):
            blunder = True

    data.append({
        "blunder": blunder
    })

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_blunder_rate():

    if not os.path.exists(DATA_FILE):
        return 0

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if not data:
        return 0

    total = len(data)
    blunders = sum(1 for d in data if d["blunder"])

    return blunders / total
