class ChessGame:
    def __init__(self):
        self.board = self.initial_board()
        self.moves = []
        self.white_king_position = (7, 4)
        self.black_king_position = (0, 4)
        self.white_turn = True
        self.castling_rights = {"white": {"king_side": True, "queen_side": True},
                               "black": {"king_side": True, "queen_side": True}}
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1

    def initial_board(self):
        board = [
            ["r", "n", "b", "q", "k", "b", "n", "r"],
            ["p", "p", "p", "p", "p", "p", "p", "p"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["P", "P", "P", "P", "P", "P", "P", "P"],
            ["R", "N", "B", "Q", "K", "B", "N", "R"]
        ]
        return board

    def parse_move(self, move):
        if len(move) == 2:
            file = ord(move[0]) - ord('a')
            rank = int(move[1]) - 1
            return file, rank
        elif len(move) == 4:
            file = ord(move[0]) - ord('a')
            rank = int(move[1]) - 1
            return file, rank
        else:
            raise ValueError("Invalid move format")

    def is_valid_move(self, move):
        file, rank = self.parse_move(move)
        piece = self.board[rank][file]
        if piece == "":
            return False
        if self.white_turn and piece.islower():
            return False
        if not self.white_turn and piece.isupper():
            return False
        if self.is_in_check(self.white_king_position if self.white_turn else self.black_king_position):
            return False
        return self.is_legal_move(move)

    def is_legal_move(self, move):
        file, rank = self.parse_move(move)
        start_file, start_rank = self.parse_move(self.moves[-1] if self.moves else "e2" if self.white_turn else "e7")
        piece = self.board[start_rank][start_file]
        piece_type = piece.lower()
        if piece_type == "p":
            return self.is_legal_pawn_move(move, start_file, start_rank)
        elif piece_type == "r":
            return self.is_legal_rook_move(move, start_file, start_rank)
        elif piece_type == "n":
            return self.is_legal_knight_move(move, start_file, start_rank)
        elif piece_type == "b":
            return self.is_legal_bishop_move(move, start_file, start_rank)
        elif piece_type == "q":
            return self.is_legal_queen_move(move, start_file, start_rank)
        elif piece_type == "k":
            return self.is_legal_king_move(move, start_file, start_rank)
        return False

    def is_legal_pawn_move(self, move, start_file, start_rank):
        file, rank = self.parse_move(move)
        if self.white_turn:
            if rank == start_rank - 1 and file == start_file and self.board[rank][file] == "":
                return True
            if start_rank == 6 and rank == start_rank - 2 and file == start_file and self.board[rank][file] == "" and self.board[rank + 1][file] == "":
                return True
            if abs(file - start_file) == 1 and rank == start_rank - 1 and self.board[rank][file].isupper():
                return True
        else:
            if rank == start_rank + 1 and file == start_file and self.board[rank][file] == "":
                return True
            if start_rank == 1 and rank == start_rank + 2 and file == start_file and self.board[rank][file] == "" and self.board[rank - 1][file] == "":
                return True
            if abs(file - start_file) == 1 and rank == start_rank + 1 and self.board[rank][file].islower():
                return True
        return False

    def is_legal_rook_move(self, move, start_file, start_rank):
        file, rank = self.parse_move(move)
        if file == start_file:
            for r in range(min(start_rank, rank) + 1, max(start_rank, rank)):
                if self.board[r][file] != "":
                    return False
            return True
        elif rank == start_rank:
            for f in range(min(start_file, file) + 1, max(start_file, file)):
                if self.board[rank][f] != "":
                    return False
            return True
        return False

    def is_legal_knight_move(self, move, start_file, start_rank):
        file, rank = self.parse_move(move)
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for move in knight_moves:
            new_file, new_rank = start_file + move[0], start_rank + move[1]
            if new_file == file and new_rank == rank:
                return True
        return False

    def is_legal_bishop_move(self, move, start_file, start_rank):
        file, rank = self.parse_move(move)
        if abs(file - start_file) == abs(rank - start_rank):
            step_file = 1 if file > start_file else -1
            step_rank = 1 if rank > start_rank else -1
            f, r = start_file + step_file, start_rank + step_rank
            while f != file and r != rank:
                if self.board[r][f] != "":
                    return False
                f += step_file
                r += step_rank
            return True
        return False

    def is_legal_queen_move(self, move, start_file, start_rank):
        return self.is_legal_rook_move(move, start_file, start_rank) or self.is_legal_bishop_move(move, start_file, start_rank)

    def is_legal_king_move(self, move, start_file, start_rank):
        file, rank = self.parse_move(move)
        if abs(file - start_file) <= 1 and abs(rank - start_rank) <= 1:
            return True
        if self.is_legal_castling(move):
            return True
        return False

    def is_legal_castling(self, move):
        if self.white_turn:
            if move == "e1g1" and self.castling_rights["white"]["king_side"]:
                if self.board[7][5] == "" and self.board[7][6] == "" and not self.is_in_check(self.white_king_position):
                    return True
            if move == "e1c1" and self.castling_rights["white"]["queen_side"]:
                if self.board[7][1] == "" and self.board[7][2] == "" and self.board[7][3] == "" and not self.is_in_check(self.white_king_position):
                    return True
        else:
            if move == "e8g8" and self.castling_rights["black"]["king_side"]:
                if self.board[0][5] == "" and self.board[0][6] == "" and not self.is_in_check(self.black_king_position):
                    return True
            if move == "e8c8" and self.castling_rights["black"]["queen_side"]:
                if self.board[0][1] == "" and self.board[0][2] == "" and self.board[0][3] == "" and not self.is_in_check(self.black_king_position):
                    return True
        return False

    def is_in_check(self, king_position):
        king_file, king_rank = king_position
        for file in range(8):
            for rank in range(8):
                piece = self.board[rank][file]
                if piece != "" and self.is_opponent(piece, self.white_turn):
                    if self.is_threat(piece, king_position):
                        return True
        return False

    def is_opponent(self, piece, color):
        return (piece.islower() and color) or (piece.isupper() and not color)

    def is_threat(self, piece, position):
        piece_type = piece.lower()
        file, rank = position
        if piece_type == "p":
            return self.is_pawn_threat(piece, position)
        elif piece_type == "r":
            return self.is_rook_threat(piece, position)
        elif piece_type == "n":
            return self.is_knight_threat(piece, position)
        elif piece_type == "b":
            return self.is_bishop_threat(piece, position)
        elif piece_type == "q":
            return self.is_queen_threat(piece, position)
        elif piece_type == "k":
            return self.is_king_threat(piece, position)
        return False

    def is_pawn_threat(self, piece, position):
        file, rank = position
        color = self.white_turn
        if color:
            if file > 0 and self.board[rank][file - 1] == piece:
                return True
            if file < 7 and self.board[rank][file + 1] == piece:
                return True
        else:
            if file > 0 and self.board[rank][file - 1] == piece:
                return True
            if file < 7 and self.board[rank][file + 1] == piece:
                return True
        return False

    def is_rook_threat(self, piece, position):
        file, rank = position
        for i in range(8):
            if self.board[rank][i] == piece or self.board[i][file] == piece:
                return True
        return False

    def is_knight_threat(self, piece, position):
        file, rank = position
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for move in knight_moves:
            new_file, new_rank = file + move[0], rank + move[1]
            if 0 <= new_file < 8 and 0 <= new_rank < 8 and self.board[new_rank][new_file] == piece:
                return True
        return False

    def is_bishop_threat(self, piece, position):
        file, rank = position
        for i in range(1, 8):
            if file + i < 8 and rank + i < 8 and self.board[rank + i][file + i] == piece:
                return True
            if file + i < 8 and rank - i >= 0 and self.board[rank - i][file + i] == piece:
                return True
            if file - i >= 0 and rank + i < 8 and self.board[rank + i][file - i] == piece:
                return True
            if file - i >= 0 and rank - i >= 0 and self.board[rank - i][file - i] == piece:
                return True
        return False

    def is_queen_threat(self, piece, position):
        return self.is_rook_threat(piece, position) or self.is_bishop_threat(piece, position)

    def is_king_threat(self, piece, position):
        file, rank = position
        king_moves = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for move in king_moves:
            new_file, new_rank = file + move[0], rank + move[1]
            if 0 <= new_file < 8 and 0 <= new_rank < 8 and self.board[new_rank][new_file] == piece:
                return True
        return False

    def make_move(self, move):
        if not self.is_valid_move(move):
            return False
        file, rank = self.parse_move(move)
        start_file, start_rank = self.parse_move(self.moves[-1] if self.moves else "e2" if self.white_turn else "e7")
        piece = self.board[start_rank][start_file]
        self.board[start_rank][start_file] = ""
        self.board[rank][file] = piece
        self.moves.append(move)
        self.halfmove_clock += 1
        if piece.lower() == "p" or self.is_capture(move):
            self.halfmove_clock = 0
        if piece.lower() == "k":
            if self.white_turn and move == "e1g1":
                self.board[7][5] = "R"
                self.board[7][7] = ""
                self.white_king_position = (7, 6)
                self.castling_rights["white"]["king_side"] = False
            elif self.white_turn and move == "e1c1":
                self.board[7][3] = "R"
                self.board[7][0] = ""
                self.white_king_position = (7, 2)
                self.castling_rights["white"]["queen_side"] = False
            elif not self.white_turn and move == "e8g8":
                self.board[0][5] = "r"
                self.board[0][7] = ""
                self.black_king_position = (0, 6)
                self.castling_rights["black"]["king_side"] = False
            elif not self.white_turn and move == "e8c8":
                self.board[0][3] = "r"
                self.board[0][0] = ""
                self.black_king_position = (0, 2)
                self.castling_rights["black"]["queen_side"] = False
        self.white_turn = not self.white_turn
        return True

    def is_capture(self, move):
        file, rank = self.parse_move(move)
        return self.board[rank][file] != "" and self.board[rank][file].isupper() != self.white_turn

    def check_rules(self, moves):
        for move in moves:
            if not self.make_move(move):
                return False
        return True

    def play_game(self, moves):
        for move in moves:
            if not self.make_move(move):
                return False
        return True

# Exemple d'utilisation
game = ChessGame()
move = "e4"

if game.make_move(move):
    print("Le coup est valide.")
else:
    print("Le coup n'est pas valide.")