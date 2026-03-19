import json
import os

DATA_FILE = "move_data.json"

def get_player_opening():

    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    if len(data) < 2:
        return None

    first_move = data[0]["piece"]

    return first_move