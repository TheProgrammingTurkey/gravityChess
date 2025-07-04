import pygame
from enum import Enum
import time
import copy

#set up an enum for the state of squares
class SquareState(Enum):
    INVALID = -1
    EMPTY = 0
    LIGHT = 1
    DARK = 2

#set up an enum for the type of a piece
class PieceType(Enum):
    PAWN = "Pawn"
    KNIGHT = "Knight"
    BISHOP = "Bishop"
    ROOK = "Rook"
    QUEEN = "Queen"
    KING = "King"

#set up an enum for the ways a game can end
class EndType(Enum):
    PLAYING = "Still Playing"
    CHECKMATE = "Checkmate"
    STALEMATE = "Stalemate"
    INSUFFICIENT = "Insufficient Material"

#set up a class for pieces
class Piece:
    #constructor
    def __init__(self, isWhite, type):
        self.isWhite = isWhite
        self.type = type
        self.justMoved2 = False
        self.hasMoved = False
    #allows easier printing of the pieces
    def __str__(self):
        return f"{self.isWhite} {self.type.value}"
    #allows for better direct comparisons of pieces
    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.type == other.type and self.isWhite == other.isWhite
        return False
    
#initialize the board with pieces
board =[
    [Piece(True, PieceType.ROOK), Piece(True, PieceType.PAWN), None, None, None, None, Piece(False, PieceType.PAWN), Piece(False, PieceType.ROOK)], 
    [Piece(True, PieceType.KNIGHT), Piece(True, PieceType.PAWN), None, None, None, None, Piece(False, PieceType.PAWN), Piece(False, PieceType.KNIGHT)], 
    [Piece(True, PieceType.BISHOP), Piece(True, PieceType.PAWN), None, None, None, None, Piece(False, PieceType.PAWN), Piece(False, PieceType.BISHOP)], 
    [Piece(True, PieceType.QUEEN), Piece(True, PieceType.PAWN), None, None, None, None, Piece(False, PieceType.PAWN), Piece(False, PieceType.QUEEN)], 
    [Piece(True, PieceType.KING), Piece(True, PieceType.PAWN), None, None, None, None, Piece(False, PieceType.PAWN), Piece(False, PieceType.KING)], 
    [Piece(True, PieceType.BISHOP), Piece(True, PieceType.PAWN), None, None, None, None, Piece(False, PieceType.PAWN), Piece(False, PieceType.BISHOP)], 
    [Piece(True, PieceType.KNIGHT), Piece(True, PieceType.PAWN), None, None, None, None, Piece(False, PieceType.PAWN), Piece(False, PieceType.KNIGHT)], 
    [Piece(True, PieceType.ROOK), Piece(True, PieceType.PAWN), None, None, None, None, Piece(False, PieceType.PAWN), Piece(False, PieceType.ROOK)]
    ]

#initialize the array with the moveable platforms
#0 means no platform, 
#1 means it can be moved or removed, 
#>2 means it's locked, 
#<0 means none can be placed
platforms = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    ]

#set up the the icons for the pieces
lightPawnIcon = pygame.image.load("assets/lightPawn.png")
lightRookIcon = pygame.image.load("assets/lightRook.png")
lightKnightIcon = pygame.image.load("assets/lightKnight.png")
lightBishopIcon = pygame.image.load("assets/lightBishop.png")
lightQueenIcon = pygame.image.load("assets/lightQueen.png")
lightKingIcon = pygame.image.load("assets/lightKing.png")
darkPawnIcon = pygame.image.load("assets/darkPawn.png")
darkRookIcon = pygame.image.load("assets/darkRook.png")
darkKnightIcon = pygame.image.load("assets/darkKnight.png")
darkBishopIcon = pygame.image.load("assets/darkBishop.png")
darkQueenIcon = pygame.image.load("assets/darkQueen.png")
darkKingIcon = pygame.image.load("assets/darkKing.png")
lockIcon = pygame.image.load("assets/lock.png")
lockIcon = pygame.transform.rotozoom(lockIcon, 0, .01)

