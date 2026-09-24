import chess
from multiprocessing import Process
from concurrent.futures import ProcessPoolExecutor

white = chess.WHITE
black = chess.BLACK
neg_inf = float('-inf')
inf = float('inf')
counter = 0
values = {
    chess.PAWN: 100,
    chess.KNIGHT: 305,
    chess.BISHOP: 320,
    chess.ROOK: 500,
    chess.QUEEN: 950,
    chess.KING: 999999999999
}

def _table(rows):
    return [value for row in reversed(rows) for value in row]

piece_square_tables = {
    chess.PAWN: _table([
        [0,0,0,0,0,0,0,0], [50,50,50,50,50,50,50,50],
        [10,10,20,30,30,20,10,10], [5,5,10,25,25,10,5,5],
        [0,0,0,20,20,0,0,0], [5,-5,-10,0,0,-10,-5,5],
        [5,10,10,-20,-20,10,10,5], [0,0,0,0,0,0,0,0]
    ]),
    chess.KNIGHT: _table([
        [-50,-40,-30,-30,-30,-30,-40,-50], [-40,-20,0,5,5,0,-20,-40],
        [-30,5,10,15,15,10,5,-30], [-30,0,15,20,20,15,0,-30],
        [-30,5,15,20,20,15,5,-30], [-30,0,10,15,15,10,0,-30],
        [-40,-20,0,0,0,0,-20,-40], [-50,-40,-30,-30,-30,-30,-40,-50]
    ]),
    chess.BISHOP: _table([
        [-20,-10,-10,-10,-10,-10,-10,-20], [-10,0,0,0,0,0,0,-10],
        [-10,0,5,10,10,5,0,-10], [-10,5,5,10,10,5,5,-10],
        [-10,0,10,10,10,10,0,-10], [-10,10,10,10,10,10,10,-10],
        [-10,5,0,0,0,0,5,-10], [-20,-10,-10,-10,-10,-10,-10,-20]
    ]),
    chess.ROOK: _table([
        [0,0,0,5,5,0,0,0], [-5,0,0,0,0,0,0,-5], [-5,0,0,0,0,0,0,-5],
        [-5,0,0,0,0,0,0,-5], [-5,0,0,0,0,0,0,-5], [-5,0,0,0,0,0,0,-5],
        [5,10,10,10,10,10,10,5], [0,0,0,0,0,0,0,0]
    ]),
    chess.QUEEN: _table([
        [-20,-10,-10,0,0,-10,-10,-20], [-10,0,0,0,0,0,0,-10],
        [-10,0,5,5,5,5,0,-10], [0,0,5,5,5,5,0,-5],
        [-5,0,5,5,5,5,0,-5], [-10,5,5,5,5,5,0,-10],
        [-10,0,5,0,0,0,0,-10], [-20,-10,-10,0,0,-10,-10,-20]
    ]),
    chess.KING: _table([
        [-30,-40,-40,-50,-50,-40,-40,-30], [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30], [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20], [-10,-20,-20,-20,-20,-20,-20,-10],
        [20,20,0,0,0,0,20,20], [20,30,10,0,0,10,30,20]
    ])
}

def piece_square_value(piece, square):
    if piece.color == chess.BLACK:
        square = chess.square_mirror(square)
    return piece_square_tables[piece.piece_type][square]

def evalulate(board):
    score = 0

    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -1000000
        return 1000000

    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    for square, piece in board.piece_map().items():
        value = values[piece.piece_type] + (piece_square_value(piece, square)*0.55)

        if piece.color == chess.WHITE:
            score += value
        else:
            score -= value

    #side_mobility = board.legal_moves.count()
    #board.push(chess.Move.null())
    #other_mobility = board.legal_moves.count()
    #board.pop()

    #if board.turn == chess.WHITE:
    #    white_mobility, black_mobility = side_mobility, other_mobility
    #else:
    #    white_mobility, black_mobility = other_mobility, side_mobility
    #
    #score += 5 * (white_mobility - black_mobility)
    # enable for best play takes very long though

    return score

def engine(turn, board):
    global counter
    counter = 0
    depth = 3
    num = list(board.legal_moves)
    mid1 =  mid2 = mid3 = None
    if len(num) >= 4:
        mid1, mid2, mid3 = [len(num) * i // 4 for i in range(1, 4)]
    elif len(num) >= 2:
        mid1 = len(num) // 2
    mids = [mid1, mid2, mid3]
    with ProcessPoolExecutor(max_workers=4) as executor:
        if mid3 is not None:
            func1 = executor.submit(minimax, board, depth, turn, neg_inf, inf, mids, 0)
            func2 = executor.submit(minimax, board, depth, turn, neg_inf, inf, mids, 1)
            func3 = executor.submit(minimax, board, depth, turn, neg_inf, inf, mids, 2)
            func4 = executor.submit(minimax, board, depth, turn, neg_inf, inf, mids, 3)
            values = [func1.result(), func2.result(), func3.result(), func4.result()]
            best_index = max if turn else min
            highest_index = best_index(range(len(values)), key=lambda i: values[i][0])
            eval, move = values[highest_index]

        elif mid1 is not None:
            func1 = executor.submit(minimax, board, depth, turn, neg_inf, inf, mids, 0)
            func2 = executor.submit(minimax, board, depth, turn, neg_inf, inf, mids, 1)
            values = [func1.result(), func2.result()]
            best_index = max if turn else min
            highest_index = best_index(range(len(values)), key=lambda i: values[i][0])
            eval, move = values[highest_index]

        else:
            func1 = executor.submit(minimax, board, depth, turn, neg_inf, inf, mids, 0)
            eval, move = func1.result()
    print(eval/100, " searched ", counter)
    return move

def minimax(board, depth, maximizing, alpha = neg_inf, beta = inf, filter=None, pos = 0):
    if filter is None:
        position = sorted(
        board.legal_moves,
        key=lambda move: board.is_capture(move),
        reverse=True
        )
    elif pos == 0:
        position = sorted(
        board.legal_moves,
        key=lambda move: board.is_capture(move),
        reverse=True
        )[:filter[0]]
    elif pos==1:
            position = sorted(
            board.legal_moves,
            key=lambda move: board.is_capture(move),
            reverse=True
            )[filter[0]:filter[1]]
    elif pos==2:
            position = sorted(
            board.legal_moves,
            key=lambda move: board.is_capture(move),
            reverse=True
            )[filter[1]:filter[2]]
    elif pos==3:
        position = sorted(
        board.legal_moves,
        key=lambda move: board.is_capture(move),
        reverse=True
        )[filter[2]:]
    bestmove = None
    if depth == 0:
        return evalulate(board), None
    if maximizing:
        maxEval = neg_inf
        for child in position:
            board.push(child)
            eval, move = minimax(board, depth -1, False, alpha, beta)
            if maxEval < eval:
                bestmove = child
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            board.pop()
            if beta <= alpha:
                break
        return maxEval, bestmove
    else:
        minEval = inf
        for child in position:
            board.push(child)
            eval, move = minimax(board, depth -1, True, alpha, beta)
            if minEval > eval:
                bestmove = child
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            board.pop()
            if beta <= alpha:
                break
        return minEval, bestmove
