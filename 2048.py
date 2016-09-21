import curses
from random import randrange, choice
from collections import defaultdict


letterCodes = [ord(ch) for ch in 'WASDRQwasdrq']
actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
actionsDict = dict(zip(letterCodes, actions * 2))


def GetUserAction(keyboard):
	char = 'N'
	while char not in actionsDict:
		char = keyboard.getch()
	return actionsDict[char]


# field is a list of tuple, in another word, a matrix	
def Transpose(field):
	return [list(row) for row in zip(*field)] # unzip, transpose the matrix
	

# invert rows of  matrix
def Invert(field):
	return [row[::-1] for row in field]
	
	
class GameField(object):
	
	def __init__(self, height = 4, width = 4, win=32):
		self.height = height
		self.width = width
		self.winValue = 2048
		self.score = 0
		self.highScore = 0
		self.Reset()
		
		
	def Reset(self):
		if self.score > self.highScore:
			self.highScore = self.score
		self.score = 0
		self.field = [[0 for i in range(self.width)] for j in range(self.height)]  # construct the original matrix
		self.Spawn()
		self.Spawn()
		
		
	def Move(self, direction):
	
		def MoveRowLeft(row):
		
			def Tighten(row):
				# squeeze non-zero elements together
				newRow = [i for i in row if i != 0]		
				newRow += [0 for i in range(len(row) - len(newRow))]  
				return newRow
				
			def Merge(row):
				pair = False     # flag of pairs have the same value
				newRow = []
				
				for i in range(len(row)):
					if pair:
						newRow.append(2 * row[i])
						self.score += 2 * row[i]
						pair = False
					elif i + 1 < len(row) and row[i] == row[i + 1]:
						pair = True
						newRow.append(0)
					else:
						newRow.append(row[i])
				assert len(newRow) == len(row)
				return newRow
				
			return Tighten(Merge(Tighten(row)))
		
		# initial moves distionary
		moves = {}
		moves['Left'] = lambda field:  [MoveRowLeft(row) for row in field]
		moves['Right'] = lambda field:  Invert(moves['Left'](Invert(field)))
		moves['Up'] = lambda field:  Transpose(move['Left'](Transpose(field)))
		moves['Down'] = lambda field:  Transpose(moves['Right'](Transpose(field)))
			
		if direction in moves:
			if self.MoveIsPossible(direction):
				self.field = moves[direction](self.field)
				self.Spawn()
				return True
			else:
				return False
				
			
	def IsWin(self):
		return any(any(i >= self.winValue for i in row) for row in self.field)
			
		
	def IsGameOver(self):
		return not any(self.MoveIsPossible(move) for move in actions)
			
			
	def Draw(self, screen):
		helpString1 = '(W)Up (S)Down (A)Left (D)Right'
		helpString2 = '     (R)Restart (Q)Exit'
		gameOverString = '		  GAME OVER'
		winString = '			   YOU WIN!'
			
		def Cast(string):
			screen.addstr(string + '\n')
			
		def DrawHorSeparator():
			line = '+' + ('+------' * self.width + '+')[1:]
			separator = defaultdict(lambda: line)
			
			if not hasattr(DrawHorSeparator, 'counter'):
				DrawHorSeparator.counter = 0
			Cast(seperator[DrawHorSeparator.counter])
			DrawHorSeparator.counter += 1
				
		def DrawRow(row):
			Cast(''.join("|{: ^5} ".format(num) if num > 0 else '|' for num in row) + '|')
			screen.clear()
			Cast("SCORE: " + str(self.score))
			if 0 != self.highScore:
				Cast("HIGHSCORE: " + str(self.highScore))
				
			for row in self.field:
				DrawHorSeparator()
			DrawRow(row)
			DrawHorSeparator()
				
			if self.IsWin():
				Cast(winString)
			elif self.IsGameOver():
				Cast(gameOverString)
			else:
				Cast(helpString1)
			Cast(helpString2)
	
	# generate new 2 or 4
	def Spawn(self):
			newElement = 4 if randrange(100) > 89 else 2
			(i, j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
			self.field[i][j] = newElement
				
	def MoveIsPossible(self, direction):
	
		def RowIsLeftMovable(row):	
			
			def Change(i):
				if row[i] == 0 and row[i+1] == row[i]:
					return True
				if row[i] != 0 and row[i+1] == row[i]:
					return True
				return False	
					
			return any(Change(i) for i in range(len(row) - 1))
					
		check = {}
		check['Left'] = lambda field:  any(RowIsLeftMovable(row) for row in field)
		check['Right'] = lambda field:  check['Left'](Invert(field))
		check['Up'] = lambda field:  check['Left'](Transpose(field))
		check['Down'] = lambda field:  check['Right'](Transpose(field))
		
		if direction in check:
			return check[direction](self.field)
		else:
			return False
			
def main(stdscr):
	
	def Init():
		gameField.Reset()
		return 'Game'
		
	
	def NotGame(state):
		gameField.Draw(stdscr)
		action = GetUserAction(stdscr)
		responses = defaultdict(lambda: state)
		responses['Restart'], responses['Exit'] = 'Init', 'Exit'
		return responses[action]
		
		
	def Game():
		gameField.Draw(stdscr)
		action = GetUserAction(stdscr)
		
		if action == 'Restart':
			return 'Init'
		if action == 'Exit':
			return 'Exit'
		if gameField.Move(action):
			if gameField.IsWin():
				return 'Win'
			if gameField.IsGameOver():
				return 'Gameover'
		return 'Game'
		
		
	stateActions = {
			'Init': Init,
			'Win': lambda: NotGame('Win'),
			'Gameover': lambda: NotGame('Gameover'),
			'Game': Game
	}
	
	curses.use_default_colors()
	gameField = GameField(win=32)
	
	state = 'Init'
	
	while state != 'Exit':
		state = stateActions[state]()
		
		
curses.wrapper(main)