#set up a dictionary to map the piece abbreviations to their icons
pieceIcons = {
    "True Rook": lightRookIcon,
    "True Pawn": lightPawnIcon,
    "True Knight": lightKnightIcon,
    "True Bishop": lightBishopIcon,
    "True Queen": lightQueenIcon,
    "True King": lightKingIcon,
    "False Rook": darkRookIcon,
    "False Pawn": darkPawnIcon,
    "False Knight": darkKnightIcon,
    "False Bishop": darkBishopIcon,
    "False Queen": darkQueenIcon,
    "False King": darkKingIcon
}

#finds the row and col of the square the user clicked
def locatePressedSquare(mousePos):
    global platformHovering
    platformHovering = (((mousePos[1]-gameY)/cellSize)%1 < platformHeight/cellSize or ((mousePos[1]-gameY)/cellSize)%1 > 1-platformHeight/cellSize) and (mousePos[1]-gameY)/cellSize > .5 and (mousePos[1]-gameY)/cellSize < 7.5
    if platformHovering:
        row = round((mousePos[1] - gameY) / cellSize)-1
        col = (mousePos[0] - gameX) // cellSize
        if row > 6 or row < 0 or col > 7 or col < 0:
            row = -1
            col = -1
    else:
        row = (mousePos[1] - gameY) // cellSize
        col = (mousePos[0] - gameX) // cellSize
    return [row, col]

#determines whether the game is over
def checkEnding():
    global board, platforms, isWhiteTurn
    hasMove = False
    pawnHasMove = False
    for row in range(len(board)):
        for col in range(len(board[row])):
            #if no piece can move --> stalemate or checkmate
            if not hasMove and getSquareState(board, row, col) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK) and len(getValidMoves(board, row, col, isWhiteTurn, True)) > 0:
                hasMove = True
            #if a pawn can move --> still life in the position
            if not pawnHasMove and getPiece(board, row, col) == Piece(True, PieceType.PAWN) and (len(getValidMoves(board, row, col, True, True)) > 0 or col == 7):
                pawnHasMove = True
            elif not pawnHasMove and getPiece(board, row, col) == Piece(False, PieceType.PAWN) and (len(getValidMoves(board, row, col, False, True)) > 0 or col == 0):
                pawnHasMove = True
            #if a pawn is not on the bottom --> still life in the position
            elif not pawnHasMove and row < 7 and (getPiece(board, row, col) == Piece(False, PieceType.PAWN) or getPiece(board, row, col) == Piece(True, PieceType.PAWN)):
                pawnHasMove = True
    #Checkmate vs Stalemate
    if not hasMove:
        if not isCheck(board, True) and not isCheck(board, False):
            return EndType.STALEMATE
        elif isWhiteTurn:
            return EndType.CHECKMATE       
        else:
            return EndType.CHECKMATE
    #If any rook, queen, bishop, or more than 2 knights are on a team, checkmate is possible
    if amtOfType(PieceType.ROOK) > 0 or amtOfType(PieceType.QUEEN) > 0 or amtOfType(PieceType.BISHOP) > 0 or amtOfPiece(Piece(True, PieceType.KNIGHT)) > 2 or amtOfPiece(Piece(False, PieceType.KNIGHT)) > 2:
        return EndType.PLAYING
    #If a pawn can move then play on
    if pawnHasMove:
        return EndType.PLAYING
    #If no queens, rooks, bishops
    if amtOfType(PieceType.ROOK) == 0 and amtOfType(PieceType.QUEEN) == 0 and amtOfType(PieceType.BISHOP) == 0:
        #if no knights and pawns cant move --> insufficient material
        if amtOfType(PieceType.KNIGHT) == 0 and not pawnHasMove:
            return EndType.INSUFFICIENT
        #if no pawns and not enough knights --> Insufficient material
        if amtOfPiece(Piece(True, PieceType.PAWN)) == 0 and amtOfPiece(Piece(True, PieceType.KNIGHT)) <= 2 and amtOfPiece(Piece(False, PieceType.PAWN)) == 0 and amtOfPiece(Piece(False, PieceType.KNIGHT)) <= 2:
            return EndType.INSUFFICIENT
    return EndType.PLAYING
    
#checks to see if removing the platform would result in its own king in check
def checkPlatform(board, platforms, oldRow, oldCol, newRow, newCol):
    tempBoard = copy.deepcopy(board)
    tempPlatforms = copy.deepcopy(platforms)
    global isWhiteTurn
    tempPlatforms[oldRow][oldCol] = 0
    if newRow != -1:
        tempPlatforms[newRow][newCol] = 1
    if isCheck(gravity(tempBoard, tempPlatforms, False), isWhiteTurn):
        return False
    return True

