'''
This class is responsible for storing all the information about the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It will also keep a move Log.
'''

class GameState():
    def __init__(self):
    #board is an 8x8 2d list, each element of the list has 2 characters.
    #The first character represents the color of the piece, 'b' or 'w'
    #The second character represents the type of the piece, 'K', 'Q' 'R', 'B', 'N' or 'P' 
    #"--" represents an empty space with no piece.
        self.board = [
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "bQ"],
        ["--", "--", "wR", "--", "--", "--", "--", "--"],
        ["--", "--", "--", "--", "--", "--", "--", "--"],
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False
        self.stale_mate = False
        self.enpassant_possible = () #coordinates to square where en-passant is possible 
        self.current_castling_rights = Castle_Rights(True, True, True, True)
        self.castle_rights_log = [Castle_Rights(self.current_castling_rights.wks, self.current_castling_rights.bks, 
                                                self.current_castling_rights.wqs, self.current_castling_rights.bqs)]


    '''
    Takes a Move as a paarameter and executes it.(does not work for castling, pawn promotion, and en-passant)
    '''
    def make_move(self, move):
        self.board[move.start_row][move.start_column] = "--" #changes square that the piece moved from to an empty square
        self.board[move.end_row][move.end_column] = move.piece_moved #changed square that the piece moved to hold the piece
        self.move_log.append(move) #stores move object to move log so move can be undone later
        self.white_to_move = not self.white_to_move #swaps turn to move to other player
        #update king location
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_column)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_column)

        
        #pawn promotion
        if move.is_pawn_promotion: #auto promotes to a queen on back rank
            self.board[move.end_row][move.end_column] = move.piece_moved[0] + 'Q'

        #en passant
        if move.is_enpassant:
            self.board[move.start_row][move.end_column] = '--'
            
        #Update en passant variable
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2: #checks for 2 square pawn advances
            self.enpassant_possible = ((move.start_row + move.end_row)//2, move.end_column)
        else:
            self.enpassant_possible = ()

        #castle move
        if move.is_castle_move:
            if move.end_column - move.start_column == 2: #king side
                self.board[move.end_row][move.end_column-1] = self.board[move.end_row][move.end_column+1] #moves rook to new square
                self.board[move.end_row][move.end_column+1] = '--' #Removes old rook
            else: #queen side
                 #king side
                self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-2] #moves rook to new square
                self.board[move.end_row][move.end_column-2] = '--' #Removes old rook

        #update castling rights - when rook or king moves for the first time
        self.update_castle_rights(move)
        self.castle_rights_log.append(Castle_Rights(self.current_castling_rights.wks, self.current_castling_rights.bks, 
                                                self.current_castling_rights.wqs, self.current_castling_rights.bqs))


    '''
    Undo the last move made
    '''
    def undo_move(self):
        if len(self.move_log) != 0: #makes sure a move has been made
            move = self.move_log.pop() #pops the prev move off the move log
            self.board[move.start_row][move.start_column] = move.piece_moved #resets piece captured
            self.board[move.end_row][move.end_column] = move.piece_captured #brings moved piece back to start
            self.white_to_move = not self.white_to_move #resets turn to correct player
            #update king location
            if move.piece_moved == 'wK':
                self.white_king_location = ( move.start_row,  move.start_column)
            elif move.piece_moved == 'bK':
                self.black_king_location = ( move.start_row,  move.start_column)
        self.check_mate = False #updating values incase player undos a checkmate or stalemate
        self.stale_mate = False
        #undo enpassant
        if move.is_enpassant:
            self.board[move.end_row][move.end_column] = '--'
            self.board[move.start_row][move.end_column] = move.piece_captured
            self.enpassant_possible = (move.end_row, move.end_column)
        #undo 2 square pawn advance
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ()
        #undo castle rights
        self.castle_rights_log.pop() #get rid of new castle rights from prev move
        new_rights = self.castle_rights_log[-1] #set castle rights back to prev state
        self.current_castling_rights =  Castle_Rights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)
        #undo castle move
        if move.is_castle_move:
            if move.end_column - move.start_column == 2:
                self.board[move.end_row][move.end_column+1] = self.board[move.end_row][move.end_column-1]
                self.board[move.end_row][move.end_column-1] = '--'
            else:  #queen side
                self.board[move.end_row][move.end_column-2] = self.board[move.end_row][move.end_column+1]
                self.board[move.end_row][move.end_column+1] = '--'
    '''
    Update the castle rights for each move
    '''
    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':#removes whites castling rights if they ever move their king
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == 'bK':#removes blacks castling rights if they ever move their king
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False

        #removes king-side/queen-side castling on the side where the rook left its starting location
        elif move.piece_moved == 'wR' and move.start_row == 7:
            if move.start_column == 0:
                self.current_castling_rights.wqs = False
            elif move.start_column == 7:
                self.current_castling_rights.wqs = False
        
        elif move.piece_moved == 'bR' and move.start_row == 0:
            if move.start_column == 0:
                self.current_castling_rights.wqs = False
            elif move.start_column == 7:
                self.current_castling_rights.wqs = False

        

    '''
    To ensure the player doesn't make an illegal move putting themself in check, you have to check every possible move by:
    1. Make the move
    2. Generate all possible moves for opposing player in new position
    3. Check if any of their moves attacks your king
    4. If the king is safe, the move is legal.
    5. Return list of valid moves
    '''

    '''
    All moves considering check
    '''
    def get_legal_moves(self):
        temp_enpassant_possible = self.enpassant_possible #save enpassant state before checking moves
        temp_castle_rights = Castle_Rights(self.current_castling_rights.wks, self.current_castling_rights.bks, #copy current castle rights
                                                self.current_castling_rights.wqs, self.current_castling_rights.bqs)
        #generate all possible moves
        moves = self.get_possible_moves()
        if self.white_to_move:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        #for each move make the move
        for i in range(len(moves)-1, -1, -1): #going through list in reverse to remove elements
            self.make_move(moves[i])
            #swap back to my turn
            #generate all opponents move for every move
            #find any opponents moves that directly attack your king
            self.white_to_move = not self.white_to_move 
            if self.in_check():
                moves.remove(moves[i]) #if your opponent can attack your king this move is removed from legal move list
            self.white_to_move = not self.white_to_move
            self.undo_move()
        
        if len(moves) == 0: #either stalemate or checkmate
            if self.in_check:
                self.check_mate = True
            else:
                self.stale_mate = True

        self.enpassant_possible = temp_enpassant_possible #reaplying enpassant moves
        self.current_castling_rights = temp_castle_rights
        return moves



    '''
    determines if player is in check
    '''
    def in_check(self):
        if self.white_to_move:#check for white king under attack
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:#check for black king under attack
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])


    '''
    determine if enemy can attack square r, c'''
    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move #swap to opponents turn
        opp_moves = self.get_possible_moves() #generate all opponents possible moves
        self.white_to_move = not self.white_to_move #swap turns back to player
        for move in opp_moves: #check all moves to see if any attack my king
            if move.end_row == r and move.end_column == c: #king is under attack
                return True
        return False




    '''
    All possible moves without considering check
    '''
    def get_possible_moves(self):
        moves = []
        for row in range(len(self.board)): #number of rows
            for column in range(len(self.board[row])): #number of columns in row
                turn = self.board[row][column][0] 
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move): #makes sure selected piece belongs to the player
                    piece = self.board[row][column][1]
                    self.move_functions[piece](row, column, moves)  #finds what piece the algorythm is looking at and adds its legal moves
        return moves


    '''
    Get all pawn moves for the pawn located at row, column and adds them to the list
    '''
    def get_pawn_moves(self, row, column, moves):
        if 0 < row < 7:
            if self.white_to_move:
                if self.board[row-1][column] == '--': #1 square forward
                    moves.append(Move((row, column), (row-1, column), self.board))

                    if row == 6 and self.board[row-2][column] == '--':#2 squares forward
                        moves.append(Move((row, column), (row-2, column), self.board))

                if column-1 >= 0: #pawn capture to left
                    if self.board[row-1][column-1][0] == 'b': 
                        moves.append(Move((row, column), (row-1, column-1), self.board))
                    elif (row-1, column-1) == self.enpassant_possible: #Checks for en-passant moves
                        moves.append(Move((row, column), (row-1, column-1), self.board, is_enpassant=True))

                if column+1 <= 7: #pawn capture to right
                    if self.board[row-1][column+1][0] == 'b':
                        moves.append(Move((row, column), (row-1, column+1), self.board))
                    elif (row-1, column+1) == self.enpassant_possible: #Checks for en-passant moves
                        moves.append(Move((row, column), (row-1, column+1), self.board, is_enpassant=True))

            else: #black pawn moves
                if self.board[row+1][column] == '--': #1 square forward
                    moves.append(Move((row, column), (row+1, column), self.board))

                    if row == 1 and self.board[row+2][column] == '--':#2 squares forward
                        moves.append(Move((row, column), (row+2, column), self.board))

                if column-1 >= 0: #pawn capture to left
                    if self.board[row+1][column-1][0] == 'w':
                        moves.append(Move((row, column), (row+1, column-1), self.board))
                    elif (row+1, column-1) == self.enpassant_possible: #Checks for en-passant moves
                        moves.append(Move((row, column), (row+1, column-1), self.board, is_enpassant=True))

                if column+1 <= 7: #pawn capture to right
                    if self.board[row+1][column+1][0] == 'w': 
                        moves.append(Move((row, column), (row+1, column+1), self.board))
                    elif (row+1, column+1) == self.enpassant_possible: #Checks for en-passant moves
                        moves.append(Move((row, column), (row+1, column+1), self.board, is_enpassant=True))



    '''
    Get all rook moves for the rook located at row, column and adds them to the list
    '''
    def get_rook_moves(self, row, column, moves):
        player, opponent = self.find_player_color()

        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        self.append_moves(directions, row, column, moves, player, opponent)




    '''
    Get all knight moves for the knight located at row, column and adds them to the list
    '''
    def get_knight_moves(self, row, column, moves):
        player, _ = self.find_player_color()

        directions = [(row-2, column-1), (row-1, column-2), (row-2, column+1),(row-1, column+2),
                 (row+2, column-1), (row+1, column-2), (row+2, column+1), (row+1, column+2)]

        for direction in directions:
            if ((0 <= direction[0] <= 7 and 0 <= direction[1] <= 7) and self.board[direction[0]][direction[1]][0] != player):
                moves.append(Move((row, column), (direction[0], direction[1]), self.board))
        
    '''
    Get all bishop moves for the bishop located at row, column and adds them to the list
    '''
    def get_bishop_moves(self, row, column, moves):
        player, opponent = self.find_player_color()

        directions = [(1, 1), (-1, -1), (-1, 1), (1, -1)]

        self.append_moves(directions, row, column, moves, player, opponent)



    '''
    Get all queen moves for the queen located at row, column and adds them to the list
    '''
    def get_queen_moves(self, row, column, moves):
        player, opponent = self.find_player_color()

        directions = [(1, 1), (-1, -1), (-1, 1), (1, -1), (1, 0), (0, 1), (-1, 0), (0, -1)]

        self.append_moves(directions, row, column, moves, player, opponent)


    '''
    Get all king moves for the king located at row, column and adds them to the list
    '''
    def get_king_moves(self, row, column, moves):
        player, _ = self.find_player_color()

        directions = [(1, 1), (-1, -1), (-1, 1), (1, -1), (1, 0), (0, 1), (-1, 0), (0, -1)]

        for direction in directions:
            end_row = row + direction[0] 
            end_column = column + direction[1]

            if not (0 <= end_row <= 7) or not(0 <= end_column <= 7):
                continue #if end row out of range or end column out of range break

            if self.board[end_row][end_column][0] == player:
                continue #if your piece is on the tile then break
            moves.append(Move((row, column), (end_row, end_column), self.board))

        



    '''
    Generate all valid castle moves for king at row, column
    '''
    def get_castle_moves(self, row, column, moves):
        
        if self.square_under_attack(row, column):
            
            return #cant castle while in check
        if (self.white_to_move and self.current_castling_rights.wks) or (not self.white_to_move and self.current_castling_rights.bks):
            
            self.get_king_side_castle_moves(row, column, moves)
        if (self.white_to_move and self.current_castling_rights.wqs) or (not self.white_to_move and self.current_castling_rights.bqs):
            
            self.get_queen_side_castle_moves(row, column, moves)

    def get_king_side_castle_moves(self, row, column, moves):
        if self.board[row][column+1] == '--' and self.board[row][column+2] == '--':
            if not self.square_under_attack(row, column+1) and not self.square_under_attack(row, column+2):
                moves.append(Move((row, column),(row, column+2), self.board, is_castle_move=True))


    def get_queen_side_castle_moves(self, row, column, moves):
        if self.board[row][column-1] == '--' and self.board[row][column-2] == '--' and self.board[row][column-3] == '--':
            if not self.square_under_attack(row, column-1) and not self.square_under_attack(row, column-2):
                moves.append(Move((row, column),(row, column-2), self.board, is_castle_move=True))
    
    '''
    Helper funstions for get_piece_move funstions
    '''
    def find_player_color(self): #helper funtion for the get_piece_move functions that returns 
        if self.white_to_move:   #the color of the current player and their opponent
            player = 'w'
            opponent = 'b'
        else:
            player = 'b'
            opponent = 'w' 
        return player, opponent


    def can_move(self, end_row, end_column, player): #helper function for the get_piece_move functions that lets you know if a tile exists and is clear
        if not (0 <= end_row <= 7) or not(0 <= end_column <= 7) :
            return False #if end row out of range or end column out of range then False

        if self.board[end_row][end_column][0] == player:
            return False #if your piece is on the tile then False
        return True


    def append_moves(self, directions, row, column, moves, player, opponent): #helper function for the get_piece_move functions 
        for direction in directions:                                          #appends all possible moves to moves
            for tiles in range(1, 8):
                end_row = row + direction[0] * tiles #increments tiles every move in given direction added to starting row
                end_column = column + direction[1] * tiles

                if not self.can_move(end_row, end_column, player):
                    break

                moves.append(Move((row, column), (end_row, end_column), self.board))#Adds move to possible moves list

                if self.board[end_row][end_column][0] == opponent:#If your oponents piece is on this tile stop searching in this direction
                    break



    

    '''
The move class stores all information about a move to make it easier to go back to previous board states without storing 
the entire board after every move.
'''

