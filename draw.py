import pygame
from io import BytesIO
import cairosvg
import chess

white_sqaure = ("#EBECD0") 
black_sqaure = ("#779556")

wk = None
wq = None
wb = None
wr = None
wn = None
wp = None
bk = None
bq = None
bb = None
br = None
bn = None
bp = None

lookup = {
    'r':'br',
    'n':'bn',
    'b':'bb',
    'q':'bq',
    'k':'bk',
    'p':'bp',
    'R':'wr',
    'N':'wn',
    'B':'wb',
    'Q':'wq',
    'K':'wk',
    'P':'wp',
    None:None
}

def load_svg(path, size):
    png = cairosvg.svg2png(
        url=path,
        output_width=size,
        output_height=size,
    )
    return pygame.image.load(BytesIO(png))

def scale_pieces(size = 800):
    size = 90

    global wk
    global wq
    global wb
    global wr
    global wn
    global wp
    global bk
    global bq
    global bb
    global br
    global bn
    global bp
    wk = load_svg("./pieces/wK.svg", size)
    wq = load_svg("./pieces/wQ.svg", size)
    wb = load_svg("./pieces/wB.svg", size)
    wr = load_svg("./pieces/wR.svg", size)
    wn = load_svg("./pieces/wN.svg", size)
    wp = load_svg("./pieces/wP.svg", size)
    bk = load_svg("./pieces/bK.svg", size)
    bq = load_svg("./pieces/bQ.svg", size)
    bb = load_svg("./pieces/bB.svg", size)
    br = load_svg("./pieces/bR.svg", size)
    bn = load_svg("./pieces/bN.svg", size)
    bp = load_svg("./pieces/bP.svg", size)

def draw_board(screen, board, size=800, selected_square=None, legal_targets=None):
    tile_size = size/8
    legal_targets = legal_targets or set()
    for y in range(8):
        for x in range(8):
            color = (white_sqaure if (x+y) % 2 == 0 else black_sqaure)
            square = chess.square(x, 7 - y)
            piece = board.piece_at(square)
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            pygame.draw.rect(screen, color, rect)

            if square == selected_square:
                pygame.draw.rect(screen, (246, 246, 105), rect, width=5)
            elif square in legal_targets:
                center = rect.center
                if piece is None:
                    pygame.draw.circle(screen, (80, 80, 80), center, int(tile_size * 0.14))
                else:
                    pygame.draw.circle(screen, (200, 60, 60), center, int(tile_size * 0.46), width=5)

            if piece is not None:
                piece_name = lookup[piece.symbol()]
                piece_image = globals()[piece_name]

                piece_rect = piece_image.get_rect(
                    center=(
                        x * tile_size + tile_size / 2,
                        y * tile_size + tile_size / 2,
                    )
                )

                screen.blit(piece_image, piece_rect)