#finds amt of pieces of a type
def amtOfType(type):
    total = 0
    for row in board:
        total += row.count(Piece(True, type))+row.count(Piece(False, type))
    return total

#finds amt of pieces of a piece
def amtOfPiece(piece):
    total = 0
    for row in board:
        total += row.count(piece)
    return total

#updates the board once a move has been made
def makeMove(board, isWhiteTurn, pieceFrom, pieceTo):
    global promotionPending, promotionSquare, pressedPos, validMoves, platforms, whiteJustPlatformed, blackJustPlatformed
    for row in range(len(board)):
        for col in range(len(board[row])):
            if getSquareState(board, row, col) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
                board[row][col].justMoved2 = False
    if getPiece(board, pieceFrom[0], pieceFrom[1]).type == PieceType.PAWN:
        #En Passant Stuff
        if abs(pieceTo[1]-pieceFrom[1]) == 2:
            board[pieceFrom[0]][pieceFrom[1]].justMoved2 = True
        if pieceFrom[0] != pieceTo[0] and pieceFrom[1] != pieceTo[1] and getSquareState(board, pieceTo[0], pieceFrom[1]) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT) and board[pieceTo[0]][pieceFrom[1]].justMoved2:
            board[pieceTo[0]][pieceFrom[1]] = None 
        #Pawn promotion stuff
        if pieceTo[1] == 0 or pieceTo[1] == 7:
            promotionPending = True
            promotionSquare = pieceTo
    #Castling
    if getPiece(board, pieceFrom[0], pieceFrom[1]).type == PieceType.KING:
        if abs(pieceTo[0]-pieceFrom[0]) > 1:
            if pieceTo[0] == 6:
                board[5][pieceFrom[1]] = board[7][pieceFrom[1]]
                board[7][pieceFrom[1]] = None
            else:
                board[3][pieceFrom[1]] = board[0][pieceFrom[1]]
                board[0][pieceFrom[1]] = None

    board[pieceTo[0]][pieceTo[1]] = board[pieceFrom[0]][pieceFrom[1]]
    board[pieceFrom[0]][pieceFrom[1]] = None
    board[pieceTo[0]][pieceTo[1]].hasMoved = True
    isWhiteTurn = not isWhiteTurn
    pressedPos = [-1, -1]
    validMoves = [-1, -1]
    board = gravity(board, platforms, True)
    platforms = setPlatforms(platforms)
    if not isWhiteTurn:
        whiteJustPlatformed = False
    else:
        blackJustPlatformed = False
    return board, isWhiteTurn

#runs the cooldowns on the platforms
def setPlatforms(platforms):
    for row in range(len(platforms)):
        for col in range(len(platforms[row])):
            if platforms[row][col] < 0:
                platforms[row][col]+=1
            elif platforms[row][col] > 1:
                platforms[row][col]-=1
    return platforms

#enact gravity on the board
def gravity(board, platforms, show):
    for stop in range(8):
        for row in reversed(range(stop+1, 8)):
            for col in range(len(board)):
                if getSquareState(board, row, col) == SquareState.EMPTY and platforms[row-1][col] < 1:
                    board[row][col] = board[row-1][col]
                    board[row-1][col] = None
            if show:
                draw(board)
                time.sleep(.01)
    return board

#finds the state of a square
def getSquareState(board, row, col):
    if row < 0 or row > 7 or col < 0 or col > 7:
        return SquareState.INVALID
    if getPiece(board, row, col) == None:
        return SquareState.EMPTY
    if getPiece(board, row, col).isWhite == True:
        return SquareState.LIGHT
    return SquareState.DARK

#obtains the piece at a square
def getPiece(board, row, col):
    return board[row][col]

