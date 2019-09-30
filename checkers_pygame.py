import copy
import pygame , sys
from pygame.locals import *
import random
import time
from operator import itemgetter

pygame.font.init()

##COLORS##
#             R    G    B 
WHITE    = (255, 255, 255)
BLUE     = (  0,   0, 255)
RED      = (255,   0,   0)
BLACK    = (  0,   0,   0)
GOLD     = (255, 215,   0)
HIGH     = (160, 190, 255)

##DIRECTIONS##
NORTHWEST = "northwest"
NORTHEAST = "northeast"
SOUTHWEST = "southwest"
SOUTHEAST = "southeast"

class Game:
	"""
	The main game control.
	"""

	def __init__(self):
		self.graphics = Graphics()
		self.board = Board()
		
		self.turn = BLUE
		self.selected_piece = None # a board location. 
		self.hop = False
		self.selected_legal_moves = []

	def setup(self):
		"""Draws the window and board at the beginning of the game"""
		self.graphics.setup_window()

	def event_loop(self):
		"""
		The event loop. This is where events are triggered 
		(like a mouse click) and then effect the game state.
		"""
		self.mouse_pos = self.graphics.board_coords(pygame.mouse.get_pos()) # what square is the mouse in?
		if self.selected_piece != None:
			self.selected_legal_moves = self.board.legal_moves(self.selected_piece, self.hop)

		for event in pygame.event.get():

			if event.type == QUIT:
				self.terminate_game()

			if event.type == MOUSEBUTTONDOWN:
				if self.hop == False:
					if self.board.location(self.mouse_pos).occupant != None and self.board.location(self.mouse_pos).occupant.color == self.turn:
						self.selected_piece = self.mouse_pos

					elif self.selected_piece != None and self.mouse_pos in self.board.legal_moves(self.selected_piece):

						self.board.move_piece(self.selected_piece, self.mouse_pos)
					
						if self.mouse_pos not in self.board.adjacent(self.selected_piece):
							self.board.remove_piece((self.selected_piece[0] + (self.mouse_pos[0] - self.selected_piece[0]) / 2, self.selected_piece[1] + (self.mouse_pos[1] - self.selected_piece[1]) / 2))
						
							self.hop = True
							self.selected_piece = self.mouse_pos

						else:
							self.end_turn()

				if self.hop == True:					
					if self.selected_piece != None and self.mouse_pos in self.board.legal_moves(self.selected_piece, self.hop):
						self.board.move_piece(self.selected_piece, self.mouse_pos)
						self.board.remove_piece((self.selected_piece[0] + (self.mouse_pos[0] - self.selected_piece[0]) / 2, self.selected_piece[1] + (self.mouse_pos[1] - self.selected_piece[1]) / 2))

					if self.board.legal_moves(self.mouse_pos, self.hop) == []:
							self.end_turn()

					else:
						self.selected_piece = self.mouse_pos

	def random_computer_move(self):
		has_hopped = False
		#hop_status = self.board.can_hop(selected_coordinates)
		possible_moves = self.board.all_possible_moves(self.turn, has_hopped)
		while len(possible_moves) > 0:
			total_move_set = random.choice(possible_moves)
			selected_coordinates = total_move_set[0]
			choosen_move = total_move_set[1]
			self.board.move_piece(selected_coordinates, choosen_move)
			if choosen_move not in self.board.adjacent(selected_coordinates):
				self.board.remove_piece((selected_coordinates[0] + (choosen_move[0] - selected_coordinates[0]) / 2, selected_coordinates[1] + (choosen_move[1] - selected_coordinates[1]) / 2))
						
				has_hopped = True
				selected_coordinates = choosen_move
				possible_moves = self.board.legal_moves(selected_coordinates, hop = has_hopped)

			else:
				possible_moves = []
		
		self.end_turn()



	def heuristic_computer_move(self):
		has_hopped = False
		#possible_moves = []
		#piece_coordinates = self.board.show_pieces(self.turn)
		possible_moves = self.board.all_possible_moves(self.turn, has_hopped)
		total_move_set = self.choose_move(possible_moves, self.turn, self.board)
		for move in total_move_set:
			current_coordinates = move[0]
			destination = move[1]							#everything up to and including this line is just choosing the move
			self.board.move_piece(current_coordinates, destination)
			if destination not in self.board.adjacent(current_coordinates):
				self.board.remove_piece((current_coordinates[0] + (destination[0] - current_coordinates[0]) / 2, current_coordinates[1] + (destination[1] - current_coordinates[1]) / 2))
			
		self.end_turn()


	def intelligent_computer_move(self, num_children, depth):
		#print "\n\n\n\n\n\n\n"
		has_hopped = False
		current_state = Node(self.board, self.turn, 0, ())
		self.make_minimax_tree(current_state, depth, num_children)
		self.search_minimax_tree(current_state)
		total_move_set = self.choose_minimax_move(current_state)
		#print "choosen: " + str(total_move_set)
		for move in total_move_set:
			current_coordinates = move[0]
			destination = move[1]
			#self.graphics.highlight_squares([destination], current_coordinates)
			self.graphics.update_display(self.board, [destination], current_coordinates)
			time.sleep(1)
			self.board.move_piece(current_coordinates, destination)
			if destination not in self.board.adjacent(current_coordinates):
				self.board.remove_piece((current_coordinates[0] + (destination[0] - current_coordinates[0]) / 2, current_coordinates[1] + (destination[1] - current_coordinates[1]) / 2))

		
		self.end_turn()

	#def minimax_computer_move(self):

	def make_minimax_tree(self, root, depth, num_children): #root is a node
		if depth > 0:
			has_hopped = False
			possible_moves = root.board.all_possible_moves(root.turn, has_hopped) ## should this be root.board or self.board? I changed it to root.board
			#print "\n" + str(possible_moves) + "\n"
			top_moves = self.choose_moves(possible_moves, num_children, root.turn, root.board)
			if root.turn == RED:
				child_color = BLUE
			else:
				child_color = RED
			for option in top_moves:
				move = option[0]
				move_score = option[1]
				board = option[2]
				root.children.append(Node(board, child_color, move_score, move))
				#print "\n" + str(depth) + " " + str(move) + " " + str(move_score) + "\n"
			for child in root.children:
				self.make_minimax_tree(child, depth-1, num_children)


	def search_minimax_tree(self, tree_head): #tree_head is a node  ##all this does is bring scores up, doesnt touch moves
		if len(tree_head.children) > 0:
			for child in tree_head.children:
				self.search_minimax_tree(child)
			tree_head.score = -max(child.score for child in tree_head.children)

	def choose_minimax_move(self, tree_head): #picks the move we want to do from immediate children
		for child in tree_head.children:
			if child.score == -tree_head.score:
				return child.move







	def board_score(self, board, color):
		own_piece_prioritizer = 1.3 #how much you weight own pieces as opposed to opponents pieces
		king_extra_value = 0.8 # how much extra a king counts for (is added on)
		piece_advantage = self.piece_advantage_counter(board, own_piece_prioritizer, king_extra_value, color)
		#if piece_advantage >= 0:
		#	possible_losses_factor = 0.9  #how much you value pieces that could be taken
		#if piece_advantage < 0:
		#	possible_losses_factor = 1.1
		return piece_advantage

	def test_move(self, total_move_set, given_board): #takes in a possible move and returns a possible board 
		test_board = copy.deepcopy(given_board)
		for move in total_move_set:
			current_coordinates = move[0]
			destination = move[1]
			test_board.move_piece(current_coordinates, destination)
			if destination not in test_board.adjacent(current_coordinates):
				test_board.remove_piece((current_coordinates[0] + (destination[0] - current_coordinates[0]) / 2, current_coordinates[1] + (destination[1] - current_coordinates[1]) / 2))
		return test_board
	
	def choose_move(self, possible_moves, color, board):
		choosen_move = []
		high_score = -10000000000000000000
		for move in possible_moves:
			test_board = self.test_move(move, board)
			move_score = self.board_score(test_board, color)
			if move_score > high_score:
				choosen_move = move
				high_score = move_score
		return choosen_move

	def choose_moves(self, possible_moves, num_moves, color, board):  #chooses the top "n" moves #returns moves as (move, score, board created)
		possible_boards = []
		possible_move_scores = []
		for move in possible_moves:
			test_board = self.test_move(move, board)
			possible_boards.append(test_board)
			move_score = self.board_score(test_board, color)
			possible_move_scores.append(move_score)
		possible_moves_zipped = [(x,y,z) for (z,y,x) in zip(possible_boards,possible_move_scores,possible_moves)]
		possible_moves_sorted = sorted(possible_moves_zipped, key=itemgetter(1))
		length_possible_moves_sorted = len(possible_moves_sorted)
		if length_possible_moves_sorted < num_moves:
			choosen_moves = possible_moves_sorted
		else:
			choosen_moves = possible_moves_sorted[length_possible_moves_sorted - num_moves:]
		return choosen_moves




	def piece_advantage_counter(self, board, own_piece_prioritizer, king_extra_value, color): #counts the piece advantage of a given board
		if color == RED:
			opponent_color = BLUE
		else:
			opponent_color = RED
		piece_coordinates = board.show_pieces(color)
		opponent_piece_coordinates = board.show_pieces(opponent_color)
		num_pieces = len(piece_coordinates)
		for coordinate in piece_coordinates:
			x = coordinate[0]
			y = coordinate[1]
			piece = board.matrix[x][y].occupant
			if piece.king == True:
				num_pieces += king_extra_value
		num_opponent_pieces = len(opponent_piece_coordinates)
		for coordinate in opponent_piece_coordinates:
			x = coordinate[0]
			y = coordinate[1]
			piece = board.matrix[x][y].occupant
			if piece.king == True:
				num_opponent_pieces += king_extra_value
		piece_advantage = own_piece_prioritizer*num_pieces - num_opponent_pieces
		return piece_advantage
		
	#def pieces_in_danger(self, board, possible_losses_factor): #count how many pieces can be taken on opponents next move. Value of piece dacays the more there
																# are since opponent can only take one. Kings are more valuable. possible loses factor is how much we care
																# about possible losses relative to 1 being normal value on pieces

	
	def is_piece_in_danger(self, board, x, y, color):
		adjacent_sqaures = board.adjacent(x, y)
		if color == BLUE:
			forward_sqaures = [adjacent_sqaures[0], adjacent_sqaures[1]]
			backwards_squares = [adjacent_sqaures[2], adjacent_sqaures[3]]
		if color == RED:
			forward_sqaures = [adjacent_sqaures[2], adjacent_sqaures[3]]
			backwards_squares = [adjacent_sqaures[0], adjacent_sqaures[1]]
		x_temp = forward_sqaures[0][0]
		y_temp = forward_sqaures[0][1]
		if board.matrix[x_temp][y_temp].occupant != None and board.matrix[x_temp][y_temp].occupant.color != color:
			x_temp = backwards_squares[1][0]
			y_temp = backwards_squares[1][1]
			if board.matrix[x_temp][y_temp].occupant == None:
				return True
		x_temp = forward_sqaures[1][0]
		y_temp = forward_sqaures[1][1]
		if board.matrix[x_temp][y_temp].occupant != None and board.matrix[x_temp][y_temp].occupant.color != color:
			x_temp = backwards_squares[0][0]
			y_temp = backwards_squares[0][1]
			if board.matrix[x_temp][y_temp].occupant == None:
				return True
		return False




	def update(self):
		"""Calls on the graphics class to update the game display."""
		self.graphics.update_display(self.board, self.selected_legal_moves, self.selected_piece)

	def terminate_game(self):
		"""Quits the program and ends the game."""
		pygame.quit()
		sys.exit
		

	def main(self):
		""""This executes the game and controls its flow."""
		self.setup()

		while True: # main game loop
			if self.turn == BLUE:
				self.event_loop()
				
			else:
				self.intelligent_computer_move(5, 4)

			self.update()

	def end_turn(self):
		"""
		End the turn. Switches the current player. 
		end_turn() also checks for and game and resets a lot of class attributes.
		"""
		if self.turn == BLUE:
			self.turn = RED
		else:
			self.turn = BLUE

		self.selected_piece = None
		self.selected_legal_moves = []
		self.hop = False

		if self.check_for_endgame():
			if self.turn == BLUE:
				self.graphics.draw_message("RED WINS!")
			else:
				self.graphics.draw_message("BLUE WINS!")

	def check_for_endgame(self):
		"""
		Checks to see if a player has run out of moves or pieces. If so, then return True. Else return False.
		"""
		for x in xrange(8):
			for y in xrange(8):
				if self.board.location((x,y)).color == BLACK and self.board.location((x,y)).occupant != None and self.board.location((x,y)).occupant.color == self.turn:
					if self.board.legal_moves((x,y)) != []:
						return False

		return True


