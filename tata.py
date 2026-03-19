from stockfish import Stockfish

# REPLACE with your actual path from Step 1
path_to_engine = r"C:\Users\venkataish\Mirror_Learner_AI\stockfish\stockfish-windows-x86-64-avx2.exe"

class StockfishManager:
    def __init__(self, engine_path):
        # Initialize the engine
        self.sf = Stockfish(path=engine_path)
    
    def set_difficulty(self, current_level):
        """Sets AI strength based on your Level 1 Calibration"""
        # We use ElO rating to throttle Level 1 strength
        # Level 1 = 1350 Elo, Level 2 = 1400 Elo, etc.
        new_elo = 1300 + (current_level * 50)
        self.sf.set_elo_rating(new_elo)
        print(f"AI adjusted to Elo: {new_elo}")

# Build the connection
try:
    my_ai = StockfishManager( r"C:\Users\venkataish\Mirror_Learner_AI\stockfish\stockfish-windows-x86-64-avx2.exe")
    my_ai.set_difficulty(1) # Start at Level 1
    print("Success: Stockfish is now linked to your Mirror model.")
except Exception as e:
    print(f"Error: Could not find Stockfish at that path. Details: {e}")
