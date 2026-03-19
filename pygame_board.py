import pygame
import chess
import sys
import os

# -------- CONFIG --------
WIDTH, HEIGHT = 480, 480
SQ_SIZE = WIDTH // 8

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
SELECT = (0, 255, 0)
MOVE_HINT = (50, 200, 50)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mirror Learner Chess")

# -------- LOAD PIECE IMAGES --------
IMAGES = {}

def load_images():
    base_path = os.path.join(os.path.dirname(__file__), "pieces")

    for p in ["p","r","n","b","q","k"]:

        IMAGES["w"+p] = pygame.transform.scale(
            pygame.image.load(os.path.join(base_path,f"w{p}.png")),
            (SQ_SIZE,SQ_SIZE)
        )

        IMAGES["b"+p] = pygame.transform.scale(
            pygame.image.load(os.path.join(base_path,f"b{p}.png")),
            (SQ_SIZE,SQ_SIZE)
        )

load_images()

# -------- DRAW BOARD --------
def draw_board(board, selected_sq=None, legal_moves=None):

    for row in range(8):
        for col in range(8):

            color = LIGHT if (row+col)%2==0 else DARK
            rect = pygame.Rect(col*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE)

            pygame.draw.rect(screen,color,rect)

            sq = chess.square(col,7-row)

            # selected highlight
            if selected_sq == sq:
                pygame.draw.rect(screen,SELECT,rect,4)

            # legal move hint
            if legal_moves:
                for move in legal_moves:
                    if move.to_square == sq:
                        center = (
                            col*SQ_SIZE + SQ_SIZE//2,
                            row*SQ_SIZE + SQ_SIZE//2
                        )
                        pygame.draw.circle(screen,MOVE_HINT,center,8)

            piece = board.piece_at(sq)

            if piece:
                key = ("w" if piece.color==chess.WHITE else "b")+piece.symbol().lower()
                screen.blit(IMAGES[key],rect)

    pygame.display.flip()

# -------- MOUSE TO SQUARE --------
def get_square_from_mouse(pos):

    x,y = pos

    col = x//SQ_SIZE
    row = y//SQ_SIZE

    return chess.square(col,7-row)

# -------- GET LEGAL MOVES --------
def get_legal_moves(board,square):

    moves = []

    for move in board.legal_moves:
        if move.from_square == square:
            moves.append(move)

    return moves

# -------- HUMAN TURN --------
def play_human_turn(board):

    selected = None
    legal_moves = []

    while True:

        draw_board(board,selected,legal_moves)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                sq = get_square_from_mouse(pygame.mouse.get_pos())

                # select piece
                if selected is None:

                    piece = board.piece_at(sq)

                    if piece and piece.color == board.turn:
                        selected = sq
                        legal_moves = get_legal_moves(board,sq)

                else:

                    piece = board.piece_at(selected)

                    # -------- PROMOTION CHECK --------
                    if piece and piece.piece_type == chess.PAWN:

                        rank = chess.square_rank(sq)

                        if (piece.color==chess.WHITE and rank==7) or \
                           (piece.color==chess.BLACK and rank==0):

                            move = chess.Move(selected,sq,promotion=chess.QUEEN)

                        else:
                            move = chess.Move(selected,sq)

                    else:
                        move = chess.Move(selected,sq)

                    # -------- EXECUTE MOVE --------
                    if move in board.legal_moves:

                        board.push(move)
                        return

                    selected = None
                    legal_moves = []