class Node:
	def __init__(self, board, turn, score, move):
		self.board = board
		self.turn = turn
		self.score = score
		self.move = move #the move required to obtain the board
		self.children = []


class Graphics:
	def __init__(self):
		self.caption = "Checkers"

		self.fps = 60
		self.clock = pygame.time.Clock()

		self.window_size = 600
		self.screen = pygame.display.set_mode((self.window_size, self.window_size))
		self.background = pygame.image.load('resources/board.png')

		self.square_size = self.window_size / 8
		self.piece_size = self.square_size / 2

		self.message = False

	def setup_window(self):
		"""
		This initializes the window and sets the caption at the top.
		"""
		pygame.init()
		pygame.display.set_caption(self.caption)

	def update_display(self, board, legal_moves, selected_piece):
		"""
		This updates the current display.
		"""
		self.screen.blit(self.background, (0,0))
		
		self.highlight_squares(legal_moves, selected_piece)
		self.draw_board_pieces(board)

		if self.message:
			self.screen.blit(self.text_surface_obj, self.text_rect_obj)

		pygame.display.update()
		self.clock.tick(self.fps)

	def draw_board_squares(self, board):
		"""
		Takes a board object and draws all of its squares to the display
		"""
		for x in xrange(8):
			for y in xrange(8):
				pygame.draw.rect(self.screen, board[x][y].color, (x * self.square_size, y * self.square_size, self.square_size, self.square_size), )
	
	def draw_board_pieces(self, board):
		"""
		Takes a board object and draws all of its pieces to the display
		"""
		for x in xrange(8):
			for y in xrange(8):
				if board.matrix[x][y].occupant != None:
					pygame.draw.circle(self.screen, board.matrix[x][y].occupant.color, self.pixel_coords((x,y)), self.piece_size) 

					if board.location((x,y)).occupant.king == True:
						pygame.draw.circle(self.screen, GOLD, self.pixel_coords((x,y)), int (self.piece_size / 1.7), self.piece_size / 4)


	def pixel_coords(self, board_coords):
		"""
		Takes in a tuple of board coordinates (x,y) 
		and returns the pixel coordinates of the center of the square at that location.
		"""
		return (board_coords[0] * self.square_size + self.piece_size, board_coords[1] * self.square_size + self.piece_size)

	def board_coords(self, (pixel_x, pixel_y)):
		"""
		Does the reverse of pixel_coords(). Takes in a tuple of of pixel coordinates and returns what square they are in.
		"""
		return (pixel_x / self.square_size, pixel_y / self.square_size)	

	def highlight_squares(self, squares, origin):
		"""
		Squares is a list of board coordinates. 
		highlight_squares highlights them.
		"""
		for square in squares:
			pygame.draw.rect(self.screen, HIGH, (square[0] * self.square_size, square[1] * self.square_size, self.square_size, self.square_size))	

		if origin != None:
			pygame.draw.rect(self.screen, HIGH, (origin[0] * self.square_size, origin[1] * self.square_size, self.square_size, self.square_size))

	def draw_message(self, message):
		"""
		Draws message to the screen. 
		"""
		self.message = True
		self.font_obj = pygame.font.Font('freesansbold.ttf', 44)
		self.text_surface_obj = self.font_obj.render(message, True, HIGH, BLACK)
		self.text_rect_obj = self.text_surface_obj.get_rect()
		self.text_rect_obj.center = (self.window_size / 2, self.window_size / 2)

