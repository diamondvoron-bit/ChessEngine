#import os              uncomment the top two if on KDE plasma
import multiprocessing

#os.environ["SDL_VIDEODRIVER"] = "x11"

import chess
import pygame
import draw
import engine


BLACK = (0, 0, 0)
BOARD_SIZE = 800

pygame.init()
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()
board = chess.Board()
draw.scale_pieces()
engine_state = False

selected_square = None
running = True

def run_engine():
    """Return the engine's move for the current board position."""
    maximizing = board.turn == chess.WHITE
    move = engine.engine(maximizing, board)
    global engine_state
    engine_state = False
    return move


def square_from_mouse(position):
    x, y = position
    tile_size = BOARD_SIZE // 8
    return chess.square(x // tile_size, 7 - (y // tile_size))


def player_move(from_square, to_square):
    piece = board.piece_at(from_square)
    promotion = None
    if piece is not None and piece.piece_type == chess.PAWN:
        if chess.square_rank(to_square) == 7:
            promotion = chess.QUEEN
    return chess.Move(from_square, to_square, promotion=promotion)
    

if __name__ == "__main__":
    multiprocessing.freeze_support()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and board.turn == chess.WHITE
                and not board.is_game_over()
            ):
                clicked_square = square_from_mouse(event.pos)
                clicked_piece = board.piece_at(clicked_square)

                if selected_square is None:
                    if clicked_piece is not None and clicked_piece.color == chess.WHITE:
                        selected_square = clicked_square
                else:
                    move = player_move(selected_square, clicked_square)
                    if move in board.legal_moves:
                        board.push(move)
                        selected_square = None
                    elif clicked_piece is not None and clicked_piece.color == chess.WHITE:
                        selected_square = clicked_square
                    else:
                        selected_square = None

        if running and board.turn == chess.BLACK and not board.is_game_over() and not engine_state:
            engine_state = True
            move = run_engine()
            if move is not None:
                board.push(move)
        screen.fill(BLACK)
        legal_targets = set()
        if selected_square is not None:
            legal_targets = {
                move.to_square
                for move in board.legal_moves
                if move.from_square == selected_square
            }
        draw.draw_board(screen, board, size=BOARD_SIZE, selected_square=selected_square, legal_targets=legal_targets)
        pygame.display.flip()
        clock.tick(20)

pygame.quit()
