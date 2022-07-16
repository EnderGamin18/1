# Kyle Gerner 
# Started 3.18.21
# Connect 4 Solver, client facing 
import strategy
import os

YELLOW_COLOR = "\u001b[38;5;226m"  # yellow
RED_COLOR = '\033[91m'  # red
BLUE_COLOR = "\u001b[38;5;39m"  # blue
NO_COLOR = '\033[0m'  # white

EMPTY, RED, YELLOW = '.', 'o', '@'
gameBoard = [[EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],  # bottom row
             [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
             [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
             [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
             [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
             [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY]]  # top row
playerColor = YELLOW
ai = strategy.Strategy()


def printBoard(board):
    '''Prints the given game board'''
    print("\n  1 2 3 4 5 6 7")
    for rowNum in range(len(board) - 1, -1, -1):
        print(f"{BLUE_COLOR}|{NO_COLOR} ", end='')
        for spot in board[rowNum]:
            if spot == RED:
                pieceColor = RED_COLOR
            elif spot == YELLOW:
                pieceColor = YELLOW_COLOR
            else:
                pieceColor = NO_COLOR
            print(f"{pieceColor}%s{NO_COLOR} " % spot, end='')
        print(f"{BLUE_COLOR}|{NO_COLOR}")
    print(f"{BLUE_COLOR}%s{NO_COLOR}" % "-" * 17)


def getPlayerMove():
    '''Takes in the user's input and performs that move on the board'''
    col = input("It's your turn, which column would you like to play? (1-7):\t")
    while True:
        if not col.isdigit() or int(col.strip()) not in range(1, 8):
            col = input("Invalid input. Please enter a number 1 through 7:\t")
        elif not ai.isValidMove(gameBoard, int(col) - 1):
            col = input("That column is full, please choose another:\t")
        else:
            break
    ai.performMove(gameBoard, int(col) - 1, playerColor)
    ai.checkGameState(gameBoard)


def main():
    '''main method that prompts the user for input'''
    global playerColor
    os.system("")  # allows colored terminal to work on Windows OS
    print("\nWelcome to Kyle's Connect 4 AI!")
    playerColorInput = input(
        "Would you like to be RED ('r') or YELLOW ('y')? (red goes first!):\t").strip().lower()
    if playerColorInput == 'r':
        playerColor = RED
        print("You will be red!")
    elif playerColorInput == 'y':
        print("You will be yellow!")
    else:
        print("Invalid input. You'll be yellow!")
    print("You: %s\tAI: %s" % (playerColor, ai.opponentOf(playerColor)))
    ai.setPlayerColor(playerColor)
    turn = RED
    while not ai.GAME_OVER:
        printBoard(gameBoard)
        if turn == playerColor:
            getPlayerMove()
        else:
            ai_move = ai.playBestMove(gameBoard)
            print("\nAI played in spot %d" % (ai_move + 1))
        turn = ai.opponentOf(turn)  # switch the turn

    winner = "RED" if ai.opponentOf(turn) == RED else "YELLOW"
    printBoard(gameBoard)
    print("%s wins!" % winner)


if __name__ == "__main__":
    main()