#finds all the valid moves from a given position
def getValidMoves(board, row, col, isWhiteTurn, checkingChecks):
    validMoves = []
    if getPiece(board, row, col).type == PieceType.PAWN:
        validMoves = pawnMovement(board, row, col, isWhiteTurn)
    elif getPiece(board, row, col).type == PieceType.ROOK:
        validMoves = rookMovement(board, row, col, isWhiteTurn)
    elif getPiece(board, row, col).type == PieceType.KNIGHT:
        validMoves = knightMovement(board, row, col, isWhiteTurn)
    elif getPiece(board, row, col).type == PieceType.BISHOP:
        validMoves = bishopMovement(board, row, col, isWhiteTurn)
    elif getPiece(board, row, col).type == PieceType.QUEEN:
        validMoves = queenMovement(board, row, col, isWhiteTurn)
    elif getPiece(board, row, col).type == PieceType.KING:
        validMoves = kingMovement(board, row, col, isWhiteTurn)
    else:
        return False
    if checkingChecks:
        safeMoves = []
        for move in validMoves:
            tempBoard = copy.deepcopy(board)
            tempBoard[move[0]][move[1]] = tempBoard[row][col]
            tempBoard[row][col] = None
            tempBoard = gravity(tempBoard, platforms, False)
            if not isCheck(tempBoard, isWhiteTurn):
                safeMoves.append(move)
        return safeMoves
    return validMoves

#finds valid moves for pawns
def pawnMovement(board, row, col, isWhiteTurn):
    possibleMoves = []
    playerCoef = 0
    if isWhiteTurn:
        playerCoef = 1
        if col == 1 and getSquareState(board, row, 3) == SquareState.EMPTY and getSquareState(board, row, 2) == SquareState.EMPTY:
            possibleMoves.append([row, 3])
    else:
        playerCoef = -1
        if col == 6 and getSquareState(board, row, 4) == SquareState.EMPTY and getSquareState(board, row, 5) == SquareState.EMPTY:
            possibleMoves.append([row, 4])
    #En Passant
    if getSquareState(board, row+1, col) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT) and board[row+1][col].justMoved2:
        possibleMoves.append([row+1, col+playerCoef])
    if getSquareState(board, row-1, col) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT) and board[row-1][col].justMoved2:
        possibleMoves.append([row-1, col+playerCoef])
    #Move Forward
    if getSquareState(board, row, col+playerCoef) == SquareState.EMPTY:
        possibleMoves.append([row, col+playerCoef])
    #Attacking
    if getSquareState(board, row-1, col+playerCoef) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
        possibleMoves.append([row-1, col+playerCoef])
    if getSquareState(board, row+1, col+playerCoef) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
        possibleMoves.append([row+1, col+playerCoef])
    return possibleMoves

#finds valid moves for rooks
def rookMovement(board, row, col, isWhiteTurn):
    possibleMoves = []
    for r in range(row+1, 8):
        if getSquareState(board, r, col) == SquareState.EMPTY:
            possibleMoves.append([r, col])
        elif getSquareState(board, r, col) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([r, col])
            break
        elif getSquareState(board, r, col) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
            break
        else:
            break
    for c in range(col+1, 8):
        if getSquareState(board, row, c) == SquareState.EMPTY:
            possibleMoves.append([row, c])
        elif getSquareState(board, row, c) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([row, c])
            break
        elif getSquareState(board, row, c) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
            break
        else:
            break
    for r in reversed(range(0, row)):
        if getSquareState(board, r, col) == SquareState.EMPTY:
            possibleMoves.append([r, col])
        elif getSquareState(board, r, col) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([r, col])
            break
        elif getSquareState(board, r, col) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
            break
        else:
            break
    for c in reversed(range(0, col)):
        if getSquareState(board, row, c) == SquareState.EMPTY:
            possibleMoves.append([row, c])
        elif getSquareState(board, row, c) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([row, c])
            break
        elif getSquareState(board, row, c) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
            break
        else:
            break
    return possibleMoves

#finds valid moves for knights
def knightMovement(board, row, col, isWhiteTurn):
    possibleMoves = []
    moveShape = [[1,2], [2,1], [-1,2], [-2,1], [1,-2], [2,-1], [-1,-2], [-2,-1]]
    for move in moveShape:
        if getSquareState(board, row+move[0], col+move[1]) == SquareState.EMPTY or getSquareState(board, row+move[0], col+move[1]) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([row+move[0], col+move[1]])
    return possibleMoves

