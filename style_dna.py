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

    total = len(data)

    captures = sum(1 for m in data if m["capture"])
    checks = sum(1 for m in data if m["check"])
    pawn_moves = sum(1 for m in data if m["piece"] == "p")

    # 🔥 NEW FEATURES
    early_moves = data[:10]

    early_captures = sum(1 for m in early_moves if m["capture"])
    early_checks = sum(1 for m in early_moves if m["check"])

    # risk = early aggression
    risk = (early_captures + early_checks) / max(len(early_moves), 1)

    # tempo = fast aggressive play
    tempo = checks / total

    style = {
        "aggression": round((captures + checks) / total, 2),
        "capture_frequency": round(captures / total, 2),
        "check_frequency": round(checks / total, 2),
        "pawn_usage": round(pawn_moves / total, 2),

        # 🔥 NEW DNA
        "risk": round(risk, 2),
        "tempo": round(tempo, 2)
    }

    return style

