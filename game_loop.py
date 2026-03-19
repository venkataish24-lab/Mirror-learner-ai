
import chess
import random
import json
import torch
from stockfish import Stockfish
from neural_bias import NeuralBias
from pygame_board import play_human_turn
from mirror_analyzer import analyze_player_style
from move_tracker import track_move
from style_dna import compute_style_dna
from opening_dna import track_opening, choose_opening
from blunder_dna import track_blunder, get_blunder_rate

# ---------------- CONFIG ----------------
SF_PATH = r"C:\Users\venkataish\Mirror_Learner_AI\stockfish\stockfish-windows-x86-64-avx2.exe"
MODEL_PATH = "bias_model.pt"
MIN_ELO = 1320


# ---------------- PERSISTENCE ----------------
def save_progress(level, history):
    with open("progress.json", "w") as f:
        json.dump({"ai_level": level, "user_history": history}, f, indent=4)


def load_progress():
    try:
        with open("progress.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"ai_level": 1, "user_history": []}


# ---------------- ENGINE ----------------
class MirrorAI:
    def __init__(self, path):

        self.sf = Stockfish(path=path)

        self.bias_net = NeuralBias()
        self.bias_opt = torch.optim.Adam(self.bias_net.parameters(), lr=0.001)

        try:
            self.bias_net.load_state_dict(torch.load(MODEL_PATH))
            print("[SYSTEM] Neural bias model loaded.")
        except:
            print("[SYSTEM] Fresh neural bias model.")

        data = load_progress()
        self.level = data["ai_level"]
        self.history = data["user_history"]

        self.recent_results = []

        self.update_engine_strength()

    # ---------------- ENGINE STRENGTH ----------------
    def update_engine_strength(self):

        skill = max(0, min(20, self.level * 3))
        elo = 1320 + (self.level * 50)

        if elo < MIN_ELO:
            elo = MIN_ELO

        self.sf.set_skill_level(skill)
        self.sf.set_elo_rating(elo)

        print(f"[SYSTEM] AI Level: {self.level} | Elo: {elo} | Skill: {skill}")

    # ---------------- AI MOVE SELECTION ----------------
    def select_skill_move(self, board, style_dna):

        self.sf.set_fen_position(board.fen())

        # -------- OPENING DNA --------
        if board.fullmove_number == 1:
            opening = choose_opening()
            if opening:
                moves = opening.split()
                if len(moves) >= 2:
                    return moves[1]

        best_move = self.sf.get_best_move()

        if not best_move:
            return None

        # -------- BLUNDER DNA --------
        blunder_rate = get_blunder_rate()
        mistake_chance = max(0.05, min(0.4, blunder_rate))

        # -------- STYLE DNA --------
        if style_dna:

            aggression = style_dna.get("aggression", 0)

            if aggression > 0.30:
                mistake_chance *= 0.8

                capture_moves = []

                for move in board.legal_moves:
                    if board.is_capture(move):
                        capture_moves.append(move)

                if capture_moves and random.random() < 0.5:
                    return random.choice(capture_moves).uci()

            if aggression < 0.10:
                mistake_chance *= 1.2

        # -------- APPLY MISTAKE --------
        if random.random() < mistake_chance:

            legal_moves = list(board.legal_moves)

            if len(legal_moves) > 1:
                return random.choice(legal_moves).uci()

        return best_move

    # ---------------- MAIN GAME LOOP ----------------
    def play(self):

        while True:

            board = chess.Board()

            pawn_moves = 0
            captures = 0
            checks = 0

            # -------- STYLE DNA --------
            style_dna = compute_style_dna()
            if style_dna:
                print("[STYLE DNA]", style_dna)

            # -------- MIRROR STYLE --------
            mirror_style = analyze_player_style()
            if mirror_style:
                print("[MIRROR STYLE]", mirror_style)

            print("\n--- NEW SESSION (GUI MODE) ---")

            while not board.is_game_over():

                # -------- HUMAN MOVE --------
                play_human_turn(board)

                last_move = board.peek()

                # -------- TRACK EVERYTHING --------
                track_opening(board)
                track_move(board, last_move)
                track_blunder(board, last_move)

                piece = board.piece_at(last_move.to_square)

                if piece and piece.piece_type == chess.PAWN:
                    pawn_moves += 1

                if board.is_capture(last_move):
                    captures += 1

                if board.is_check():
                    checks += 1

                if board.is_game_over():
                    break

                # -------- AI MOVE --------
                ai_move = self.select_skill_move(board, style_dna)

                if not ai_move:
                    print("AI returned no move.")
                    break

                board.push_uci(ai_move)

            # ---------------- GAME END ----------------
            result = board.result()
            print("Result:", result)

            print("Checkmate:", board.is_checkmate())
            print("Stalemate:", board.is_stalemate())
            print("Insufficient material:", board.is_insufficient_material())
            print("50-move rule:", board.can_claim_fifty_moves())
            print("Repetition:", board.is_repetition())
            print("---------------")

            # ---------------- AUTO DIFFICULTY ----------------
            if result == "1-0":
                self.recent_results.append(1)
            elif result == "0-1":
                self.recent_results.append(0)

            if len(self.recent_results) > 4:
                self.recent_results.pop(0)

            if len(self.recent_results) >= 4:

                win_rate = sum(self.recent_results) / len(self.recent_results)

                if win_rate >= 0.75:
                    self.level += 1
                    print("[SYSTEM] Player dominating → increasing difficulty")
                    self.update_engine_strength()

                elif win_rate <= 0.25:
                    self.level = max(0, self.level - 1)
                    print("[SYSTEM] Player struggling → reducing difficulty")
                    self.update_engine_strength()

            # ---------------- SAVE ----------------
            self.history.append({
                "result": result,
                "captures": captures,
                "pawn_moves": pawn_moves,
                "checks": checks
            })

            save_progress(self.level, self.history)

            again = input("Play again? (y/n): ")
            if again.lower() != "y":
                break


# ---------------- RUN ----------------
if __name__ == "__main__":
    MirrorAI(SF_PATH).play()