#finds valid moves for bishops
def bishopMovement(board, row, col, isWhiteTurn):
    possibleMoves = []
    for r, c in zip(range(row+1, 8), range(col+1, 8)):
        if getSquareState(board, r, c) == SquareState.EMPTY:
            possibleMoves.append([r, c])
        elif getSquareState(board, r, c) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([r, c])
            break
        elif getSquareState(board, r, c) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
            break
        else:
            break
    for r, c in zip(range(row+1, 8), range(col-1, -1, -1)):
        if getSquareState(board, r, c) == SquareState.EMPTY:
            possibleMoves.append([r, c])
        elif getSquareState(board, r, c) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([r, c])
            break
        elif getSquareState(board, r, c) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
            break
        else:
            break
    for r, c in zip(range(row-1, -1, -1), range(col+1, 8)):
        if getSquareState(board, r, c) == SquareState.EMPTY:
            possibleMoves.append([r, c])
        elif getSquareState(board, r, c) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([r, c])
            break
        elif getSquareState(board, r, c) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
            break
        else:
            break
    for r, c in zip(range(row-1, -1, -1), range(col-1, -1, -1)):
        if getSquareState(board, r, c) == SquareState.EMPTY:
            possibleMoves.append([r, c])
        elif getSquareState(board, r, c) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([r, c])
            break
        elif getSquareState(board, r, c) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
            break
        else:
            break
    return possibleMoves

#finds valid moves for queens
def queenMovement(board, row, col, isWhiteTurn):
    possibleMoves = []
    possibleMoves.extend(rookMovement(board, row, col, isWhiteTurn))
    possibleMoves.extend(bishopMovement(board, row, col, isWhiteTurn))
    return possibleMoves

#finds valid moves for kings
def kingMovement(board, row, col, isWhiteTurn):
    possibleMoves = []
    #Regular Movement
    moveShape = [[1,1], [-1,1], [0,1], [1,0], [1,-1], [-1,-1], [0,-1], [-1,0]]
    for move in moveShape:
        if getSquareState(board, row+move[0], col+move[1]) == SquareState.EMPTY or getSquareState(board, row+move[0], col+move[1]) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
            possibleMoves.append([row+move[0], col+move[1]])
    #castling
    if not board[row][col].hasMoved and isWhiteTurn:
        if getSquareState(board, 0, 0) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK) and not board[0][0].hasMoved and getSquareState(board, 1, 0) == SquareState.EMPTY and getSquareState(board, 2, 0) == SquareState.EMPTY and getSquareState(board, 3, 0) == SquareState.EMPTY:
            possibleMoves.append([2, 0])
        if getSquareState(board, 7, 0) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK) and not board[7][0].hasMoved and getSquareState(board, 6, 0) == SquareState.EMPTY and getSquareState(board, 5, 0) == SquareState.EMPTY:
            possibleMoves.append([6, 0])
    if not board[row][col].hasMoved and not isWhiteTurn:
        if getSquareState(board, 0, 7) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK) and not board[0][7].hasMoved and getSquareState(board, 1, 7) == SquareState.EMPTY and getSquareState(board, 2, 7) == SquareState.EMPTY and getSquareState(board, 3, 7) == SquareState.EMPTY:
            possibleMoves.append([2, 7])
        if getSquareState(board, 7, 7) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK) and not board[7][7].hasMoved and getSquareState(board, 6, 7) == SquareState.EMPTY and getSquareState(board, 5, 7) == SquareState.EMPTY:
            possibleMoves.append([6, 7])

        

    return possibleMoves

#finds the index of an item in a 2d array
def getIndexOf(array2d, item):
    for array1d in array2d:
        for arrayItem in array1d:
            if item == arrayItem:
                return [array2d.index(array1d), array1d.index(arrayItem)]
    return [-1, -1]

#finds whether the current players king is in check         
def isCheck(board, isWhiteTurn):
    r,c = getIndexOf(board, Piece(True if isWhiteTurn else False, PieceType.KING))
    for row in range(0, len(board)):
        for col in range(0, len(board[row])):
            if getSquareState(board, row, col) == (SquareState.DARK if isWhiteTurn else SquareState.LIGHT):
                if [r, c] in getValidMoves(board, row, col, not isWhiteTurn, False):
                    return True
    return False

