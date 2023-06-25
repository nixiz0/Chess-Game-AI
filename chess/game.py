
class GameState():
    def __init__(self):
        # Board 8 * 8
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 
                              'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        
        self.whiteToMove = True 
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enPassantPossible = ()
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
        
    def make_move(self, move):
        self.board[move.initialRow][move.initialCol] = "--"
        self.board[move.finalRow][move.finalCol] = move.pieceMoved
        self.moveLog.append(move) # log the move
        self.whiteToMove = not self.whiteToMove # swap players
        # updating king location
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.finalRow, move.finalCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.finalRow, move.finalCol)
            
        # pawn promotion
        if move.pawnPromotion:
            self.board[move.finalRow][move.finalCol] = move.pieceMoved[0] + 'Q'
            
        # en passant move
        if move.enPassant:
            # capturing the pawn
            self.board[move.initialRow][move.finalCol] = '--'
        # update enPassantPossible
        if move.pieceMoved[1] == 'p' and abs(move.initialRow - move.finalRow) == 2:
            self.enPassantPossible = ((move.initialRow + move.finalRow) // 2, move.initialCol)
        else: 
            self.enPassantPossible = ()
            
        # castle move
        if move.castleMove:
            # king side castle
            if move.finalCol - move.initialCol == 2:
                # moves the rook
                self.board[move.finalRow][move.finalCol - 1] = self.board[move.finalRow][move.finalCol + 1]
                self.board[move.finalRow][move.finalCol + 1] = "--"
            # queen side castle
            else: 
                # moves the rook
                self.board[move.finalRow][move.finalCol + 1] = self.board[move.finalRow][move.finalCol - 2]
                self.board[move.finalRow][move.finalCol - 2] = "--"
                
        self.enPassantPossibleLog.append(self.enPassantPossible)
            
        # update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
            
    def undo_move(self):
        if len(self.moveLog) != 0: # Verified if have a move to undo
            move = self.moveLog.pop()
            self.board[move.initialRow][move.initialCol] = move.pieceMoved
            self.board[move.finalRow][move.finalCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # switch turn back
            # updating king location
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.initialRow, move.initialCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.initialRow, move.initialCol)
            # undo en passant move
            if move.enPassant:
                self.board[move.finalRow][move.finalCol] = '--'
                self.board[move.initialRow][move.finalCol] = move.pieceCaptured

            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]
                
            # undo castling rights
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            # undo castle move
            if move.castleMove:
                # king side
                if move.finalCol - move.initialCol == 2:
                    self.board[move.finalRow][move.finalCol + 1] = self.board[move.finalRow][move.finalCol - 1]
                    self.board[move.finalRow][move.finalCol - 1] = "--"
                # queen side
                else: 
                    self.board[move.finalRow][move.finalCol - 2] = self.board[move.finalRow][move.finalCol + 1]
                    self.board[move.finalRow][move.finalCol + 1] = "--"
                    
            self.checkmate = False
            self.stalemate = False
                
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.initialRow == 7:
                if move.initialCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.initialCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.initialRow == 0:
                if move.initialCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.initialCol == 7:
                    self.currentCastlingRight.bks = False
                    
        # Check if a rook is captured
        if move.pieceCaptured == 'wR' and move.finalRow == 7:
            if move.finalCol == 0:
                self.currentCastlingRight.wqs = False
            elif move.finalCol == 7:
                self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR' and move.finalRow == 0:
            if move.finalCol == 0:
                self.currentCastlingRight.bqs = False
            elif move.finalCol == 7:
                self.currentCastlingRight.bks = False
                
    """ All moves considering checks """
    def get_valid_moves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else: 
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck: 
            # only 1 check
            if len(self.checks) == 1:
                moves = self.get_all_possible_moves()
                # check info
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                # enemy causing the check
                pieceChecking = self.board[checkRow][checkCol]
                # squares that pieces can move to
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else: 
                    for i in range(1, 8):
                        # check[2] & [3] are the check directions
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) -1, -1, -1): 
                    # move doesn't move king so must block or capture
                    if moves[i].pieceMoved[1] != 'K':
                        # move doesn't block check or capture piece
                        if not (moves[i].finalRow, moves[i].finalCol) in validSquares: 
                            moves.remove(moves[i])
            # double check, king has to move
            else: 
                self.getKingMoves(kingRow, kingCol, moves)
        # not in check so all moves are fine
        else: 
            moves = self.get_all_possible_moves()
            
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True 
        else: 
            self.checkmate = False
            self.stalemate = False 
            
        return moves

    """ All moves without considering checks """
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    # call the appropriate move function of piece type
                    self.moveFunctions[piece](r, c, moves)
        return moves
    
    """ All Piece Autorise Moves Function """
    def getPawnMoves(self, r, c, moves):
        piecePinned = False 
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c: 
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break 
        
        if self.whiteToMove:
            moveAmount = -1
            initialRow = 6
            backRow = 0
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else: 
            moveAmount = 1
            initialRow = 1
            backRow = 7
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation
        pawnPromotion = False
        
        if self.board[r + moveAmount][c] == '--':
            # 1 square move
            if not piecePinned or pinDirection == (moveAmount, 0):
                if r + moveAmount == backRow:
                    pawnPromotion = True 
                moves.append(Move((r, c), (r + moveAmount, c), self.board, pawnPromotion=pawnPromotion))
                # 2 squares move
                if r == initialRow and self.board[r + 2 * moveAmount][c] == '--':
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
        # capture left
        if c - 1 >= 0:
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    if r + moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, pawnPromotion=pawnPromotion))
                if (r + moveAmount, c - 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: # king is left of the pawn
                            insideRange = range(kingCol + 1, c - 1)
                            outsideRange = range(c + 1, 8)
                        else: # king right of the pawn
                            insideRange = range(kingCol - 1, c, -1)
                            outsideRange = range(c - 2, -1, -1)
                        for i in insideRange:
                            # some piece beside en passant pawn blocks
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant=True))
        # capture right
        if c + 1 <= 7:
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    if r + moveAmount == backRow:
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, pawnPromotion=pawnPromotion))
                if (r + moveAmount, c + 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == r:
                        if kingCol < c: # king is left of the pawn
                            insideRange = range(kingCol + 1, c)
                            outsideRange = range(c + 2, 8)
                        else: # king right of the pawn
                            insideRange = range(kingCol - 1, c + 1, -1)
                            outsideRange = range(c - 1, -1, -1)
                        for i in insideRange:
                            # some piece beside en passant pawn blocks
                            if self.board[r][i] != "--":
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[r][i]
                            if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant=True))

    def getRookMoves(self, r, c, moves):
        piecePinned = False 
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                # can't remove queen from pin on rook moves
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                finalRow = r + d[0] * i 
                finalCol = c + d[1] * i
                if 0 <= finalRow < 8 and 0 <= finalCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        finalPiece = self.board[finalRow][finalCol]
                        if finalPiece == "--": 
                            moves.append(Move((r, c), (finalRow, finalCol), self.board))
                        # enemy piece
                        elif finalPiece[0] == enemyColor:
                            moves.append(Move((r, c), (finalRow, finalCol), self.board))
                            break 
                        # friendly piece invalid action
                        else: 
                            break 
                # off board
                else: 
                    break
    
    def getKnightMoves(self, r, c, moves):
        piecePinned = False 
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        friendlyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            finalRow = r + m[0]
            finalCol = c + m[1]
            if 0 <= finalRow < 8 and 0 <= finalCol < 8:
                if not piecePinned:
                    finalPiece = self.board[finalRow][finalCol]
                    if finalPiece[0] != friendlyColor:
                        moves.append(Move((r, c), (finalRow, finalCol), self.board))

    def getBishopMoves(self, r, c, moves):
        piecePinned = False 
        pinDirection = ()
        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                finalRow = r + d[0] * i
                finalCol = c + d[1] * i
                if 0 <= finalRow < 8 and 0 <= finalCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        finalPiece = self.board[finalRow][finalCol]
                        if finalPiece == "--":
                            moves.append(Move((r, c), (finalRow, finalCol), self.board))
                        # enemy piece
                        elif finalPiece[0] == enemyColor: 
                            moves.append(Move((r, c), (finalRow, finalCol), self.board))
                            break 
                        # friendly piece
                        else: 
                            break 
                # off board
                else: 
                    break
    
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        friendlyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            finalRow = r + rowMoves[i]
            finalCol = c + colMoves[i]
            if 0 <= finalRow < 8 and 0 <= finalCol < 8:
                finalPiece = self.board[finalRow][finalCol]
                # not friendly (enemy or empty)
                if finalPiece[0] != friendlyColor:
                    # place king on en square and check for checks
                    if friendlyColor == "w":
                        self.whiteKingLocation = (finalRow, finalCol)
                    else: 
                        self.blackKingLocation = (finalRow, finalCol)
                    inCheck, pins, checks = self.check_for_pins_and_checks()
                    if not inCheck:
                        moves.append(Move((r, c), (finalRow, finalCol), self.board))
                    # place king back on original location
                    if friendlyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else: 
                        self.blackKingLocation = (r, c)
        self.getCastleMoves(r, c, moves, friendlyColor)
        
    """ Generate all valid move for king for castling """
    def getCastleMoves(self, r, c, moves, friendlyColor):
        inCheck = self.square_under_attack(r, c, friendlyColor)
        if inCheck:
            return # can't castle while in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves, friendlyColor)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves, friendlyColor)

    def getKingsideCastleMoves(self, r, c, moves, friendlyColor):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--' and \
            not self.square_under_attack(r, c+1, friendlyColor) and not self.square_under_attack(r, c+2, friendlyColor):
                moves.append(Move((r, c), (r, c+2), self.board, castleMove=True))
        
    def getQueensideCastleMoves(self, r, c, moves, friendlyColor):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--' and \
            not self.square_under_attack(r, c-1, friendlyColor) and not self.square_under_attack(r, c-2, friendlyColor):
                moves.append(Move((r, c), (r, c-2), self.board, castleMove=True))
    
    def square_under_attack(self, r, c, friendlyColor):
        enemyColor = 'w' if friendlyColor == 'b' else 'b'
        directions = ((-1, 0), (0, -1), (1, 0),(0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                finalRow = r + d[0] * i 
                finalCol = c + d[1] * i
                if 0 <= finalRow < 8 and 0 <= finalCol < 8 :
                    finalPiece = self.board[finalRow][finalCol]
                    # no attack from that direction
                    if finalPiece[0] == friendlyColor:
                        break
                    elif finalPiece[0] == enemyColor:
                        type = finalPiece[1]
                        if  (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type =='K'):
                            return True
                        # enemy piece not applying check
                        else: 
                            break 
                # off board
                else: 
                    break
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            finalRow = r + m[0]
            finalCol = c + m[1]
            if 0 <= finalRow < 8 and 0 <= finalCol < 8:
                finalPiece = self.board[finalRow][finalCol]
                # enemy knight attacking king
                if finalPiece[0] == enemyColor and finalPiece[1] == 'N':
                    return True
        return False
                    
    def check_for_pins_and_checks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            friendlyColor = "w"
            initialRow = self.whiteKingLocation[0]
            initialCol = self.whiteKingLocation[1]
        else: 
            enemyColor = "w"
            friendlyColor = "b"
            initialRow = self.blackKingLocation[0]
            initialCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            # reset possible pins
            possiblePin = () 
            for i in range(1, 8):
                finalRow = initialRow + d[0] * i 
                finalCol = initialCol + d[1] * i
                if 0 <= finalRow < 8 and 0 <= finalCol < 8:
                    finalPiece = self.board[finalRow][finalCol]
                    if finalPiece[0] == friendlyColor and finalPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (finalRow, finalCol, d[0], d[1])
                        else: 
                            break 
                    elif finalPiece[0] == enemyColor:
                        type = finalPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == 'K'):
                            # no piece blocking, so check
                            if possiblePin == ():
                                inCheck = True 
                                checks.append((finalRow, finalCol, d[0], d[1]))
                                break 
                            # piece blocking so pin
                            else: 
                                pins.append(possiblePin)
                                break
                        # enemy piece not applying check
                        else: 
                            break
                # off board
                else: 
                    break
                        
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            finalRow = initialRow + m[0]
            finalCol = initialCol + m[1]
            if 0 <= finalRow < 8 and 0 <= finalCol < 8:
                finalPiece = self.board[finalRow][finalCol]
                # enemy Knight attacking king
                if finalPiece[0] == enemyColor and finalPiece[1] == 'N':
                    inCheck = True
                    checks.append((finalRow, finalCol, m[0], m[1]))
        return inCheck, pins, checks
        
class CastleRights():
    # white & black king side and queen side
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
        
class Move():
    # Maps keys to values
    ranksToRows = {"1":7, "2":6, "3":5, "4":4,
                   "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3,
                   "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    def __init__(self, initial, final, board, enPassant=False, pawnPromotion=False, castleMove=False):
        self.initialRow = initial[0]
        self.initialCol = initial[1]
        self.finalRow = final[0]
        self.finalCol = final[1]
        self.pieceMoved = board[self.initialRow][self.initialCol]
        self.pieceCaptured = board[self.finalRow][self.finalCol]
        # pawn promotion
        self.pawnPromotion = pawnPromotion
        # en passant
        self.enPassant = enPassant
        if self.enPassant:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # castle move
        self.castleMove = castleMove
        self.isCapture = self.pieceCaptured == '--'
        
        self.moveID = self.initialRow * 1000 + self.initialCol * 100 + self.finalRow * 10 + self.finalCol
        
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID 
        return False
        
    def get_chess_notation(self):
        return self.get_rank_file(self.initialRow, self.initialCol) + self.get_rank_file(self.finalRow, self.finalCol)
        
    def get_rank_file(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
    
    # overriding the str function
    def __str__(self):
        if self.castleMove:
            return "O-O" if self.finalCol == 6 else "O-O-O"
        
        finalSquare = self.get_rank_file(self.finalRow, self.finalCol)
        
        if self.pieceMoved[1] == 'p':
            if self.isCapture:
                return finalSquare
            
        moveStr = self.pieceMoved[1]
        if self.isCapture:
            moveStr += ''
        return moveStr + finalSquare
    