# Kyle Gerner
# Started 7.15.22
# Othello AI, client facing
import os
import sys
import time
from importlib import import_module

from strategy import OthelloStrategy, setAiMaxSearchDepth, setAiMaxValidMovesToEvaluate, copyOfBoard, BLACK, \
    WHITE, EMPTY, BOARD_DIMENSION, setBoardDimension, getValidMoves, opponentOf, playMove, currentScore, \
    checkGameOver, numberOfPieceOnBoard, pieceAt, hasValidMoves, isMoveValid, isMoveInRange
from Player import Player

# Escape sequences for terminal color output
GREEN_COLOR = '\033[92m'
RED_COLOR = '\033[91m'
BLUE_COLOR = '\033[38;5;39m'
ORANGE_COLOR = '\033[38;5;208m'
NO_COLOR = '\033[0m'
HIGHLIGHT = '\033[48;5;238m'

CURSOR_UP_ONE = '\033[1A'
ERASE_LINE = '\033[2K'

# Miscellaneous
COLUMN_LABELS = list(map(chr, range(65, 65 + BOARD_DIMENSION)))
AI_DUEL_MODE = False
BOARD_OUTLINE_HEIGHT = 4
SAVE_STATE_OUTPUT_HEIGHT = BOARD_DIMENSION + 6
ERASE_MODE_ON = True
CONFIG_FILENAME = "config.json"
ERROR_SYMBOL = f"{RED_COLOR}<!>{NO_COLOR}"
INFO_SYMBOL = f"{BLUE_COLOR}<!>{NO_COLOR}"

# class for the Human player
class HumanPlayer(Player):

    def __init__(self, color):
        super().__init__(color, isAI=False)

    def getMove(self, board):
        """Takes in the user's input and returns the move"""
        pass

class GameRunner:
    """Handles overall gameplay"""

    def __init__(self, UserPlayerClass, OpponentPlayerClass):
        self.userPiece = getPieceColorInput()
        self.opponentPiece = opponentOf(self.userPiece)
        self.userPlayerName = "Your AI" if AI_DUEL_MODE else "You"
        self.aiPlayerName = "My AI" if AI_DUEL_MODE else "AI"
        self.playerNames = {self.userPiece: self.userPlayerName, self.opponentPiece: self.userPlayerName}
        self.players = {
            self.opponentPiece: OpponentPlayerClass(self.opponentPiece),
            self.userPiece: UserPlayerClass(self.userPiece)
        }
        self.board = [[EMPTY for _ in range(BOARD_DIMENSION)] for __ in range(BOARD_DIMENSION)]
        self.board[BOARD_DIMENSION // 2][BOARD_DIMENSION // 2 - 1] = WHITE
        self.board[BOARD_DIMENSION // 2 - 1][BOARD_DIMENSION // 2] = WHITE
        self.board[BOARD_DIMENSION // 2][BOARD_DIMENSION // 2] = BLACK
        self.board[BOARD_DIMENSION // 2 - 1][BOARD_DIMENSION // 2 - 1] = BLACK
        self.ai = OthelloStrategy(self.opponentPiece)
        self.overrideTurn = BLACK
        self.boardHistory = [[[], copyOfBoard(self.board)]] # [0]: highlighted coordinates  [1]: game board
        self.linesWrittenToConsole = 0
        # paste board save state here

    def endGame(self, winner=None):
        """Ends the game"""
        textColor = self.textColorOf(winner)
        colorName = nameOfPieceColor(winner)
        if winner:
            print(f"\n{textColor}{colorName}{NO_COLOR} wins!")
        else:
            print("\nThe game ended in a draw!")
        print("\nThanks for playing!")
        exit(0)

    def getMove(self):
        """Gets a move input from the user"""
        coord = input("It's your turn, which spot would you like to play? (A1 - %s%d):\t" % (
            COLUMN_LABELS[-1], BOARD_DIMENSION)).strip().upper()
        self.linesWrittenToConsole = BOARD_DIMENSION + 6
        while True:
            if coord == 'Q':
                self.endGame()
            elif coord == 'S':
                erasePreviousLines(self.linesWrittenToConsole)
                self.printOutSaveState(self.userPiece)
                print("\nSave state for the current game has been printed.")
                coord = input("It's your turn, which spot would you like to play? (A1 - %s%d):\t" % (
                    COLUMN_LABELS[-1], BOARD_DIMENSION)).strip().upper()
                self.linesWrittenToConsole = SAVE_STATE_OUTPUT_HEIGHT + 3
            elif coord == 'QS' or coord == 'SQ':
                self.printOutSaveState(self.userPiece)
                self.endGame()
            elif coord == 'P':
                erasePreviousLines(self.linesWrittenToConsole)
                self.printBoard(getValidMoves(self.userPiece, self.board))
                print("Your available moves have been highlighted.")
                coord = input("It's your turn, which spot would you like to play? (A1 - %s%d):\t" % (
                    COLUMN_LABELS[-1], BOARD_DIMENSION)).strip().upper()
                self.linesWrittenToConsole = BOARD_DIMENSION + BOARD_OUTLINE_HEIGHT + 2
            elif coord == 'H':
                if len(self.boardHistory) < 2:
                    coord = input("No previous moves to see. Enter a valid move to play:   ").strip().upper()
                    self.linesWrittenToConsole += 1
                else:
                    numMovesPrevious = input(f"How many moves ago do you want to see? (1 to {len(self.boardHistory) - 1})  ").strip()
                    self.linesWrittenToConsole += 1
                    if numMovesPrevious.isdigit() and 1 <= int(numMovesPrevious) <= len(self.boardHistory):
                        erasePreviousLines(self.linesWrittenToConsole)
                        self.printMoveHistory(int(numMovesPrevious))
                        coord = input(f"{INFO_SYMBOL} You're back in play mode. Which spot would you like to play?   ").strip().upper()
                        self.linesWrittenToConsole = BOARD_DIMENSION + BOARD_OUTLINE_HEIGHT + 1
                    else:
                        coord = input(f"{ERROR_SYMBOL} Invalid input. Enter a valid move to play:   ").strip().upper()
            elif len(coord) in ([2] if BOARD_DIMENSION < 10 else [2, 3]) and coord[0] in COLUMN_LABELS and \
                    coord[1:].isdigit() and int(coord[1:]) in range(1, BOARD_DIMENSION + 1):
                row, col = int(coord[1]) - 1, COLUMN_LABELS.index(coord[0])
                if isMoveValid(self.userPiece, row, col, self.board):
                    return row, col
                elif isMoveInRange(row, col) and pieceAt(row, col, self.board) != EMPTY:
                    erasePreviousLines(1)
                    coord = input(
                        f"{ERROR_SYMBOL} That spot is already taken! Please choose a different spot:   ").strip().upper()
                else:
                    erasePreviousLines(self.linesWrittenToConsole)
                    self.printBoard(getValidMoves(self.userPiece, self.board))
                    coord = input(f"{ERROR_SYMBOL} Please choose one of the highlighted spaces:   ").strip().upper()
                    self.linesWrittenToConsole = BOARD_DIMENSION + BOARD_OUTLINE_HEIGHT + 1
            else:
                erasePreviousLines(1)
                coord = input(f"{ERROR_SYMBOL} Please enter a valid move (A1 - %s%d):   " % (
                    COLUMN_LABELS[-1], BOARD_DIMENSION)).strip().upper()

    def textColorOf(self, piece):
        """Gets the text color of the given piece, or an empty string if no piece given"""
        if piece == self.userPiece:
            return GREEN_COLOR
        elif piece == self.opponentPiece:
            return RED_COLOR
        else:
            return ""

    def start(self):
        """Starts the game and handles all basic gameplay functionality"""
        turn = self.overrideTurn
        if turn == self.userPiece:
            self.printBoard(getValidMoves(self.userPiece, self.board))
        else:
            self.printBoard()
        print()
        noValidMovesInARow = 0
        while True:
            self.linesWrittenToConsole = BOARD_DIMENSION + 5
            if hasValidMoves(turn, self.board):
                noValidMovesInARow = 0
                if turn == self.userPiece:
                    row, col = self.getMove()
                    playMove(turn, row, col, self.board)
                    self.boardHistory.append([[row, col], copyOfBoard(self.board)])
                    erasePreviousLines(self.linesWrittenToConsole)
                    self.printBoard([[row, col]])
                    print("You played in spot %s%d." % (COLUMN_LABELS[col], row + 1))
                    self.linesWrittenToConsole += 1
                else:
                    userInput = input("Press enter for the AI to play.   ").strip().lower()
                    self.linesWrittenToConsole += 1
                    if userInput == 'q':
                        self.endGame()
                    elif userInput == 's':
                        self.printOutSaveState(turn)
                        input(
                            "\nSave state for the current game has been printed. Copy it, then press enter to continue. ")
                        self.linesWrittenToConsole += SAVE_STATE_OUTPUT_HEIGHT + 2
                    elif userInput == 'qs':
                        self.printOutSaveState(turn)
                        self.endGame()
                    elif userInput == 'p':
                        erasePreviousLines(self.linesWrittenToConsole)
                        self.printBoard(getValidMoves(turn, self.board))
                        input("AI's available moves have been highlighted. Press enter to continue.")
                        self.linesWrittenToConsole = BOARD_DIMENSION + BOARD_OUTLINE_HEIGHT + 1
                    startTime = time.time()
                    row, col = self.ai.getMove(self.board)
                    numBoardsEvaluated = self.ai.numBoardsEvaluated
                    endTime = time.time()
                    timeToPlayMove = round(endTime - startTime, 2)
                    playMove(turn, row, col, self.board)
                    self.boardHistory.append([[row, col], copyOfBoard(self.board)])
                    erasePreviousLines(self.linesWrittenToConsole)
                    self.printBoard([[row, col]] + getValidMoves(self.userPiece, self.board))
                    print("The AI played in spot %s%d  (%0.2f sec, %d possible futures)" % (
                        COLUMN_LABELS[col], row + 1, timeToPlayMove, numBoardsEvaluated))
            else:
                noValidMovesInARow += 1
                if noValidMovesInARow == 2:
                    print("Neither player has any valid moves left!")
                    userScore, aiScore = currentScore(self.userPiece, self.board)
                    if userScore > aiScore:
                        self.endGame(self.userPiece)
                    elif aiScore > userScore:
                        self.endGame(self.opponentPiece)
                    else:
                        self.endGame()
                noValidMovesColor = self.textColorOf(turn)
                playAgainColor = self.textColorOf(opponentOf(turn))
                print(
                    f"{noValidMovesColor}%s{NO_COLOR} has no valid moves this turn! {playAgainColor}%s{NO_COLOR} will play again." % (
                        nameOfPieceColor(turn), nameOfPieceColor(opponentOf(turn))))
                self.linesWrittenToConsole += 3 + BOARD_DIMENSION
            isOver, winner = checkGameOver(self.board)
            if isOver:
                self.endGame(winner)
            turn = opponentOf(turn)

    def printBoard(self, highlightedCoordinates=None, board=None):
        """Prints the gameBoard in a human-readable format"""
        if highlightedCoordinates is None:
            highlightedCoordinates = []
        if board is None:
            board = self.board
        print("\n\t    %s" % " ".join(COLUMN_LABELS))
        for rowNum in range(BOARD_DIMENSION):
            print("\t%d%s| " % (rowNum + 1, "" if rowNum > 8 else " "), end='')
            for colNum in range(BOARD_DIMENSION):
                piece = pieceAt(rowNum, colNum, board)
                pieceColor = HIGHLIGHT if [rowNum, colNum] in highlightedCoordinates else ''
                pieceColor += self.textColorOf(piece)
                print(f"{pieceColor}%s{NO_COLOR} " % piece, end='')
            if rowNum == BOARD_DIMENSION // 2:
                print("   %d turns remain." % (numberOfPieceOnBoard(EMPTY, board)), end='')
            print()
        userScore, aiScore = currentScore(self.userPiece, board)
        additionalIndent = " " * ((2 + (2 * (BOARD_DIMENSION // 2 - 1))) - (1 if userScore >= 10 else 0))
        print(f"\t{additionalIndent}{GREEN_COLOR}{userScore}{NO_COLOR} to {RED_COLOR}{aiScore}{NO_COLOR}\n")

    def printMoveHistory(self, numMovesPrevious):
        """Prints the move history of the current game"""
        while True:
            self.printBoard(self.boardHistory[-(numMovesPrevious + 1)][0], self.boardHistory[-(numMovesPrevious + 1)][1])
            if numMovesPrevious == 0:
                return
            print("(%d move%s before current board state)" % (numMovesPrevious, "s" if numMovesPrevious != 1 else ""))
            numMovesPrevious -= 1
            userInput = input("Press enter for next move, or 'e' to return to game.  ").strip().lower()
            if userInput == 'q':
                self.endGame()
            elif userInput == 'e':
                erasePreviousLines(2)
                return
            else:
                erasePreviousLines(BOARD_DIMENSION + BOARD_OUTLINE_HEIGHT + 2)

    def printOutSaveState(self, turn):
        """Prints out the current state of the board as Python code"""
        print("\n# copy and paste this at the end of the __init__ function in the client")
        outputStr = "self.board = [\n"
        for row in self.board:
            rowStr = "["
            for spot in row:
                rowStr += f"\"{spot}\", "
            rowStr = rowStr[:-2] + "],\n"
            outputStr += rowStr
        outputStr = outputStr[:-2] + "]\n"
        outputStr += f"self.overrideTurn ='{turn}'\n"
        outputStr += "# copy and paste everything above this line\n"
        print(outputStr)


def nameOfPieceColor(piece):
    """Gets the name of the color of the given piece"""
    if piece == BLACK:
        return "BLACK"
    elif piece == WHITE:
        return "WHITE"
    else:
        return "EMPTY"


def getPieceColorInput():
    """Gets input from the user to determine which color they will be"""
    color_input = input("Would you like to be BLACK ('b') or WHITE ('w')?   ").strip().lower()
    erasePreviousLines(1)
    color = BLACK if color_input == 'b' else WHITE
    if color == BLACK:
        print(f"You will be BLACK {GREEN_COLOR}{BLACK}{NO_COLOR}!")
    else:
        print(f"You will be WHITE {GREEN_COLOR}{WHITE}{NO_COLOR}!")
    print(f"Your pieces are shown in {GREEN_COLOR}%s{NO_COLOR}!" % (
        "blue" if GREEN_COLOR == BLUE_COLOR else "green"))
    print(f"Enemy pieces are shown in {RED_COLOR}%s{NO_COLOR}!" % (
        "orange" if RED_COLOR == ORANGE_COLOR else "red"))
    return color

def loadConfiguration():
    """Loads in the saved configuration from config.json"""
    try:
        import json5 as json
    except ImportError:
        print(
            f"{ERROR_SYMBOL} json5 package not found. Remove all comments from config.json to make it readable.")
        import json
    try:
        with open(CONFIG_FILENAME, 'r') as configFile:
            configuration = json.load(configFile)
    except FileNotFoundError:
        print(f"{ERROR_SYMBOL} No configuration file found in the current directory. Using default values.")
        return
    except:
        print(
            f"{ERROR_SYMBOL} There was an issue reading from config.json.")
        return
    if configuration.get("colorblindMode", "").lower() == "true":
        global RED_COLOR, GREEN_COLOR
        RED_COLOR = ORANGE_COLOR
        GREEN_COLOR = BLUE_COLOR
    if configuration.get("aiMaxSearchDepth", "").isdigit():
        setAiMaxSearchDepth(max(int(configuration["aiMaxSearchDepth"]), 1))
    if configuration.get("boardDimension", "").isdigit():
        global SAVE_STATE_OUTPUT_HEIGHT, COLUMN_LABELS
        setBoardDimension(int(configuration["boardDimension"]))
        SAVE_STATE_OUTPUT_HEIGHT = BOARD_DIMENSION + 6
        COLUMN_LABELS = list(map(chr, range(65, 65 + BOARD_DIMENSION)))
    if configuration.get("eraseMode", "").lower() == "false":
        global ERASE_MODE_ON
        ERASE_MODE_ON = False
    if configuration.get("aiMaxValidMovesToEvaluateEachTurn", "").isdigit():
        setAiMaxValidMovesToEvaluate(int(configuration["aiMaxValidMovesToEvaluateEachTurn"]))


def erasePreviousLines(numLines, overrideEraseMode=False):
    """Erases the specified previous number of lines from the terminal"""
    eraseMode = ERASE_MODE_ON if not overrideEraseMode else (not ERASE_MODE_ON)
    if eraseMode:
        print(f"{CURSOR_UP_ONE}{ERASE_LINE}" * max(numLines, 0), end='')


def printGameRules():
    """Gives the user the option to view the rules of the game"""
    print("\nType 'q' at any move prompt to quit the game.")
    print("Type 'p' to show the available moves.")
    print("Type 's' to print out the board's save state.")
    print("Type 'h' at your turn to see previous moves.")
    print("Game constants are modifiable in the config.json file.")
    showRules = input("Would you like to see the rules? (y/n)   ").strip().lower()
    erasePreviousLines(1)
    if showRules == 'q':
        print("\nThanks for playing!")
        exit(0)
    elif showRules == 'y':
        print("""
    - OBJECTIVE: Have more pieces on the board than the opponent when all spaces are full
    - TURNS: Black will go first. Each player will take turns placing one piece each turn
    - GAMEPLAY: Trap enemy pieces between two friendly pieces to convert them to friendly pieces
        """)


def getOpposingAiModuleName():
    """Reads the command line arguments to determine the name of module for the opposing AI"""
    remainingCommandLineArgs = sys.argv[2:]
    for arg in remainingCommandLineArgs:
        if "-" not in arg:
            return arg
    print(f"{ERROR_SYMBOL} You need to provide the name of your AI strategy module.")
    exit(0)


def getDuelingAi():
    """Returns the imported AI Strategy class if the import is valid"""
    duelAiModuleName = getOpposingAiModuleName()
    try:
        DuelingAi  = getattr(import_module(duelAiModuleName), 'Strategy')
        if not issubclass(DuelingAi, Player):
            print(f"{ERROR_SYMBOL} Please make sure your AI is a subclass of 'Player'")
            exit(0)
        return DuelingAi
    except ImportError:
        print(f"{ERROR_SYMBOL} Please provide a valid module to import.\n" +
              f"{INFO_SYMBOL} Pass the name of your Python file as a command line argument, WITHOUT the .py extension.")
        exit(0)
    except AttributeError:
        print(f"{ERROR_SYMBOL} Please make sure your AI's class name is 'Strategy'")
        exit(0)


def main():
    """Prompts user for input and creates a new GameRunner"""
    global AI_DUEL_MODE
    os.system("")  # allows output text coloring for Windows OS
    if "-d" in sys.argv or "-aiDuel" in sys.argv:
        UserPlayerClass = getDuelingAi()
        print(f"\n{INFO_SYMBOL} You are in AI Duel Mode!")
        AI_DUEL_MODE = True
    else:
        UserPlayerClass = HumanPlayer
        AI_DUEL_MODE = False
    print("Welcome to Kyle's Othello AI!")
    loadConfiguration()
    printGameRules()
    game = GameRunner(UserPlayerClass, OthelloStrategy)
    game.start()


if __name__ == '__main__':
    main()
