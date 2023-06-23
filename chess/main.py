import pygame as p 
from game import *
from ai import *
from multiprocessing import Process, Queue


BOARD_WIDTH = 648
BOARD_HEIGHT = 648
DIMENSION = 8 # dimension board 8*8
SQSIZE = BOARD_HEIGHT // DIMENSION
MOVE_LOG_PANEL_WIDTH = 220 # dimension log panel
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
MAX_FPS = 15 # for animation
IMAGES = {}

def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ',]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("chess/assets/" + piece + ".png"), (SQSIZE, SQSIZE))

""" 
User input & update the board : 
"""
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 21, False, False)
    game_state = GameState()
    validMoves = game_state.get_valid_moves()
    moveMade = False # flag var when move is made
    animate = False # flag var when should animate move
    load_images() # Only once, before the wile loop
    running = True
    sqSelected = () # square select & keep track last click
    playerClicks = [] # all clicks player
    gameOver = False
    playerOne = True # If human playing white then will be True
    playerTwo = False # Same as above but for black
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    while running:
        humanTurn = (game_state.whiteToMove and playerOne) or (not game_state.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # Mouse Use
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # (x,y) location of mouse
                    row = location[1] // SQSIZE
                    col = location[0] // SQSIZE
                    if sqSelected == (row, col) or col >= 8: # user click same square twice (= undo action) or click log panel
                        sqSelected = () # deselect
                        playerClicks = [] # clear player clicks
                    else:   
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2 and humanTurn:
                        move = Move(playerClicks[0], playerClicks[1], game_state.board)
                        print(move.get_chess_notation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                game_state.make_move(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () # reset user clicks
                                playerClicks = [] 
                        if not moveMade: 
                            playerClicks = [sqSelected]
             
            # Keys Use
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    # undo press Z
                    game_state.undo_move()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                    
                if e.key == p.K_r:
                    # restart press R
                    game_state = GameState()
                    game_state.whiteToMove = True 
                    validMoves = game_state.get_valid_moves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                    
        # AI Move
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("AI thinking...")
                returnQueue = Queue() # use to pass data between threads
                moveFinderProcess = Process(target=AI.findBestMove, args=(game_state,validMoves, returnQueue))
                moveFinderProcess.start() # call findBestMove(game_state,validMoves, returnQueue)
                
            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = AI.findRandomMove(validMoves)
                game_state.make_move(AIMove)
                moveMade = True
                animate = True
                AIThinking = False
                   
        if moveMade:
            if animate:  
                animateMove(game_state.moveLog[-1], screen, game_state.board, clock)
            validMoves = game_state.get_valid_moves()
            moveMade = False
            animate = False
            moveUndone = False
            
        draw_game_state(screen, game_state, validMoves, sqSelected, moveLogFont)
        
        # GameOver Text
        if game_state.checkmate or game_state.stalemate:
            gameOver = True
            text = 'Stalemate' if game_state.stalemate else 'Black wins by checkmate' if game_state.whiteToMove \
                    else 'White wins by checkmate'
            drawEndGameText(screen, text)
            
        clock.tick(MAX_FPS)
        p.display.flip()
 
         
""" 
Graphic Part : 
"""

def draw_game_state(screen, game_state, validMoves, sqSelected, moveLogFont):
    draw_board(screen) # draw squares on board
    highlightSquares(screen, game_state, validMoves, sqSelected)
    draw_pieces(screen, game_state.board) # draw pieces on board
    drawMoveLog(screen, game_state, moveLogFont)
    
def draw_board(screen):
    global colors
    colors = [p.Color("light grey"), p.Color("dim grey")] # Color of board
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)] 
            p.draw.rect(screen, color, p.Rect(c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE)) # Draw
    
""" Highlight square selected and moves for piece """
def highlightSquares(screen, game_state, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        # sqSelected is a piece that can be moved
        if game_state.board[r][c][0] == ('w' if game_state.whiteToMove else 'b'):
            s = p.Surface((SQSIZE, SQSIZE))
            s.set_alpha(100) # transperancy value
            s.fill(p.Color('blue')) # choice color
            screen.blit(s, (c * SQSIZE, r * SQSIZE))
            # highlight move from that square
            s.fill(p.Color('green')) # choice color
            for move in validMoves:
                if move.initialRow == r and move.initialCol == c: 
                    screen.blit(s, (move.finalCol * SQSIZE, move.finalRow * SQSIZE))
                    
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # not an empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE))
                
def drawMoveLog(screen, game_state, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), moveLogRect)
    moveLog = game_state.moveLog 
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveStr = str(i//2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog): # make sure black made a move
            moveStr += str(moveLog[i+1]) + "    "
        moveTexts.append(moveStr)
    movesPerRow = 2
    padding = 5
    textY = padding
    lineSpacingY = 4
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('white'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacingY
        
""" Animating a move """ 
def animateMove(move, screen, board, clock):
    global colors
    dR = move.finalRow - move.initialRow
    dC = move.finalCol - move.initialCol
    framesPerSquare = 5 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.initialRow + dR * frame / frameCount, move.initialCol + dC * frame / frameCount)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase piece moved from ending square
        color = colors[(move.finalRow + move.finalCol) % 2]
        finalSquare = p.Rect(move.finalCol * SQSIZE, move.finalRow * SQSIZE, SQSIZE, SQSIZE)
        p.draw.rect(screen, color, finalSquare)
        # draw captured piece
        if move.pieceCaptured != "--":
            if move.enPassant:
                enPassantRow = move.finalRow + 1 if move.pieceCaptured[0] == 'b' else move.finalRow - 1
                finalSquare = p.Rect(move.finalCol * SQSIZE, enPassantRow * SQSIZE, SQSIZE, SQSIZE)
            screen.blit(IMAGES[move.pieceCaptured], finalSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE))
        p.display.flip()
        clock.tick(80) # frame per second
        
def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 55, True, False)
    textObject = font.render(text, 0, p.Color('black'))
    # center text
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 5, p.Color("green"))
    screen.blit(textObject, textLocation.move(3, 2))
        
if __name__ == "__main__":
    main()