class Move():
    #maps keys to values
    #key : value
    ranks_to_rows = {'1':7, '2':6, '3':5, '4':4, '5':3, '6':2, '7':1, '8':0} #takes rank chess notation and converts it to python row index for board
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()} #inverts ranks_to_rows to convert python row index into rank chess notation

    files_to_columns = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7} #takes file chess notation and converts it to python column index for board
    columns_to_files = {v: k for k, v in files_to_columns.items()} #inverts files_to_columns to convert python column index into file chess notation

    def __init__(self, start_sq, end_sq, board, is_enpassant=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_column = start_sq[1]
        self.end_row = end_sq[0]
        self.end_column = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_column]
        self.piece_captured = board[self.end_row][self.end_column]
        #keeps track of pawn promotion moves to help with undos
        self.is_pawn_promotion = (self.piece_moved == ('wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7))
        #keeps track of en passant moves to help with undos
        self.is_enpassant = is_enpassant
        if self.is_enpassant:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'
        #castle move
        self.is_castle_move = is_castle_move
        #generetes a unique 4 digit move id for every move in a given board state
        self.move_id = (self.start_row * 1000) + (self.start_column * 100) + (self.end_row * 10) + (self.end_column) 

        


    '''
    overide object equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self): #return chess noation for start click and end click using get_rank_file.
        return self.get_rank_file(self.start_row, self.start_column) + self.get_rank_file(self.end_row, self.end_column)


    def get_rank_file(self, r, c): # takes row and column index and converts it into chess notation using dictionaries found above.
        return self.columns_to_files[c] + self.rows_to_ranks[r]



class Castle_Rights():
    
    def __init__(self, wks, bks, wqs, bqs): #white king side, black king side, white queen side, black queen side
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs










