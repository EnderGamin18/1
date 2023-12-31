# Kyle Gerner
# 3.12.2021
# Tool for Game Pigeon's 'Word Bites' puzzle game

from functools import cmp_to_key
from util.terminaloutput.colors import NO_COLOR, BLUE_COLOR, YELLOW_COLOR
from util.terminaloutput.symbols import ERROR_SYMBOL
from util.terminaloutput.erasing import erasePreviousLines

# directional constants
HORIZONTAL = 'H'
VERTICAL = 'V'

# display mode constants
LIST = 0
DIAGRAM = 1

# globals
MAX_LENGTHS = {HORIZONTAL: 8, VERTICAL: 9}  # max length of the words in each direction
DISPLAY_MODE = DIAGRAM  # default display mode
horizPieces = []  # list of horizontal letter groupings
vertPieces = []   # list of vertical letter groupings
singleLetterPieces = []  # list of letter groupings made up of a single letter
englishWords = set()  # LARGE set that will contain every possible word. Using set for O(1) lookup
wordStarts = set()  # set that holds every starting character sequence of every valid word
validWordsOnly = set()  # set of only the valid word strings (no tuple pairing)
validsWithDetails = set()  # contains the words and direction, as well as index of list of pieces from piecesList if in DIAGRAM mode
piecesList = []  # used to keep the list of pieces for a valid word (in DIAGRAM mode), since lists cannot be hashed in the set

LIST_MODE_DIRECTION_COLORS = {HORIZONTAL: BLUE_COLOR, VERTICAL: YELLOW_COLOR}
MORE_INFO_OUTPUT_HEIGHT = 30

WORD_LIST_FILEPATH = 'wordbites/letters9.txt'


def readInBoard():
	"""Read in the user's input for the board pieces"""
	versions = [('Single Letter', singleLetterPieces), 
				('Horizontal', horizPieces), 
				('Vertical', vertPieces)]
	for pair in versions:
		if versions.index(pair) + 1 < len(versions):
			nextInput = "start inputting %s pieces." % versions[versions.index(pair) + 1][0]
		else :
			nextInput ="calculate best piece combinations."
		print("\nPlease enter each %s piece, with each piece on its own line.\n" % pair[0]+ 
			  "When you are done with %s pieces, press 'enter' on an empty line\n" % pair[0]+ 
			  "to %s\n" % nextInput)
		count = 1
		pieceStr = input("%s piece #1:\t" % pair[0]).strip().lower()
		while len(pieceStr) != 0:
			if not pieceStr.isalpha():
				erasePreviousLines(1)
				pieceStr = input(f"{ERROR_SYMBOL} Please make sure your input only contains letters.\t").strip().lower()
			else:
				if len(pieceStr) != 2 and pair[0] != 'Single Letter':
					erasePreviousLines(1)
					pieceStr = input(f"{ERROR_SYMBOL} All %s pieces should be 2 letters long.\t" % pair[0]).strip().lower()
				elif pair[0] == 'Single Letter' and len(pieceStr) > 1:
					erasePreviousLines(1)
					pieceStr = input(f"{ERROR_SYMBOL} You should be entering a single letter right now.\t").strip().lower()
				else:
					pair[1].append(pieceStr)
					count += 1
					pieceStr = input("%s piece #%d:\t" % (pair[0], count)).strip().lower()
		erasePreviousLines(6)
		erasePreviousLines(len(pair[1]))
		pieceListOutput = ", ".join(pair[1])
		print(f"{pair[0]} pieces: {pieceListOutput}")


def findWords():
	"""Calls the recursive findWordsInDirection method for each direction (H and V)"""
	findWordsInDirection(singleLetterPieces, horizPieces, vertPieces, "", HORIZONTAL, [])
	findWordsInDirection(singleLetterPieces, horizPieces, vertPieces, "", VERTICAL, [])


def findWordsInDirection(singles, horiz, vert, currStr, direction, currTuples):
	"""Find all the valid words for a board in a certain direction"""
	if len(currStr) > MAX_LENGTHS[direction]:
		# word too long
		return
	if len(currStr) >= 3 and currStr not in wordStarts:
		# not the beginning of a word so stop searching this expansion
		return
	if currStr in englishWords and currStr not in validWordsOnly:
		# valid word that hasn't been found yet
		validWordsOnly.add(currStr)
		if DISPLAY_MODE == DIAGRAM:
			piecesListIndex = len(piecesList)
			piecesList.append(currTuples)
			tup = currStr, direction, piecesListIndex
		else:
			tup = currStr, direction
		validsWithDetails.add(tup)
	for i in range(len(singles)):
		# copyTuples will keep track of the pieces for a word in DIAGRAM mode, is unnecessary in LIST mode
		if DISPLAY_MODE == DIAGRAM:
			copyTuples = currTuples.copy()
			copyTuples.append(singles[i])
		else:
			copyTuples = []
		findWordsInDirection(singles[:i] + singles[i+1:], horiz, vert, currStr + singles[i], direction, copyTuples)
	for j in range(len(horiz)):
		if DISPLAY_MODE == DIAGRAM:
			copyTuples = currTuples.copy()
			copyTuples.append(horiz[j])
		else:
			copyTuples = []
		if direction == HORIZONTAL:
			findWordsInDirection(singles, horiz[:j] + horiz[j+1:], vert, currStr + horiz[j], direction, copyTuples)
		else:
			for horizLetter in horiz[j]:
				findWordsInDirection(singles, horiz[:j] + horiz[j+1:], vert, currStr + horizLetter, direction, copyTuples)
	for k in range(len(vert)):
		if DISPLAY_MODE == DIAGRAM:
			copyTuples = currTuples.copy()
			copyTuples.append(vert[k])
		else:
			copyTuples = []
		if direction == HORIZONTAL:
			for vertLetter in vert[k]:
				findWordsInDirection(singles, horiz, vert[:k] + vert[k+1:], currStr + vertLetter, direction, copyTuples)
		else:
			findWordsInDirection(singles, horiz, vert[:k] + vert[k+1:], currStr + vert[k], direction, copyTuples)


def word_compare(a, b):
	"""For custom sorting of valid words; sorts longest to shortest, and alphabetically"""
	if len(a[0]) < len(b[0]):
		return 1
	elif len(a[0]) == len(b[0]):
		if a[0] > b[0]: 
			return 1
		elif a[0] < b[0]:
			return -1
		return 0
	return -1


def printOutput(words):
	"""Print the valid words in whichever mode the user selected"""
	count = 1
	print("\n%d word%s found.\n" % (len(words), '' if len(words) == 1 else 's'))
	if DISPLAY_MODE == LIST:
		print("   #  |   Word \t|  Direction\n" +
			  "-------------------------------")
		cmd = ''
		while cmd != 'q':
			if count > 1:
				# if not the first time printing words to output
				erasePreviousLines(12)
			if cmd == 'a':
				while count <= len(words):
					dirSpacing = " "*5 + " "*(9-len(words[count - 1][0]))
					direction = words[count - 1][1]
					directionLetterOutput = LIST_MODE_DIRECTION_COLORS[direction] + direction + NO_COLOR
					print("%d.\t%s%s%s" % (count, words[count - 1][0], dirSpacing, directionLetterOutput))
					count += 1
				print("\nThanks for using my Word Bites Tool!\n")
				return
			for i in range(10):
				dirSpacing = " "*5 + " "*(9-len(words[count - 1][0]))
				direction = words[count - 1][1]
				directionLetterOutput = LIST_MODE_DIRECTION_COLORS[direction] + direction + NO_COLOR
				print("%d.\t%s%s%s" % (count, words[count - 1][0], dirSpacing, directionLetterOutput))
				count += 1
				if count - 1 == len(words):
					# if reached the end of the list
					print("\nNo more words. Thanks for using my Word Bites Tool!\n")
					return
			if count + 8 < len(words):
				grammar = "next 10 words"
			else:
				wordsLeft = len(words) - count + 1
				if wordsLeft > 1:
					grammar = "final %d words" % wordsLeft
				else:
					grammar = "final word"
			cmd = input("\nPress enter for %s, or 'q' to quit, or 'a' for all:\t" % grammar).strip().lower()
		erasePreviousLines(1)
		print("Thanks for using my Word Bites Tool!\n")
	else:
		# DISPLAY_MODE = DIAGRAM
		# NOTE: This display mode was written to conform with the Game Pigeon Word Bites 
		# 		pieces standards, which means all pieces are either length 1 or 2
		wordNum = 1
		linesToEraseFromPreviousOutput = 0
		for wordItem in words:
			if wordNum > 1:
				# if not first time through
				if input("\nPress enter for next word, or 'q' to quit:\t").strip().lower() == 'q':
					erasePreviousLines(1)
					print("Thanks for using my Word Bites Tool!\n")
					exit(0)
			erasePreviousLines(linesToEraseFromPreviousOutput)
			linesToEraseFromPreviousOutput = 3
			# create copies of the pieces lists because they will be edited in the next part
			singePiecesCopy, horizPiecesCopy, vertPiecesCopy = singleLetterPieces.copy(), horizPieces.copy(), vertPieces.copy()
			word, direction, pieces = wordItem[0], wordItem[1], piecesList[wordItem[2]]
			wordWithNumber = "%d:   %s" % (wordNum, word)
			print()
			if direction == HORIZONTAL:
				# if word is horizontal
				indexInWord = 0
				lineAbove, line, lineBelow = "\t", "\t", "\t"
				for piece in pieces:
					if piece in vertPiecesCopy:
						# if the piece is a vertical piece
						vertPiecesCopy.remove(piece)
						if piece.index(word[indexInWord]) == 0:
							# if top letter is in word
							above, cur, below = "  ", piece[0] + " ", piece[1] + " "
						else:
							# bottom letter in word
							above, cur, below = piece[0] + " ", piece[1] + " ", " "
						indexInWord += 1
					elif piece in horizPiecesCopy:
						# if the piece is a horizontal piece
						horizPiecesCopy.remove(piece)
						above, cur, below = "   ", piece + " ", "   "
						indexInWord += 2
					else:
						# piece is a single letter
						singePiecesCopy.remove(piece)
						above, cur, below = "  ", piece  + " ", "  "
						indexInWord += 1
					lineAbove += above
					line += cur 
					lineBelow += below
				afterWordTabs = "\t" * (3 - (len(line) - 1)//8)
				print(f"{lineAbove}\n{line}{afterWordTabs}{wordWithNumber}\n{lineBelow}\n")
				linesToEraseFromPreviousOutput += 4
			else:
				# if word is vertical
				indexInWord = 0
				lineLeft, line, lineRight = "", "", ""
				for piece in pieces:
					if piece in horizPiecesCopy:
						# if the piece is a horizonal piece
						horizPiecesCopy.remove(piece)
						if piece.index(word[indexInWord]) == 0:
							# if left letter is in word
							left, cur, right = " ", piece[0], piece[1]
						else:
							# right letter in word
							left, cur, right = piece[0], piece[1], " "
						indexInWord += 1
					elif piece in vertPiecesCopy:
						# if the piece is a vertical piece
						vertPiecesCopy.remove(piece)
						left, cur, right = "  ", piece, "  "
						indexInWord += 2
					else:
						# piece is a single letter
						singePiecesCopy.remove(piece)
						left, cur, right = " ", piece, " "
						indexInWord += 1
					lineLeft += left
					line += cur 
					lineRight += right
				verticalOutputs = rotateStringsToVertical(lineLeft, line, lineRight)
				indexOfFullWordOutput = max(int(len(verticalOutputs) / 2) - 1, 1)
				count = 0
				for line in verticalOutputs:
					if count == indexOfFullWordOutput:
						line += "\t\t\t%s" % wordWithNumber
					print(line) # 3\t
					count += 1
				linesToEraseFromPreviousOutput += len(verticalOutputs)
			wordNum += 1


def rotateStringsToVertical(leftStr, middleStr, rightStr):
	"""Takes in 3 strings and 'rotates' them so that they print vertically"""
	horizStrings = []
	for i in range(len(leftStr)):
		horizStr = "\t%s %s %s" % (leftStr[i], middleStr[i], rightStr[i])
		horizStrings.append(horizStr)
	return horizStrings


def printModeInfo():
	"""Show the user further information about the different modes available for printing word list"""
	print("------------------------------------------------------------\n" + 
		  "------------------------------------------------------------")
	print("There are two available display modes:\n")
	print("List Mode is one large list, where each word has its own row:\n")
	print("   #  |   Word 	|  Direction\n" +
		  "-------------------------------\n" + 
		  f"1:\tathetised\t{YELLOW_COLOR}V{NO_COLOR}\n" +
		  f"2:\tbirthdays\t{YELLOW_COLOR}V{NO_COLOR}\n" +
		  f"3:\tdiameters\t{BLUE_COLOR}H{NO_COLOR}\n" +
		  " .\t    .\t\t .\n"*3)
	print("Diagram Mode feeds the user 1 word at a time, and displays a\n" + 
		  "visual representation of how to arrange the board pieces:\n")
	print("\t  a l\n\t  t\n\to h\n\t  e\t\t1:   athetised\n\t  t\n\t  i n\n\t  s\n\t  e\n\t  d\n")
	print("Press enter for next word.")


def run():
	"""main method - fills english words sets and calls other functions"""
	global DISPLAY_MODE
	# initial setup
	print("\nWelcome to Kyle's Word Bites Solver!")
	try:
		inputFile = open(WORD_LIST_FILEPATH, 'r')
		for word in inputFile:
			strippedWord = word.strip()
			if len(strippedWord) > max(MAX_LENGTHS.values()):
				continue
			englishWords.add(strippedWord)
			# add each word start to the set of word starts
			for i in range(3, len(strippedWord) + 1):
				wordStarts.add(strippedWord[:i])
		inputFile.close()
	except FileNotFoundError:
		print(f"\n{ERROR_SYMBOL} Could not open word list file. Please make sure {WORD_LIST_FILEPATH.split('/')[-1]} is in the Word Bites directory.\n")
		exit(0)

	# display mode select
	modeSelect = input("\nUse Diagram Mode (d) or List Mode (l)? Type 'i' for more info:\t").strip().lower()
	erasePreviousLines(2)
	if modeSelect == 'i':
		printModeInfo()
		modeSelect = input("\nUse Diagram Mode (d) or List Mode (l)?\n").strip().lower()
		erasePreviousLines(MORE_INFO_OUTPUT_HEIGHT + 2)
	if modeSelect == 'l':
		DISPLAY_MODE = LIST
		print("\nWords will be displayed in List Mode.")
	else:
		print("\nWords will be displayed in Diagram Mode.")

	# read in user input and use it to calculate best piece combinations
	readInBoard()
	findWords()
	word_cmp_key = cmp_to_key(word_compare)
	validWords = sorted(list(validsWithDetails), key=word_cmp_key)
	if len(validWords) == 0:
		print(f"{ERROR_SYMBOL} There were no valid words for the board.")
		exit(0)
	printOutput(validWords)
