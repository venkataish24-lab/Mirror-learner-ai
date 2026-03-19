import json

def analyze_player_style():

    try:
        with open("progress.json", "r") as f:
            data = json.load(f)
    except:
        return None

    games = data.get("user_history", [])

    if len(games) < 5:
        return None

    last_games = games[-10:]

    captures = 0
    count = 0

    for g in last_games:
        captures += g.get("captures", 0)
        count += 1

    style = {
        "aggression": captures / max(count,1)
    }

    return style