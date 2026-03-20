import chess
import random
import json
import torch
from stockfish import Stockfish
from neural_bias import NeuralBias, board_features
from pygame_board import play_human_turn
from move_tracker import track_move
from style_dna import compute_style_dna
from opening_dna import track_opening, choose_opening
from blunder_dna import track_blunder, get_blunder_rate

# ---------------- CONFIG ----------------
SF_PATH = r"C:\Users\venkataish\Mirror_Learner_AI\stockfish\stockfish-windows-x86-64-avx2.exe"
MODEL_PATH = "bias_model.pt"
MIN_ELO = 1320


# ---------------- PATTERN MEMORY ----------------
def load_patterns():
    try:
        with open("patterns.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save_patterns(data):
    with open("patterns.json", "w") as f:
        json.dump(data, f, indent=4)


# ---------------- PERSONALITY ----------------
def load_personality():
    try:
        with open("personality.json", "r") as f:
            return json.load(f)
    except:
        return None


def save_personality(style_dna):
    with open("personality.json", "w") as f:
        json.dump(style_dna, f, indent=4)


# ---------------- LEARNING ----------------
def load_learning():
    try:
        with open("learning.json", "r") as f:
            return json.load(f)
    except:
        return {"wins": 0, "losses": 0}


def save_learning(data):
    with open("learning.json", "w") as f:
        json.dump(data, f, indent=4)


# ---------------- HABIT MEMORY ----------------
def load_habits():
    try:
        with open("habits.json", "r") as f:
            return json.load(f)
    except:
        return {"piece_usage": {}}


def save_habits(data):
    with open("habits.json", "w") as f:
        json.dump(data, f, indent=4)


# ---------------- NEURAL SCORE ----------------
def neural_score(ai, board, move, style_dna):
    try:
        board.push(move)

        style_type = "aggressive" if style_dna and style_dna.get("aggression", 0) > 0.2 else "normal"
        features = board_features(board, style_type)

        with torch.no_grad():
            score = ai.bias_net(features).item()

        board.pop()
        return score

    except:
        try:
            board.pop()
        except:
            pass
        return 0


# ---------------- GAME MODE ----------------
def detect_game_mode(board):
    king_square = board.king(board.turn)
    attackers = board.attackers(not board.turn, king_square)

    if len(attackers) >= 2:
        return "defense"

    if board.is_check():
        return "attack"

    return "normal"


# ---------------- EMOTION ----------------
def apply_emotion(score, move, board, emotion):

    if emotion == "revenge":
        if board.is_capture(move):
            score += 6

    if emotion == "tilt":
        score -= random.randint(0, 5)

    if emotion == "confident":
        if board.gives_check(move):
            score += 4

    return score


# ---------------- STYLE ----------------
def score_move(board, move, style_dna, mode):
    score = 0

    if not style_dna:
        return score

    piece = board.piece_at(move.from_square)

    if board.is_capture(move):
        score += style_dna.get("capture_frequency", 0) * 10
        if mode == "attack":
            score += 5

    if board.gives_check(move):
        score += style_dna.get("check_frequency", 0) * 8
        if mode == "attack":
            score += 5

    if piece and piece.piece_type == chess.PAWN:
        score += style_dna.get("pawn_usage", 0) * 5

    if mode == "defense":
        if board.is_capture(move):
            score -= 3

    score += style_dna.get("risk", 0) * 6

    if board.gives_check(move):
        score += style_dna.get("tempo", 0) * 5

    return score


# ---------------- SAVE/LOAD ----------------
def save_progress(level, history):
    with open("progress.json", "w") as f:
        json.dump({"ai_level": level, "user_history": history}, f, indent=4)


def load_progress():
    try:
        with open("progress.json", "r") as f:
            return json.load(f)
    except:
        return {"ai_level": 1, "user_history": []}


# ---------------- ENGINE ----------------
class MirrorAI:
    def __init__(self, path):

        self.sf = Stockfish(path=path)

        self.bias_net = NeuralBias()
        self.bias_opt = torch.optim.Adam(self.bias_net.parameters(), lr=0.001)

        try:
            self.bias_net.load_state_dict(torch.load(MODEL_PATH))
        except:
            pass

        data = load_progress()
        self.level = data["ai_level"]
        self.history = data["user_history"]

        self.emotion = "neutral"
        self.personality = load_personality()
        self.learning = load_learning()
        self.habits = load_habits()
        self.patterns = load_patterns()

        self.move_memory = []

        self.update_engine_strength()

    def update_engine_strength(self):
        skill = max(0, min(20, self.level * 3))
        elo = 1320 + (self.level * 50)

        if elo < MIN_ELO:
            elo = MIN_ELO

        self.sf.set_skill_level(skill)
        self.sf.set_elo_rating(elo)

    def update_emotion(self, board, last_move):

        if board.is_capture(last_move):
            self.emotion = "revenge"

        blunder_rate = get_blunder_rate()

        if blunder_rate > 0.3:
            self.emotion = "tilt"
        elif blunder_rate < 0.1:
            self.emotion = "confident"

    def select_skill_move(self, board, style_dna):

        # 🔥 CLONE LOGIC
        fen = board.board_fen()
        if fen in self.patterns:
            moves = self.patterns[fen]
            best = max(moves, key=moves.get)
            if best in [m.uci() for m in board.legal_moves]:
                return best

        self.sf.set_fen_position(board.fen())

        if board.fullmove_number <= 3:
            opening = choose_opening()
            if opening:
                moves = opening.split()
                idx = board.fullmove_number - 1
                if idx < len(moves):
                    return moves[idx]

        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        mode = detect_game_mode(board)
        style = dict(style_dna) if style_dna else {}

        most_used_piece = None
        if self.habits["piece_usage"]:
            most_used_piece = max(self.habits["piece_usage"], key=self.habits["piece_usage"].get)

        scored_moves = []

        for move in legal_moves:
            score = score_move(board, move, style, mode)
            score += neural_score(self, board, move, style) * 15
            score = apply_emotion(score, move, board, self.emotion)

            if most_used_piece:
                piece = board.piece_at(move.from_square)
                if piece and piece.symbol().lower() == most_used_piece:
                    score += 3

            scored_moves.append((move, score))

        scored_moves.sort(key=lambda x: x[1], reverse=True)

        best_move = scored_moves[0][0]

        self.move_memory.append({
            "board": board.fen(),
            "move": best_move.uci()
        })

        return best_move.uci()

    def play(self):

        while True:

            board = chess.Board()
            live_style = compute_style_dna()
            style_dna = self.personality if self.personality else live_style

            while not board.is_game_over():

                play_human_turn(board)
                last_move = board.peek()

                track_opening(board)
                track_move(board, last_move)
                track_blunder(board, last_move)

                # 🔥 PATTERN STORE
                fen = board.board_fen()
                if fen not in self.patterns:
                    self.patterns[fen] = {}

                move_str = last_move.uci()
                if move_str not in self.patterns[fen]:
                    self.patterns[fen][move_str] = 0

                self.patterns[fen][move_str] += 1
                save_patterns(self.patterns)

                # HABITS
                piece = board.piece_at(last_move.to_square)
                if piece:
                    p = piece.symbol().lower()
                    self.habits["piece_usage"][p] = self.habits["piece_usage"].get(p, 0) + 1
                save_habits(self.habits)

                self.update_emotion(board, last_move)

                if board.is_game_over():
                    break

                ai_move = self.select_skill_move(board, style_dna)
                if not ai_move:
                    break

                board.push_uci(ai_move)

            result = board.result()
            print("Result:", result)

            reward = 1 if result == "0-1" else -1

            for mem in self.move_memory:
                try:
                    temp_board = chess.Board(mem["board"])
                    move = chess.Move.from_uci(mem["move"])
                    temp_board.push(move)

                    features = board_features(temp_board, "aggressive")
                    pred = self.bias_net(features)

                    target = torch.tensor([reward], dtype=torch.float32)
                    loss = (pred - target).pow(2).mean()

                    self.bias_opt.zero_grad()
                    loss.backward()
                    self.bias_opt.step()

                except:
                    continue

            self.move_memory = []

            torch.save(self.bias_net.state_dict(), MODEL_PATH)

            if input("Play again? (y/n): ").lower() != "y":
                break


if __name__ == "__main__":
    MirrorAI(SF_PATH).play()






