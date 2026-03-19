class Level1Shadow:
    def __init__(self):
        self.ai_level = 1  # Starting depth
        self.user_history = []

    def calibrate(self, user_win):
        self.user_history.append(user_win)
        # Keep only the last 10 games
        if len(self.user_history) > 10:
            self.user_history.pop(0)
            
        win_rate = sum(self.user_history) / len(self.user_history)
        
        # The Evolution Algorithm (Syncing the learning)
        if win_rate > 0.55:
            self.ai_level += 1  # AI levels up with you
            print(f"User is learning! AI increasing level to {self.ai_level}")
        elif win_rate < 0.45:
            print("User struggling. AI freezing level.")
