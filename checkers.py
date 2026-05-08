#!/usr/bin/env python3
"""
Checkers (Draughts) Game - Command-line implementation
Features:
- 8x8 board
- Two-player turn-based gameplay
- Standard capture and kinging rules
- Move notation input/output (e.g., 'e2-e4')
"""

import re
from typing import Optional


class CheckersGame:
    """Checkers game implementation with standard rules."""
    
    # Board representation: 8x8 grid
    # Pieces: 'r' = red, 'b' = black, 'R' = red king, 'B' = black king
    # Empty squares are represented as None
    
    def __init__(self):
        """Initialize the game board and state."""
        self.board = self._create_initial_board()
        self.current_player = 'red'  # Red starts first
        self.red_pieces = 12
        self.black_pieces = 12
        self.red_kings = 0
        self.black_kings = 0
        self.game_over = False
        self.winner = None
        self.must_capture = False  # If a capture is available, player must take it
        
    def _create_initial_board(self) -> list:
        """Create the initial 8x8 board with pieces in starting positions."""
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Place red pieces on odd columns of rows 0-2 (top of board)
        # Row 0: columns 1, 3, 5, 7
        # Row 1: columns 0, 2, 4, 6
        # Row 2: columns 1, 3, 5, 7
        for row in range(3):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 'r'
        
        # Place black pieces on even columns of rows 5-7 (bottom of board)
        for row in range(5, 8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    board[row][col] = 'b'
        
        return board
    
    def _is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is within board bounds."""
        return 0 <= row < 8 and 0 <= col < 8
    
    def _is_square_valid(self, row: int, col: int) -> bool:
        """Check if a square is a valid playing square (dark squares)."""
        return self._is_valid_position(row, col) and (row + col) % 2 == 1
    
    def get_piece(self, row: int, col: int) -> Optional[str]:
        """Get the piece at a given position."""
        if self._is_valid_position(row, col):
            return self.board[row][col]
        return None
    
    def _is_red_piece(self, piece: str) -> bool:
        """Check if a piece belongs to the red player."""
        return piece.lower() == 'r'
    
    def _is_black_piece(self, piece: str) -> bool:
        """Check if a piece belongs to the black player."""
        return piece.lower() == 'b'
    
    def _is_king(self, piece: str) -> bool:
        """Check if a piece is a king."""
        return piece.isupper()
    
    def _is_own_piece(self, piece: str) -> bool:
        """Check if a piece belongs to the current player."""
        if self.current_player == 'red':
            return self._is_red_piece(piece)
        else:
            return self._is_black_piece(piece)
    
    def _get_direction(self, piece: str) -> list:
        """Get the valid movement directions for a piece."""
        if self._is_king(piece):
            return [-1, 1]  # Kings can move both directions
        elif self._is_red_piece(piece):
            return [1]  # Red moves down (increasing row index)
        else:
            return [-1]  # Black moves up (decreasing row index)
    
    def _get_opponent_pieces(self) -> list:
        """Get the character(s) representing opponent pieces."""
        if self.current_player == 'red':
            return ['b', 'B']
        else:
            return ['r', 'R']
    
    def get_all_valid_moves(self) -> list:
        """Get all valid moves for the current player."""
        moves = []
        capture_moves = []
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and self._is_own_piece(piece):
                    piece_moves = self._get_piece_moves(row, col, piece)
                    for move in piece_moves:
                        if move['capture']:
                            capture_moves.append(move)
                        else:
                            moves.append(move)
        
        # If capture is available, must take it (standard rules)
        if capture_moves:
            return capture_moves
        return moves
    
    def _get_piece_moves(self, row: int, col: int, piece: str) -> list:
        """Get all valid moves for a specific piece."""
        moves = []
        directions = self._get_direction(piece)
        
        # Check regular moves (non-capture)
        for d_row in directions:
            for d_col in [-1, 1]:
                new_row, new_col = row + d_row, col + d_col
                if self._is_square_valid(new_row, new_col) and self.board[new_row][new_col] is None:
                    moves.append({
                        'from_row': row,
                        'from_col': col,
                        'to_row': new_row,
                        'to_col': new_col,
                        'capture': None
                    })
        
        # Check capture moves
        for d_row in [-1, 1]:  # Can capture in any diagonal direction
            for d_col in [-1, 1]:
                jump_row, jump_col = row + 2 * d_row, col + 2 * d_col
                mid_row, mid_col = row + d_row, col + d_col
                
                if (self._is_square_valid(jump_row, jump_col) and 
                    self.board[jump_row][jump_col] is None):
                    
                    mid_piece = self.board[mid_row][mid_col]
                    if (mid_piece is not None and 
                        mid_piece in self._get_opponent_pieces()):
                        
                        # Verify directional constraint for captures
                        can_capture = False
                        if self._is_king(piece):
                            can_capture = True
                        elif self._is_red_piece(piece):
                            can_capture = d_row == 1
                        else:
                            can_capture = d_row == -1
                        
                        if can_capture:
                            moves.append({
                                'from_row': row,
                                'from_col': col,
                                'to_row': jump_row,
                                'to_col': jump_col,
                                'capture': (mid_row, mid_col)
                            })
        
        return moves
    
    def parse_move(self, move_str: str) -> Optional[dict]:
        """Parse move notation like 'e2-e4' or 'e2 to e4'."""
        move_str = move_str.strip().lower()
        
        # Match patterns like "e2-e4", "e2 to e4", "e2 e4"
        pattern = r'^([a-h])([1-8])\s*[-to]*\s*([a-h])([1-8])$'
        match = re.match(pattern, move_str)
        
        if not match:
            return None
        
        from_col = ord(match.group(1)) - ord('a')
        from_row = 8 - int(match.group(2))
        to_col = ord(match.group(3)) - ord('a')
        to_row = 8 - int(match.group(4))
        
        return {
            'from_col': from_col,
            'from_row': from_row,
            'to_col': to_col,
            'to_row': to_row
        }
    
    def execute_move(self, move: dict) -> bool:
        """Execute a move and update the board state."""
        from_row = move['from_row']
        from_col = move['from_col']
        to_row = move['to_row']
        to_col = move['to_col']
        
        piece = self.board[from_row][from_col]
        self.board[from_row][from_col] = None
        self.board[to_row][to_col] = piece
        
        # Handle capture
        if move['capture']:
            cap_row, cap_col = move['capture']
            captured_piece = self.board[cap_row][cap_col]
            self.board[cap_row][cap_col] = None
            
            if self._is_red_piece(captured_piece):
                self.red_pieces -= 1
            else:
                self.black_pieces -= 1
        
        # Check for king promotion
        promoted = False
        if not self._is_king(piece):
            if (self._is_red_piece(piece) and to_row == 7) or \
               (self._is_black_piece(piece) and to_row == 0):
                self.board[to_row][to_col] = piece.upper()
                promoted = True
                if self._is_red_piece(piece):
                    self.red_kings += 1
                else:
                    self.black_kings += 1
        
        # Check win condition
        if self.red_pieces == 0:
            self.game_over = True
            self.winner = 'black'
        elif self.black_pieces == 0:
            self.game_over = True
            self.winner = 'red'
        else:
            # Check if the moving piece can capture again (double jump)
            if move['capture']:
                further_moves = self._get_piece_moves(to_row, to_col, self.board[to_row][to_col])
                has_capture = any(m['capture'] for m in further_moves)
                if has_capture:
                    self.must_capture = True
                    return True  # Turn continues
            
            # Switch turns
            self.must_capture = False
            self.current_player = 'black' if self.current_player == 'red' else 'red'
        
        return True
    
    def display_board(self):
        """Display the current board state."""
        print("\n  a b c d e f g h")
        print(" +-----------------+")
        
        for row in range(8):
            print(f"{8 - row}|", end=" ")
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    print(".", end=" ")
                elif piece.lower() == 'r':
                    print("r", end=" ")
                elif piece.lower() == 'b':
                    print("b", end=" ")
                else:
                    print(piece, end=" ")
            print(f"|{8 - row}")
        
        print(" +-----------------+")
        print("  a b c d e f g h")
        
        # Display piece counts and kings
        print(f"\nRed pieces: {self.red_pieces} (Kings: {self.red_kings})")
        print(f"Black pieces: {self.black_pieces} (Kings: {self.black_kings})")
    
    def convert_position(self, row: int, col: int) -> str:
        """Convert board coordinates to algebraic notation (e.g., 'e2')."""
        return f"{chr(ord('a') + col)}{8 - row}"
    
    def play(self):
        """Main game loop."""
        print("=" * 50)
        print("       WELCOME TO CHECKERS!")
        print("=" * 50)
        print("\nInstructions:")
        print("- Red moves first")
        print("- Enter moves in format: e2-e4 (from e2 to e4)")
        print("- Capture moves are mandatory if available")
        print("- Pieces become Kings when reaching the opposite end")
        print("- First player to eliminate all opponent pieces wins!")
        print()
        
        while not self.game_over:
            self.display_board()
            
            print(f"\n{self.current_player.capitalize()}'s turn")
            
            # Check if current player has any valid moves
            valid_moves = self.get_all_valid_moves()
            
            if not valid_moves:
                self.game_over = True
                self.winner = 'black' if self.current_player == 'red' else 'red'
                break
            
            # If player must capture, inform them
            if self.must_capture:
                print("You must capture! Available captures:")
                for move in valid_moves:
                    from_pos = self.convert_position(move['from_row'], move['from_col'])
                    to_pos = self.convert_position(move['to_row'], move['to_col'])
                    print(f"  {from_pos} to {to_pos}")
            
            # Get player input
            while True:
                move_input = input("\nEnter your move (e.g., e2-e4): ").strip()
                
                if move_input.lower() in ['quit', 'q', 'exit']:
                    print("\nGame ended by player.")
                    return
                
                move = self.parse_move(move_input)
                
                if move is None:
                    print("Invalid move format. Use: e2-e4")
                    continue
                
                # Check if move is valid
                move_match = None
                for m in valid_moves:
                    if (m['from_row'] == move['from_row'] and 
                        m['from_col'] == move['from_col'] and
                        m['to_row'] == move['to_row'] and 
                        m['to_col'] == move['to_col']):
                        move_match = m
                        break
                
                if move_match:
                    self.execute_move(move_match)
                    from_pos = self.convert_position(move['from_row'], move['from_col'])
                    to_pos = self.convert_position(move['to_row'], move['to_col'])
                    print(f"\nMove: {from_pos} to {to_pos}")
                    break
                else:
                    print("Invalid move. Try again.")
        
        # Game over - display final state
        self.display_board()
        print("\n" + "=" * 50)
        print(f"       GAME OVER! {self.winner.upper()} WINS!")
        print("=" * 50)


def main():
    """Main entry point."""
    game = CheckersGame()
    game.play()


if __name__ == "__main__":
    main()
