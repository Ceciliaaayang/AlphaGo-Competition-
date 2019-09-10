from board_evaluator import BoardEvaluator


class BoardSearcher(object):
	"""Board searcher for best next move."""

	def __init__ (self):
		self.evaluator = BoardEvaluator()
		self.board = [ [ 0 for n in range(7) ] for i in range(7) ]
		self.gameover = 0
		self.overvalue = 0
		self.maxdepth = 4	# set the max depth to 3 so that the running time
							# for each move is not too long
							# depth: 1 - <1 sec, 2 - a few sec, 3 - up to 4 min


	def genMoves(self, turn):
		"""Generate all legal moves for the current board.

		store the score and position of each move in a list in format of (score, i, j)
		"""
		moves = []
		board = self.board
		POSES = self.evaluator.POS
		for i in range(7):
			for j in range(7):
				if board[i][j] == 0:
					score = POSES[i][j]
					moves.append((score, i, j))
	
		moves.sort(reverse=True)	# sort moves in reverse order, i.e., with decreasing scores
		return moves
	

	def __search(self, turn, depth, pattern_moves, alpha = -0x7fffffff, beta = 0x7fffffff):
		"""Recursive search, return the best score.
		
		Minimax algorithm with alpha-beta pruning.
		0x7fffffff == (2^31)-1, indicating a large value
		"""
		# print(depth, "aaa")
		# base case: depth is 0
		# evaluate the board and return
		if depth <= 0:
			score = self.evaluator.evaluate(self.board, turn)
			return score

		# if game over, return immediately (??? RAY)
		# do you check the full board (RAY ??)
		score = self.evaluator.evaluate(self.board, turn)
		# print(score, 'aaaaaaaa', 'depth', depth)
		if abs(score) >= 9999 and depth < self.maxdepth: 
			return score
		if sum([i.count(0) for i in self.board]) == 0:
			return 0

		# first search check if has patter move
		if depth == self.maxdepth and len(pattern_moves) > 0:
			moves = pattern_moves
		else:
			moves = self.genMoves(turn)

		# generate new moves
		# moves = self.genMoves(turn)
		bestmove = None

		# for all current moves
		# len(moves) == num of empty intersections on current board
		# worst case O(m^n) or O( m!/(m-n)! ), m = num of empty spots, 
		# 			n = depth(num of further steps this program predicts)
		# print(moves, 'eee')
		for score, row, col in moves:

			# label current move to board
			self.board[row][col] = turn
			
			# calculate next turn
			if turn == 1:
				nturn = 2
			elif turn == 2:
				nturn = 1
			
			# DFS, return score and position of move
			score = - self.__search(
				turn=nturn, 
				depth=depth - 1, 
				pattern_moves=pattern_moves,
				alpha=-beta, 
				beta=-alpha)
			# print(score, 'score')

			# clear current move on board
			self.board[row][col] = 0

			# calculate the move with best score
			# alpha beta pruning: removes nodes that are evaluated by the minimax algorithm
			# 				in the search tree, eliminates branches that cannot posibbly
			#				influence the final decision.
			# print(score, 'aa', depth, 'aa')
			# print(alpha, 'bb', depth, 'bb')
			if score > alpha:
				alpha = score
				bestmove = (row, col)
				if alpha >= beta:
					break
		
		# if depth is max depth, record the best move
		# print(depth, 'dd')
		# print(bestmove, 'bestmove')
		if depth == self.maxdepth and bestmove:
			self.bestmove = bestmove

		# return current best score and its correponding move
		# print(self.bestmove)
		# print(alpha, 'aaaass')
		return alpha

	# specific search
	# args: turn: 1(black)/2(white), depth
	def search(self, board, turn, pattern_moves, depth=3):
		self.board = board
		self.maxdepth = depth
		self.bestmove = None
		score = self.__search(turn=turn, depth=depth, pattern_moves=pattern_moves)
		if abs(score) > 8000:
			self.maxdepth = depth
			score = self.__search(turn=turn, depth=1, pattern_moves=pattern_moves)
		row, col = self.bestmove
		return score, row, col