class Board:
	def __init__(self):
		self.matrix = self.new_board()

	def new_board(self):
		"""
		Create a new board matrix.
		"""

		# initialize squares and place them in matrix

		matrix = [[None] * 8 for i in xrange(8)]

		# The following code block has been adapted from
		# http://itgirl.dreamhosters.com/itgirlgames/games/Program%20Leaders/ClareR/Checkers/checkers.py
		for x in xrange(8):
			for y in xrange(8):
				if (x % 2 != 0) and (y % 2 == 0):
					matrix[y][x] = Square(WHITE)
				elif (x % 2 != 0) and (y % 2 != 0):
					matrix[y][x] = Square(BLACK)
				elif (x % 2 == 0) and (y % 2 != 0):
					matrix[y][x] = Square(WHITE)
				elif (x % 2 == 0) and (y % 2 == 0): 
					matrix[y][x] = Square(BLACK)

		# initialize the pieces and put them in the appropriate squares

		for x in xrange(8):
			for y in xrange(3):
				if matrix[x][y].color == BLACK:
					matrix[x][y].occupant = Piece(RED)
			for y in xrange(5, 8):
				if matrix[x][y].color == BLACK:
					matrix[x][y].occupant = Piece(BLUE)

		return matrix

	def board_string(self, board):
		"""
		Takes a board and returns a matrix of the board space colors. Used for testing new_board()
		"""

		board_string = [[None] * 8] * 8 

		for x in xrange(8):
			for y in xrange(8):
				if board[x][y].color == WHITE:
					board_string[x][y] = "WHITE"
				else:
					board_string[x][y] = "BLACK"

	
	def rel(self, dir, (x,y)):
		"""
		Returns the coordinates one square in a different direction to (x,y).
		===DOCTESTS===
		>>> board = Board()
		>>> board.rel(NORTHWEST, (1,2))
		(0,1)
		>>> board.rel(SOUTHEAST, (3,4))
		(4,5)
		>>> board.rel(NORTHEAST, (3,6))
		(4,5)
		>>> board.rel(SOUTHWEST, (2,5))
		(1,6)
		"""
		if dir == NORTHWEST:
			return (x - 1, y - 1)
		elif dir == NORTHEAST:
			return (x + 1, y - 1)
		elif dir == SOUTHWEST:
			return (x - 1, y + 1)
		elif dir == SOUTHEAST:
			return (x + 1, y + 1)
		else:
			return 0

	def adjacent(self, (x,y)):
		"""
		Returns a list of squares locations that are adjacent (on a diagonal) to (x,y).
		"""

		return [self.rel(NORTHWEST, (x,y)), self.rel(NORTHEAST, (x,y)),self.rel(SOUTHWEST, (x,y)),self.rel(SOUTHEAST, (x,y))]

	def location(self, (x,y)):
		"""
		Takes a set of coordinates as arguments and returns self.matrix[x][y]
		This can be faster than writing something like self.matrix[coords[0]][coords[1]]
		"""

		return self.matrix[x][y]

	def blind_legal_moves(self, (x,y)):
		"""
		Returns a list of blind legal move locations from a set of coordinates (x,y) on the board. 
		If that location is empty, then blind_legal_moves() return an empty list.
		"""

		if self.matrix[x][y].occupant != None:
			
			if self.matrix[x][y].occupant.king == False and self.matrix[x][y].occupant.color == BLUE:
				blind_legal_moves = [self.rel(NORTHWEST, (x,y)), self.rel(NORTHEAST, (x,y))]
				
			elif self.matrix[x][y].occupant.king == False and self.matrix[x][y].occupant.color == RED:
				blind_legal_moves = [self.rel(SOUTHWEST, (x,y)), self.rel(SOUTHEAST, (x,y))]

			else:
				blind_legal_moves = [self.rel(NORTHWEST, (x,y)), self.rel(NORTHEAST, (x,y)), self.rel(SOUTHWEST, (x,y)), self.rel(SOUTHEAST, (x,y))]

		else:
			blind_legal_moves = []

		return blind_legal_moves

	def legal_moves(self, (x,y), hop = False):
		"""
		Returns a list of legal move locations from a given set of coordinates (x,y) on the board.
		If that location is empty, then legal_moves() returns an empty list.
		"""

		blind_legal_moves = self.blind_legal_moves((x,y)) 
		legal_moves = []

		if hop == False:
			for move in blind_legal_moves:
				if hop == False:
					if self.on_board(move):
						if self.location(move).occupant == None:
							legal_moves.append(move)

						elif self.location(move).occupant.color != self.location((x,y)).occupant.color and self.on_board((move[0] + (move[0] - x), move[1] + (move[1] - y))) and self.location((move[0] + (move[0] - x), move[1] + (move[1] - y))).occupant == None: # is this location filled by an enemy piece?
							legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))

		else: # hop == True
			for move in blind_legal_moves:
				if self.on_board(move) and self.location(move).occupant != None:
					if self.location(move).occupant.color != self.location((x,y)).occupant.color and self.on_board((move[0] + (move[0] - x), move[1] + (move[1] - y))) and self.location((move[0] + (move[0] - x), move[1] + (move[1] - y))).occupant == None: # is this location filled by an enemy piece?
						legal_moves.append((move[0] + (move[0] - x), move[1] + (move[1] - y)))
		
		return legal_moves

	def all_possible_moves(self, color, has_hopped = False): ##returns all possible moves a player can make     ##has hopped is either True or False
		possible_moves = []
		piece_coordinates = self.show_pieces(color)
		for piece in piece_coordinates:
			king = self.location(piece).occupant.king
			piece_possible_moves = self.legal_moves(piece, hop = has_hopped)
			for move in piece_possible_moves:
				if move not in self.adjacent(piece):
					possible_moves += self.multiple_jump_moves(move, king, color, [(piece, move)], [])
				else:
					possible_moves += [[(piece, move)]]
		return possible_moves

	def multiple_jump_moves(self, (x,y), king, color, path, jump_moves): #recursively finds all jumping paths
		possible_next_locations = self.possible_jump_locations((x,y), king, color, path)
		jump_moves += [path]
		for location in possible_next_locations:
			if color == RED and location[1] == 7:
				self.multiple_jump_moves(location, True, color, path + [((x,y), location)], jump_moves)
			elif color == BLUE and location[1] == 0:
				self.multiple_jump_moves(location, True, color, path + [((x,y), location)], jump_moves)
			else:
				self.multiple_jump_moves(location, king, color, path + [((x,y), location)], jump_moves)
		return jump_moves
		

	def possible_jump_locations(self, (x,y), king, color, path): #takes in a piece and returns possible hop spots
		piece_has_been = []
		for move in path:
			piece_has_been += [move[0]]
		available_landing_spots = []
		if color == RED:
			if self.on_board((x+1, y+1)) and self.location((x+1, y+1)).occupant != None and self.location((x+1, y+1)).occupant.color == BLUE:
				if self.on_board((x+2, y+2)) and self.location((x+2, y+2)).occupant == None:
					if (x+2,y+2) not in piece_has_been:
						available_landing_spots += [(x+2,y+2)]
			if self.on_board((x-1, y+1)) and self.location((x-1, y+1)).occupant != None and self.location((x-1, y+1)).occupant.color == BLUE:
				if self.on_board((x-2, y+2)) and self.location((x-2, y+2)).occupant == None:
					if (x-2,y+2) not in piece_has_been:
						available_landing_spots += [(x-2,y+2)]
			if king:
				if self.on_board((x-1, y-1)) and self.location((x-1, y-1)).occupant != None and self.location((x-1, y-1)).occupant.color == BLUE:
					if self.on_board((x-2, y-2)) and self.location((x-2, y-2)).occupant == None:
						if (x-2,y-2) not in piece_has_been:
							available_landing_spots += [(x-2,y-2)]
				if self.on_board((x+1, y-1)) and self.location((x+1, y-1)).occupant != None and self.location((x+1, y-1)).occupant.color == BLUE:
					if self.on_board((x+2, y-2)) and self.location((x+2, y-2)).occupant == None:
						if (x+2,y-2) not in piece_has_been:
							available_landing_spots += [(x+2,y-2)]
		if color == BLUE:
			if self.on_board((x-1, y-1)) and self.location((x-1, y-1)).occupant != None and self.location((x-1, y-1)).occupant.color == RED:
				if self.on_board((x-2, y-2)) and self.location((x-2, y-2)).occupant == None:
					if (x-2,y-2) not in piece_has_been:
						available_landing_spots += [(x-2,y-2)]
			if self.on_board((x+1, y-1)) and self.location((x+1, y-1)).occupant != None and self.location((x+1, y-1)).occupant.color == RED:
				if self.on_board((x+2, y-2)) and self.location((x+2, y-2)).occupant == None:
					if (x+2,y-2) not in piece_has_been:
						available_landing_spots += [(x+2,y-2)]
			if king:
				if self.on_board((x+1, y+1)) and self.location((x+1, y+1)).occupant != None and self.location((x+1, y+1)).occupant.color == RED:
					if self.on_board((x+2, y+2)) and self.location((x+2, y+2)).occupant == None:
						if (x+2,y+2) not in piece_has_been:
							available_landing_spots += [(x+2,y+2)]
				if self.on_board((x-1, y+1)) and self.location((x-1, y+1)).occupant != None and self.location((x-1, y+1)).occupant.color == RED:
					if self.on_board((x-2, y+2)) and self.location((x-2, y+2)).occupant == None:
						if (x-2,y+2) not in piece_has_been:
							available_landing_spots += [(x-2,y+2)]
		return available_landing_spots



	def remove_piece(self, (x,y)):
		"""
		Removes a piece from the board at position (x,y). 
		"""
		self.matrix[x][y].occupant = None

	def move_piece(self, (start_x, start_y), (end_x, end_y)):
		"""
		Move a piece from (start_x, start_y) to (end_x, end_y).
		"""

		self.matrix[end_x][end_y].occupant = self.matrix[start_x][start_y].occupant
		self.remove_piece((start_x, start_y))

		self.king((end_x, end_y))


	def is_end_square(self, coords):
		"""
		Is passed a coordinate tuple (x,y), and returns true or 
		false depending on if that square on the board is an end square.
		===DOCTESTS===
		>>> board = Board()
		>>> board.is_end_square((2,7))
		True
		>>> board.is_end_square((5,0))
		True
		>>>board.is_end_square((0,5))
		False
		"""

		if coords[1] == 0 or coords[1] == 7:
			return True
		else:
			return False

	def on_board(self, (x,y)):
		"""
		Checks to see if the given square (x,y) lies on the board.
		If it does, then on_board() return True. Otherwise it returns false.
		===DOCTESTS===
		>>> board = Board()
		>>> board.on_board((5,0)):
		True
		>>> board.on_board(-2, 0):
		False
		>>> board.on_board(3, 9):
		False
		"""

		if x < 0 or y < 0 or x > 7 or y > 7:
			return False
		else:
			return True


	def king(self, (x,y)):
		"""
		Takes in (x,y), the coordinates of square to be considered for kinging.
		If it meets the criteria, then king() kings the piece in that square and kings it.
		"""
		if self.location((x,y)).occupant != None:
			if (self.location((x,y)).occupant.color == BLUE and y == 0) or (self.location((x,y)).occupant.color == RED and y == 7):
				self.location((x,y)).occupant.king = True

	def show_pieces(self, player_color):
		piece_coordinates = []
		for x in xrange(8):
			for y in xrange(8):
				if self.matrix[x][y].occupant != None and self.matrix[x][y].occupant.color == player_color:
					piece_coordinates.append((x,y)) 
		return piece_coordinates
	
	def can_hop(self, (x,y)):
		if self.matrix[x][y].occupant != None:
			piece = self.matrix[x][y].occupant
			color = piece.color
			king = piece.king
			if color == BLUE:
				if self.matrix[x-1][y-1].occupant != None and self.matrix[x-1, y-1].occupant.color == RED:
					if self.matrix[x-2][y-2].occupant == None:
						return True
				if self.matrix[x+1][y-1].occupant != None and self.matrix[x+1, y-1].occupant.color == RED:
					if self.matrix[x+2][y-2].occupant == None:
						return True
				if king == True:
					if self.matrix[x-1][y+1].occupant != None and self.matrix[x-1, y+1].occupant.color == RED:
						if self.matrix[x-2][y+2].occupant == None:
							return True
					if self.matrix[x+1][y+1].occupant != None and self.matrix[x+1, y+1].occupant.color == RED:
						if self.matrix[x+2][y+2].occupant == None:
							return True
			if color == RED:
				if self.matrix[x-1][y+1].occupant != None and self.matrix[x-1, y+1].occupant.color == BLUE:
					if self.matrix[x-2][y+2].occupant == None:
						return True
				if self.matrix[x+1][y+1].occupant != None and self.matrix[x+1, y+1].occupant.color == BLUE:
					if self.matrix[x+2][y+2].occupant == None:
						return True
				if king == True:
					if self.matrix[x-1][y-1].occupant != None and self.matrix[x-1, y-1].occupant.color == BLUE:
						if self.matrix[x-2][y-2].occupant == None:
							return True
					if self.matrix[x+1][y-1].occupant != None and self.matrix[x+1, y-1].occupant.color == BLUE:
						if self.matrix[x+2][y-2].occupant == None:
							return True
		return False



class Piece:
	def __init__(self, color, king = False):
		self.color = color
		self.king = king

class Square:
	def __init__(self, color, occupant = None):
		self.color = color # color is either BLACK or WHITE
		self.occupant = occupant # occupant is a Square object

def main():
	game = Game()
	game.main()

if __name__ == "__main__":
	main()