#draw the board - the board goes from (460, 60) to (940, 540)
def draw(board):
    #outlining the board
    pygame.draw.lines(screen, "black", False, [(gameX+gameSize, gameY), (gameX+gameSize, gameY+gameSize), (gameX, gameY+gameSize)])
    for row in range(len(board)):
        for col in range(len(board[row])):
            #highlight yellow if hovering or clicking on square
            if ([row, col] == pressedPos and getSquareState(board, row, col) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK)) or (not platformHovering and [row, col] == hoveredPos):
                pygame.draw.rect(screen, "yellow", (gameX+col*cellSize, gameY+row*cellSize, cellSize, cellSize))
            #highlight blue for possible moves
            elif [row, col] in validMoves:
                pygame.draw.rect(screen, "blue", (gameX+col*cellSize, gameY+row*cellSize, cellSize, cellSize))
            #else make a checkerboard style
            elif row % 2 == 0:
                if col % 2 == 0:
                    pygame.draw.rect(screen, "white", (gameX+col*cellSize, gameY+row*cellSize, cellSize, cellSize))
                else:
                    pygame.draw.rect(screen, "gray", (gameX+col*cellSize, gameY+row*cellSize, cellSize, cellSize))
            else:
                if col % 2 == 0:
                    pygame.draw.rect(screen, "gray", (gameX+col*cellSize, gameY+row*cellSize, cellSize, cellSize))
                else:
                    pygame.draw.rect(screen, "white", (gameX+col*cellSize, gameY+row*cellSize, cellSize, cellSize))
    #highlight red if king is in check
    if isCheck(board, True):
        kingPos = getIndexOf(board, Piece(True, PieceType.KING))
        pygame.draw.rect(screen, "red", (gameX+kingPos[1]*cellSize, gameY+kingPos[0]*cellSize, cellSize, cellSize))
    if isCheck(board, False):
        kingPos = getIndexOf(board, Piece(False, PieceType.KING))
        pygame.draw.rect(screen, "red", (gameX+kingPos[1]*cellSize, gameY+kingPos[0]*cellSize, cellSize, cellSize))
    #outline the squares
    for row in range(len(board)):
        pygame.draw.line(screen, "black", (gameX, gameY+row*cellSize), (gameX+gameSize, gameY+row*cellSize))
        pygame.draw.line(screen, "black", (gameX+row*cellSize, cellSize), (gameX+row*cellSize, gameY+gameSize))
    #making thick lines for the platforms
    for row in range(len(platforms)):
        for col in range(len(platforms[row])):
            if platforms[row][col] > 0:
                if (platformHovering and platforms[row][col] == 1 and (hoveredPos[0] == row and hoveredPos[1] == col)) or (pressedPlatform[0] == row and pressedPlatform[1] == col): 
                    pygame.draw.line(screen, "yellow", (gameX+col*cellSize, gameY+(row+1)*cellSize), (gameX+(col+1)*cellSize, gameY+(row+1)*cellSize), platformHeight)
                else:
                    pygame.draw.line(screen, "black", (gameX+col*cellSize, gameY+(row+1)*cellSize), (gameX+(col+1)*cellSize, gameY+(row+1)*cellSize), platformHeight)
                if platforms[row][col] > 1:
                    screen.blit(lockIcon, (gameX+col*cellSize+cellSize/2-7, gameY+(row+1)*cellSize+cellSize/2-37))
            elif platforms[row][col] == 0 and platformHovering and (hoveredPos[0] == row and hoveredPos[1] == col) or (pressedPlatform[0] == row and pressedPlatform[1] == col):
                pygame.draw.line(screen, "yellow", (gameX+col*cellSize, gameY+(row+1)*cellSize), (gameX+(col+1)*cellSize, gameY+(row+1)*cellSize), platformHeight)
                
    #draw the piece icons
    for rowIndex, row in enumerate(board):
        for colIndex, cell in enumerate(row):
            if str(cell) in pieceIcons:
                screen.blit(pieceIcons[str(cell)], (gameX + colIndex * cellSize, gameY + rowIndex * cellSize))
    #Pick new piece for pawn promotion
    if promotionPending:
        pygame.draw.rect(screen, "white", (promotionX, promotionY, 2*promotionSize, 2*promotionSize))
        row, col = promotionSquare
        isWhite = board[row][col].isWhite if board[row][col] else isWhiteTurn
        iconKeys = [
            f"{isWhite} Queen",
            f"{isWhite} Rook",
            f"{isWhite} Bishop",
            f"{isWhite} Knight"
        ]
        for i, key in enumerate(iconKeys):
            cellCol = i % 2
            cellRow = i // 2
            cellX = promotionX + cellCol * promotionSize
            cellY = promotionY + cellRow * promotionSize
            # Highlight if hovered
            if promotionHovered == i:
                pygame.draw.rect(screen, "yellow", (cellX, cellY, promotionSize, promotionSize))
            icon = pieceIcons.get(key)
            pygame.draw.rect(screen, "black", (promotionX, promotionY, 2*promotionSize, 2*promotionSize), 1)
            screen.blit(icon, (cellX+(promotionSize-60)/2, cellY+(promotionSize-60)/2))
    #Checkmates and Stalemates
    if gameOver != EndType.PLAYING:
        font = pygame.font.SysFont(None, 36)
        if gameOver == EndType.STALEMATE:
            text = font.render("Draw - Stalemate", True, "black")
        elif gameOver == EndType.CHECKMATE and isWhiteTurn:
            text = font.render("Checkmate - Black Wins", True, "black")
        elif gameOver == EndType.CHECKMATE:
            text = font.render("Checkmate - White Wins", True, "black")
        elif gameOver == EndType.INSUFFICIENT:
            text = font.render("Draw - Insufficient Material", True, "black")
        screen.blit(text, (500, 20))
    #flip() the display to put your work on screen
    pygame.display.flip()

