import torch
import torch.nn as nn
import torch.optim as optim

# Small NN: preference only (not best move)
class NeuralBias(nn.Module):
    def __init__(self, input_size=20):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 32),
            nn.ReLU(),
            nn.Linear(32, 1)   # preference score
        )

    def forward(self, x):
        return self.net(x)

# helper
def board_features(board, human_style):
    # VERY simple features (safe)
    return torch.tensor([
        board.fullmove_number / 100.0,          # game progress
        len(list(board.legal_moves)) / 50.0,    # mobility
        1.0 if board.is_check() else 0.0,        # pressure
        1.0 if human_style == "aggressive" else 0.0,
    ] + [0.0]*16)  # pad to 20
