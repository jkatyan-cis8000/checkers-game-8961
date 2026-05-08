#!/usr/bin/env python3
"""Test script for Checkers game functionality."""

import sys
sys.path.insert(0, '/workspace/checkers-game-8961')

from checkers import CheckersGame


def test_initial_board():
    """Test that the initial board is set up correctly."""
    game = CheckersGame()
    
    # Check board dimensions
    assert len(game.board) == 8
    for row in game.board:
        assert len(row) == 8
    
    # Check initial piece counts
    assert game.red_pieces == 12
    assert game.black_pieces == 12
    assert game.red_kings == 0
    assert game.black_kings == 0
    
    # Check red pieces in correct positions (rows 0-2)
    for row in range(3):
        for col in range(8):
            if (row + col) % 2 == 1:
                assert game.board[row][col] == 'r', f"Expected red piece at ({row}, {col})"
    
    # Check black pieces in correct positions (rows 5-7)
    for row in range(5, 8):
        for col in range(8):
            if (row + col) % 2 == 1:
                assert game.board[row][col] == 'b', f"Expected black piece at ({row}, {col})"
    
    print("✓ Initial board test passed")


def test_move_parsing():
    """Test move notation parsing."""
    game = CheckersGame()
    
    # Test various move formats
    test_cases = [
        ("e2-e4", (6, 4, 4, 4)),  # from e2 to e4
        ("e2 to e4", (6, 4, 4, 4)),
        ("e2 e4", (6, 4, 4, 4)),
        ("d3-c4", (5, 3, 4, 2)),  # from d3 to c4
        ("a1-b2", (7, 0, 6, 1)),  # from a1 to b2
    ]
    
    for move_str, expected in test_cases:
        result = game.parse_move(move_str)
        assert result is not None, f"Failed to parse: {move_str}"
        assert result['from_row'] == expected[0], f"Wrong from_row for {move_str}"
        assert result['from_col'] == expected[1], f"Wrong from_col for {move_str}"
        assert result['to_row'] == expected[2], f"Wrong to_row for {move_str}"
        assert result['to_col'] == expected[3], f"Wrong to_col for {move_str}"
    
    # Test invalid moves
    invalid_moves = ["", "i9-i10", "a1", "abc-def"]
    for move_str in invalid_moves:
        assert game.parse_move(move_str) is None, f"Should reject: {move_str}"
    
    print("✓ Move parsing test passed")


def test_valid_moves():
    """Test move validation logic."""
    game = CheckersGame()
    
    # Red player should be able to move pieces forward diagonally
    valid_moves = game.get_all_valid_moves()
    assert len(valid_moves) > 0, "Red should have valid moves on first turn"
    
    # Test specific valid move: e2-e3 (one step forward)
    # Actually, let's check what valid moves exist
    initial_positions = set()
    for move in valid_moves:
        initial_positions.add((move['from_row'], move['from_col']))
    
    # Should have moves from row 2 (the third row from top, index 2)
    has_row_2_moves = any(m['from_row'] == 2 for m in valid_moves)
    assert has_row_2_moves, "Red should have moves from row 2"
    
    print("✓ Valid moves test passed")


def test_basic_move_execution():
    """Test basic move execution."""
    game = CheckersGame()
    
    # Get valid moves and use one
    valid_moves = game.get_all_valid_moves()
    assert len(valid_moves) > 0, "Should have valid moves"
    
    # Find a valid non-capture move
    basic_move = None
    for m in valid_moves:
        if not m['capture']:
            basic_move = m
            break
    
    assert basic_move is not None, "Should have a basic move available"
    
    result = game.execute_move(basic_move)
    
    assert result == True, "Move execution should return True"
    assert game.board[basic_move['from_row']][basic_move['from_col']] is None, "Original position should be empty"
    assert game.board[basic_move['to_row']][basic_move['to_col']] == 'r', "New position should have red piece"
    assert game.current_player == 'black', "Turn should switch to black"
    
    print("✓ Basic move execution test passed")


def test_capture_move():
    """Test capture move execution."""
    # Create a custom board for capture testing
    game = CheckersGame()
    game.board = [[None for _ in range(8)] for _ in range(8)]
    
    # Place red piece, black piece to capture, and empty landing spot
    game.board[4][3] = 'r'  # Red piece
    game.board[3][4] = 'b'  # Black piece (to be captured)
    game.board[2][5] = None  # Empty landing spot
    
    game.current_player = 'red'
    game.red_pieces = 1
    game.black_pieces = 1
    
    # Execute capture move
    move = {'from_row': 4, 'from_col': 3, 'to_row': 2, 'to_col': 5, 'capture': (3, 4)}
    game.execute_move(move)
    
    assert game.board[4][3] is None, "Original position should be empty"
    assert game.board[2][5] == 'r', "Landing spot should have red piece"
    assert game.board[3][4] is None, "Captured piece should be removed"
    assert game.black_pieces == 0, "Black pieces count should decrease"
    
    print("✓ Capture move test passed")


def test_kinging():
    """Test king promotion."""
    game = CheckersGame()
    
    # Create a custom board to test kinging
    game.board = [[None for _ in range(8)] for _ in range(8)]
    game.board[6][1] = 'r'  # Red piece near promotion
    game.red_kings = 0
    
    # Execute move that promotes the piece
    move = {'from_row': 6, 'from_col': 1, 'to_row': 7, 'to_col': 0, 'capture': None}
    game.execute_move(move)
    
    assert game.board[7][0] == 'R', "Piece should be promoted to king"
    assert game.red_kings == 1, "Red kings count should increase"
    assert game.current_player == 'black', "Turn should switch"
    
    print("✓ Kinging test passed")


def test_position_conversion():
    """Test position coordinate conversion."""
    game = CheckersGame()
    
    # Test algebraic notation conversion
    test_cases = [
        (0, 0, "a8"),
        (0, 4, "e8"),
        (7, 7, "h1"),
        (2, 4, "e6"),
        (5, 3, "d3"),
    ]
    
    for row, col, expected in test_cases:
        result = game.convert_position(row, col)
        assert result == expected, f"Expected {expected} for ({row}, {col}), got {result}"
    
    print("✓ Position conversion test passed")


def test_invalid_moves():
    """Test that invalid moves are rejected."""
    game = CheckersGame()
    
    # Try to move onto an occupied square
    move = {'from_row': 2, 'from_col': 4, 'to_row': 1, 'to_col': 0, 'capture': None}
    # This position is invalid (white square), but let's test board bounds
    
    # Test out of bounds
    assert not game._is_square_valid(-1, 0), "Negative row should be invalid"
    assert not game._is_square_valid(8, 0), "Row 8 should be invalid"
    assert not game._is_square_valid(0, 8), "Col 8 should be invalid"
    
    # Test white squares (invalid playing squares)
    assert not game._is_square_valid(0, 0), "White square (0,0) should be invalid"
    assert not game._is_square_valid(0, 2), "White square (0,2) should be invalid"
    
    print("✓ Invalid moves test passed")


def run_all_tests():
    """Run all tests."""
    print("Running Checkers game tests...\n")
    
    test_initial_board()
    test_move_parsing()
    test_valid_moves()
    test_basic_move_execution()
    test_capture_move()
    test_kinging()
    test_position_conversion()
    test_invalid_moves()
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()