#random variables
pressedPos = [-1, -1]
hoveredPos = [-1, -1]
validMoves = []
isWhiteTurn = True
promotionPending = False
promotionSquare = None
promotionHovered = -1
gameX = 460
gameY = 60
gameSize = 480
cellSize = gameSize // 8
promotionX = 620
promotionY = 220
promotionSize = 80
platformHeight = 6
platformHovering = False
pressedPlatform = [-1, -1]
gameOver = EndType.PLAYING
amtPlatforms = 0
maxPlatforms = 4
whiteJustPlatformed = False
blackJustPlatformed = False
platformCooldown = 7

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1000, 600))
running = True


while running:
    #fill the screen with a color to wipe away anything from last frame
    screen.fill("beige")
    #poll for events
    events = pygame.event.get()
    if gameOver == EndType.PLAYING:
        gameOver = checkEnding()
    if gameOver != EndType.PLAYING:
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        draw(board)
        continue
    for event in events:
        #pygame.QUIT event means the user clicked X to close your window
        if event.type == pygame.QUIT:
            running = False
        #pawn promotion handling
        if promotionPending:
            #find what piece user is hovering during promotion
            mx, my = pygame.mouse.get_pos()
            if promotionX <= mx <= promotionX+2*promotionSize and promotionY <= my <= promotionY+2*promotionSize:
                col = (mx - promotionX) // promotionSize
                row = (my - promotionY) // promotionSize
                if 0 <= col < 2 and 0 <= row < 2:
                    promotionHovered = row * 2 + col
            #find what piece user is clicking during promotion
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if promotionX <= x <= promotionX+2*promotionSize and promotionY <= y <= promotionY+2*promotionSize:
                    col = (x - promotionX) // promotionSize
                    row = (y - promotionY) // promotionSize
                    option = row * 2 + col
                    if 0 <= option < 4:
                        pieceType = [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT][option]
                        board[promotionSquare[0]][promotionSquare[1]] = Piece(not isWhiteTurn, pieceType)
                        promotionPending = False
                        promotionSquare = None
        else:
            #find mouse position when hovering
            if event.type == pygame.MOUSEMOTION:
                hoveredPos = locatePressedSquare(event.pos)
                if platformHovering and amtPlatforms >= maxPlatforms and pressedPlatform == [-1, -1] and platforms[hoveredPos[0]][hoveredPos[1]] < 1:
                    hoveredPos = [-1, -1]
                elif platformHovering and (whiteJustPlatformed if isWhiteTurn else blackJustPlatformed):
                    hoveredPos = [-1, -1]
            #if mouse is over a platform
            if platformHovering:
                #find mouse position when clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #if no prior platform was selected, select the platform
                    if pressedPlatform == [-1, -1] and (amtPlatforms < maxPlatforms or platforms[locatePressedSquare(event.pos)[0]][locatePressedSquare(event.pos)[1]] > 0):
                        pressedPlatform = locatePressedSquare(event.pos)
                        if platforms[pressedPlatform[0]][pressedPlatform[1]] > 1 or platforms[pressedPlatform[0]][pressedPlatform[1]] < 0 or (whiteJustPlatformed if isWhiteTurn else blackJustPlatformed):
                            pressedPlatform = [-1, -1]
                            hoveredPos = [-1, -1]
                        pressedPos = [-1, -1]
                        validMoves = []
                    #if selected platform is a platform
                    elif platforms[pressedPlatform[0]][pressedPlatform[1]] == 1:
                        #move a platform to there
                        if hoveredPos != pressedPlatform and platforms[hoveredPos[0]][hoveredPos[1]] == 0 and checkPlatform(board, platforms, pressedPlatform[0], pressedPlatform[1], hoveredPos[0], hoveredPos[1]):
                            platforms[hoveredPos[0]][hoveredPos[1]] = platformCooldown
                            platforms[pressedPlatform[0]][pressedPlatform[1]] = -platformCooldown + 3
                            isWhiteTurn = not isWhiteTurn
                            if not isWhiteTurn:
                                whiteJustPlatformed = True
                            else:
                                blackJustPlatformed = True
                            pressedPlatform = [-1, -1]
                            validMoves = []
                            board = gravity(board, platforms, True)
                            platforms = setPlatforms(platforms)
                        #unselect a platform
                        elif hoveredPos != pressedPlatform and platforms[hoveredPos[0]][hoveredPos[1]] == 1:
                            pressedPlatform = locatePressedSquare(event.pos)
                        #remove a platform
                        elif hoveredPos == pressedPlatform and checkPlatform(board, platforms, pressedPlatform[0], pressedPlatform[1], -1, -1):
                            amtPlatforms-=1
                            platforms[hoveredPos[0]][hoveredPos[1]] = -platformCooldown + 3
                            isWhiteTurn = not isWhiteTurn
                            if not isWhiteTurn:
                                whiteJustPlatformed = True
                            else:
                                blackJustPlatformed = True
                            pressedPlatform = [-1, -1]
                            board = gravity(board, platforms, True)
                            validMoves = []
                            platforms = setPlatforms(platforms)
                    elif platforms[pressedPlatform[0]][pressedPlatform[1]] == 0 and amtPlatforms < maxPlatforms and not isCheck(board, isWhiteTurn): 
                        #add a platform
                        if hoveredPos == pressedPlatform:
                            amtPlatforms+=1
                            platforms[hoveredPos[0]][hoveredPos[1]] = platformCooldown
                            isWhiteTurn = not isWhiteTurn
                            if not isWhiteTurn:
                                whiteJustPlatformed = True
                            else:
                                blackJustPlatformed = True
                            pressedPlatform = [-1, -1]
                            validMoves = []
                            platforms = setPlatforms(platforms)
                        #select a different platform
                        elif hoveredPos != pressedPlatform and platforms[hoveredPos[0]][hoveredPos[1]] == 0:
                            pressedPlatform = locatePressedSquare(event.pos)
            #mouse is over a square
            else:
                #find mouse position when clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pressedPlatform = [-1, -1]
                    #if no prior piece was selected, select the piece
                    if pressedPos == [-1, -1]:
                        pressedPos = locatePressedSquare(event.pos)
                        #check to make sure the piece is the right color
                        if getSquareState(board, pressedPos[0], pressedPos[1]) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
                            validMoves = getValidMoves(board, pressedPos[0], pressedPos[1], isWhiteTurn, True)
                            #If there are no valid moves then dont select the piece
                            if validMoves == []:
                                pressedPos = [-1, -1]
                        else:
                            pressedPos = [-1, -1]
                    #check if mouse pos falls in a valid square
                    elif locatePressedSquare(event.pos) in validMoves:
                        board, isWhiteTurn = makeMove(board, isWhiteTurn, pressedPos, locatePressedSquare(event.pos))
                    #check if user is clicking a different piece to make a move
                    elif getSquareState(board, locatePressedSquare(event.pos)[0], locatePressedSquare(event.pos)[1]) == (SquareState.LIGHT if isWhiteTurn else SquareState.DARK):
                        pressedPos = locatePressedSquare(event.pos)
                        validMoves = getValidMoves(board, pressedPos[0], pressedPos[1], isWhiteTurn, True)
                        if validMoves == []:
                            pressedPos = [-1, -1]
    #drawing the board
    draw(board)

pygame.quit()