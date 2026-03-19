
import json

DATA_FILE = "move_data.json"

def compute_style_dna():

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        return None

    if len(data) == 0:
        return None

    total_moves = len(data)
    captures = 0
    checks = 0
    pawn_moves = 0

    for m in data:

        if m["capture"]:
            captures += 1

        if m["check"]:
            checks += 1

        if m["piece"] == "p":
            pawn_moves += 1

    style = {
        "aggression": round((captures + checks) / total_moves, 2),
        "capture_frequency": round(captures / total_moves, 2),
        "pawn_usage": round(pawn_moves / total_moves, 2),
        "check_frequency": round(checks / total_moves, 2)
    }

    return style
