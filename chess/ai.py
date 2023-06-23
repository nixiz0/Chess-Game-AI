import random


pieceScore = {'K':0, 'Q':10, 'R':5, 'B':3, 'N':3, 'p':1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores =  [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores =  [ [4, 3, 4, 4, 4, 4, 3, 4],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [1, 1, 2, 3, 3, 2, 1, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 1, 2, 2, 2, 2, 1, 1],
                [4, 4, 4, 4, 4, 4, 4, 4],
                [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScores =  [[8, 8, 8, 8, 8, 8, 8, 8],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores =  [[0, 0, 0, 0, 0, 0, 0, 0],
                    [1, 1, 1, 0, 0, 1, 1, 1],
                    [1, 1, 2, 3, 3, 2, 1, 1],
                    [1, 2, 3, 4, 4, 3, 2, 1],
                    [2, 3, 3, 5, 5, 3, 3, 2],
                    [5, 6, 6, 7, 7, 6, 6, 5],
                    [8, 8, 8, 8, 8, 8, 8, 8],
                    [8, 8, 8, 8, 8, 8, 8, 8]]


piecePositionScores = {'N': knightScores, 'Q': queenScores, 'B': bishopScores, 'R': rookScores, \
                        'wp': whitePawnScores, 'bp': blackPawnScores}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3

class AI():

    def findRandomMove(validMoves):
        return validMoves[random.randint(0, len(validMoves) - 1)]
      
    # find best move min max, without recursion
    def findBestMoveMinMaxNoRecursion(game_state, validMoves):
        turnColor = 1 if game_state.whiteToMove else -1
        opponentMinMaxScore = CHECKMATE 
        bestPlayerMove = None
        random.shuffle(validMoves)
        for playerMove in validMoves:
            game_state.make_move(playerMove)
            opponentMoves = game_state.get_valid_moves()
            if game_state.stalemate:
                opponentMaxScore = STALEMATE
            elif game_state.checkmate:
                opponentMaxScore = -CHECKMATE
            else: 
                opponentMaxScore = -CHECKMATE
                for opponentMove in opponentMoves:
                    game_state.make_move(opponentMove)
                    game_state.get_valid_moves()
                    if game_state.checkmate:
                        score = CHECKMATE 
                    elif game_state.stalemate:
                        score = STALEMATE
                    else: 
                        score = -turnColor * scoreMaterial(game_state.board)
                    if score > opponentMaxScore:
                        opponentMaxScore = score
                    game_state.undo_move()
            if opponentMaxScore < opponentMinMaxScore:
                opponentMinMaxScore = opponentMaxScore
                bestPlayerMove = playerMove
            game_state.undo_move()
        return bestPlayerMove
    
    """ Helper method to make first recursive call """
    def findBestMove(game_state, validMoves, returnQueue):
        global nextMove, counter
        nextMove = None
        counter = 0
        # findMoveMinMax(game_state, validMoves, DEPTH, game_state.whiteToMove)
        # findMoveNegaMax(game_state, validMoves, DEPTH, 1 if game_state.whiteToMove else -1)
        findMoveNegaMaxAlphaBeta(game_state, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if game_state.whiteToMove else -1)
        print(counter)
        returnQueue.put(nextMove)
    
def findMoveMinMax(game_state, validMoves, depth, whiteToMove):
    global nextMove 
    if depth ==0:
        return scoreMaterial(game_state.board)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            game_state.make_move(move)
            nextMoves = game_state.get_valid_moves()
            score = findMoveMinMax(game_state, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMoves = move
            game_state.undo_move()
        return maxScore
    else: 
        minScore = CHECKMATE
        for move in validMoves:
            game_state.make_move(move)
            nextMoves = game_state.get_valid_moves()
            score = findMoveMinMax(game_state, nextMoves, depth - 1, True)
            if score < minScore: 
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            game_state.undo_move()
        return minScore

def findMoveNegaMax(game_state, validMoves, depth, turnColor):
    global nextMove, counter
    counter += 1
    if depth ==0:
        return turnColor * scoreBoard(game_state)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        game_state.make_move(move)
        nextMoves = game_state.get_valid_moves()
        score = -findMoveNegaMax(game_state, nextMoves, depth - 1, -turnColor)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        game_state.undo_move()
    return maxScore

def findMoveNegaMaxAlphaBeta(game_state, validMoves, depth, alpha, beta, turnColor):
    global nextMove, counter
    counter += 1
    if depth ==0:
        return turnColor * scoreBoard(game_state)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        game_state.make_move(move)
        nextMoves = game_state.get_valid_moves()
        score = -findMoveNegaMaxAlphaBeta(game_state, nextMoves, depth - 1, -beta, -alpha, -turnColor)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        game_state.undo_move()
        if maxScore > alpha: # pruning happens
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore
        
""" 
A positive score is good for white 
A negative score is good for black
"""
def scoreBoard(game_state):
    if game_state.checkmate:
        if game_state.whiteToMove:
            return -CHECKMATE # blacks wins
        else: 
            return CHECKMATE # white wins
    elif game_state.stalemate:
        return STALEMATE
    
    score = 0
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            square = game_state.board[row][col]
            piecePositionScore = 0
            if square != "--":
                # score it positionally
                if square[1] != 'K': # no position table for king
                    if square[1] == 'p':
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]

                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * .1
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * .1
            
    return score
    
""" Score the board on material """
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
            
    return score