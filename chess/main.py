import pygame as p 
import sys
from game import *
from ai import *


BOARD_WIDTH = 648
BOARD_HEIGHT = 648
DIMENSION = 8 # dimension board 8*8
SQSIZE = BOARD_HEIGHT // DIMENSION
MOVE_LOG_PANEL_WIDTH = 220 # dimension log panel
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
MAX_FPS = 15 # for animation
IMAGES = {}

class Main():
    def __init__(self):
        p.init()
        self.menu_active = True  # Add variable for activate/deactivate the menu
        self.screen = p.display.set_mode((BOARD_WIDTH + 0, BOARD_HEIGHT))
        
    def show_menu(self):
        p.display.set_caption("ChessItium AI Game")
        game_state = GameState()
        board = game_state.board
        self.lastMove = None
        playerOne = True # If human playing white then will be True
        playerTwo = False # Same as above but for black
        # Load the chessboard background image
        background_image = p.image.load("chess/assets/chess_menu_game.png").convert()

        # Define colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GRAY = (200, 200, 200)

        # Define button properties
        BUTTON_WIDTH, BUTTON_HEIGHT = 180, 70
        BUTTON_X = BOARD_WIDTH // 2 - BUTTON_WIDTH // 2
        BLACK_BUTTON_Y = BOARD_HEIGHT // 2 - BUTTON_HEIGHT // 2
        WHITE_BUTTON_Y = BOARD_HEIGHT // 2 + BUTTON_HEIGHT // 2 + 10
        BUTTON_SPACING = 20

        # Create font object
        font = p.font.Font("./chess/assets/Merriweather-Bold.ttf", 40)

        while self.menu_active:
            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()

            # Blit the background image onto the screen
            self.screen.blit(background_image, (0, 0))

            # Calculer les positions verticales des boutons
            first_button_y = (BOARD_HEIGHT - (BUTTON_HEIGHT * 4 + BUTTON_SPACING * 3)) // 2
            black_button_y = first_button_y
            white_button_y = black_button_y + BUTTON_HEIGHT + BUTTON_SPACING
            button_pvp_y = white_button_y + BUTTON_HEIGHT + BUTTON_SPACING

            # Dessiner les boutons
            black_button = p.draw.rect(self.screen, BLACK, (BUTTON_X, black_button_y, BUTTON_WIDTH, BUTTON_HEIGHT))
            white_button = p.draw.rect(self.screen, WHITE, (BUTTON_X, white_button_y, BUTTON_WIDTH, BUTTON_HEIGHT))
            button_pvp = p.draw.rect(self.screen, p.Color('gray'), (BUTTON_X, button_pvp_y, BUTTON_WIDTH, BUTTON_HEIGHT))

            # Dessiner les libellés des boutons
            black_text = font.render("AI", True, WHITE)
            black_text_rect = black_text.get_rect(center=(BUTTON_X + BUTTON_WIDTH // 2, black_button_y + BUTTON_HEIGHT // 2))
            self.screen.blit(black_text, black_text_rect)

            white_text = font.render("AI", True, BLACK)
            white_text_rect = white_text.get_rect(center=(BUTTON_X + BUTTON_WIDTH // 2, white_button_y + BUTTON_HEIGHT // 2))
            self.screen.blit(white_text, white_text_rect)

            black_text_pvp = font.render("PVP", True, p.Color('dim gray'))
            black_text_rect_pvp = black_text_pvp.get_rect(center=(BUTTON_X + BUTTON_WIDTH // 2, button_pvp_y + BUTTON_HEIGHT // 2))
            self.screen.blit(black_text_pvp, black_text_rect_pvp)

            # Draw the title
            title_text_shadow = font.render("Play PVP or with an AI", True, BLACK)
            title_text = font.render("Play PVP or with an AI", True, WHITE)
            title_text_rect = title_text.get_rect(center=(BOARD_WIDTH // 2, 50))
            title_text_shadow_rect = title_text_shadow.get_rect(center=(BOARD_WIDTH // 2 + 2, 52))
            self.screen.blit(title_text_shadow, title_text_shadow_rect)
            self.screen.blit(title_text, title_text_rect)

            # Check if buttons are clicked
            mouse_pos = p.mouse.get_pos()
            if black_button.collidepoint(mouse_pos):
                if p.mouse.get_pressed()[0]:
                    # Black button clicked
                    # start the game black (reverse the board)
                    # playerOne : False & playerTwo : True
                    self.main_game(playerOne=False, playerTwo=True)
                    flip_board = game_state.flip_board(game_state.board)
                    print(flip_board)

            if white_button.collidepoint(mouse_pos):
                if p.mouse.get_pressed()[0]:
                    # White button clicked
                    # start the game
                    # playerOne : True & playerTwo : False
                    self.main_game(playerOne=True, playerTwo=False)
                    
            if button_pvp.collidepoint(mouse_pos):
                if p.mouse.get_pressed()[0]:
                    # Button PVP clicked
                    # start the game
                    # playerOne : True & playerTwo : True
                    self.main_game(playerOne=True, playerTwo=True)

            # Update the display
            p.display.flip()
    
    def load_images(self):
        pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ',]
        for piece in pieces:
            IMAGES[piece] = p.transform.scale(p.image.load("chess/assets/pieces/" + piece + ".png"), (SQSIZE, SQSIZE))

    """ 
    User input & update the board : 
    """
    def main_game(self, playerOne, playerTwo):
        self.menu_active = False
        self.screen.fill(p.Color("white"))
        self.screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
        self.load_images() # Only once, before the wile loop
        clock = p.time.Clock()
        moveLogFont = p.font.SysFont("Arial", 21, False, False)
        game_state = GameState()
        validMoves = game_state.get_valid_moves()
        moveMade = False # flag var when move is made
        animate = False # flag var when should animate move
        running = True
        sqSelected = () # square select & keep track last click
        playerClicks = [] # all clicks player
        gameOver = False
        moveUndone = False
        menu = self.show_menu()
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
                        moveUndone = False
                        self.lastMove = None
                        
                    if e.key == p.K_m:
                        # restart press M
                        self.menu_active = True
                        self.screen = p.display.set_mode((BOARD_WIDTH + 0, BOARD_HEIGHT))
                        return
                            
            # AI Move
            if not gameOver and not humanTurn and not moveUndone:
                AIMove = AI.findBestMove(game_state, validMoves)
                if AIMove is None:
                    AIMove = AI.findRandomMove(validMoves)
                game_state.make_move(AIMove)
                moveMade = True
                animate = True
                    
            if moveMade:
                if animate:  
                    self.animateMove(game_state.moveLog[-1], self.screen, game_state.board, clock)
                validMoves = game_state.get_valid_moves()
                moveMade = False
                animate = False
                moveUndone = False
                 # Set the last move to the latest move made
                self.lastMove = game_state.moveLog[-1] if game_state.moveLog else None
                
            self.draw_game_state(self.screen, game_state, validMoves, sqSelected, moveLogFont)
            
            # GameOver Text
            if game_state.checkmate or game_state.stalemate:
                gameOver = True
                text = 'Stalemate' if game_state.stalemate else 'Black wins by checkmate' if game_state.whiteToMove \
                        else 'White wins by checkmate'
                self.drawEndGameText(self.screen, text)
                
            clock.tick(MAX_FPS)
            p.display.flip()
    
            
    """ 
    Graphic Part : 
    """

    def draw_game_state(self, screen, game_state, validMoves, sqSelected, moveLogFont):
        self.draw_board(self.screen) # draw squares on board
        self.highlightSquares(screen, game_state, validMoves, sqSelected)
        self.draw_pieces(screen, game_state.board) # draw pieces on board
        self.drawMoveLog(screen, game_state, moveLogFont)
        
    def draw_board(self, screen):
        global colors
        colors = [p.Color("light grey"), p.Color("dim grey")] # Color of board
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                color = colors[((r+c) % 2)] 
                p.draw.rect(screen, color, p.Rect(c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE)) # Draw
        
    """ Highlight square selected and moves for piece """
    def highlightSquares(self, screen, game_state, validMoves, sqSelected):
        if sqSelected != ():
            r, c = sqSelected
            # sqSelected is a piece that can be moved
            if game_state.board[r][c][0] == ('w' if game_state.whiteToMove else 'b'):
                s = p.Surface((SQSIZE, SQSIZE))
                s.set_alpha(100)  # transparency value
                s.fill(p.Color('blue'))  # choice color
                self.screen.blit(s, (c * SQSIZE, r * SQSIZE))
                # highlight move from that square
                s.fill(p.Color('green'))  # choice color
                for move in validMoves:
                    if move.initialRow == r and move.initialCol == c:
                        self.screen.blit(s, (move.finalCol * SQSIZE, move.finalRow * SQSIZE))

        if self.lastMove is not None:  # Highlight the last move
            s = p.Surface((SQSIZE, SQSIZE))
            s.set_alpha(100)  # transparency value
            s.fill(p.Color('yellow'))  # choice color
            self.screen.blit(s, (self.lastMove.initialCol * SQSIZE, self.lastMove.initialRow * SQSIZE))
            self.screen.blit(s, (self.lastMove.finalCol * SQSIZE, self.lastMove.finalRow * SQSIZE))
                        
    def draw_pieces(self, screen, board):
        for r in range(DIMENSION):
            for c in range(DIMENSION):
                piece = board[r][c]
                if piece != "--": # not an empty square
                    screen.blit(IMAGES[piece], p.Rect(c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE))
                    
    def drawMoveLog(self, screen, game_state, font):
        moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
        p.draw.rect(self.screen, p.Color('black'), moveLogRect)
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
            self.screen.blit(textObject, textLocation)
            textY += textObject.get_height() + lineSpacingY
            
    """ Animating a move """ 
    def animateMove(self, move, screen, board, clock):
        global colors
        dR = move.finalRow - move.initialRow
        dC = move.finalCol - move.initialCol
        framesPerSquare = 5 # frames to move one square
        frameCount = (abs(dR) + abs(dC)) * framesPerSquare
        for frame in range(frameCount + 1):
            r, c = (move.initialRow + dR * frame / frameCount, move.initialCol + dC * frame / frameCount)
            self.draw_board(self.screen)
            self.draw_pieces(self.screen, board)
            # erase piece moved from ending square
            color = colors[(move.finalRow + move.finalCol) % 2]
            finalSquare = p.Rect(move.finalCol * SQSIZE, move.finalRow * SQSIZE, SQSIZE, SQSIZE)
            p.draw.rect(self.screen, color, finalSquare)
            # draw captured piece
            if move.pieceCaptured != "--":
                if move.enPassant:
                    enPassantRow = move.finalRow + 1 if move.pieceCaptured[0] == 'b' else move.finalRow - 1
                    finalSquare = p.Rect(move.finalCol * SQSIZE, enPassantRow * SQSIZE, SQSIZE, SQSIZE)
                self.screen.blit(IMAGES[move.pieceCaptured], finalSquare)
            # draw moving piece
            self.screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQSIZE, r * SQSIZE, SQSIZE, SQSIZE))
            p.display.flip()
            clock.tick(80) # frame per second
            
    def drawEndGameText(self, screen, text):
        font = p.font.SysFont("Helvitca", 55, True, False)
        textObject = font.render(text, 0, p.Color('black'))
        # center text
        textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
        self.screen.blit(textObject, textLocation)
        textObject = font.render(text, 5, p.Color("green"))
        self.screen.blit(textObject, textLocation.move(3, 2))
    
main = Main()
main.show_menu()