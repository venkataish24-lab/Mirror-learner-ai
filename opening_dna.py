
import json
import os
import random

DATA_FILE = "opening_data.json"



def track_opening(board):

    if board.fullmove_number > 3:
        return

    moves = [move.uci() for move in board.move_stack[:6]]

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    key = " ".join(moves)

    if key not in data:
        data[key] = 0

    data[key] += 1

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def choose_opening():

    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if not data:
        return None

    openings = list(data.keys())
    weights = list(data.values())

    return random.choices(openings, weights=weights)[0]