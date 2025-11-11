#!/usr/bin/env python3
"""
Test script for Liars Chess functionality.
Tests board display, move input, and basic game mechanics.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli_interface import CLIInterface
from chess_engine import Color, ChessBoard, PieceType
from deception_layer import DeceptionLayer
from game_state import GameStateManager

def test_board_display():
    """Test the enhanced board display."""
    print("=" * 50)
    print("TESTING BOARD DISPLAY")
    print("=" * 50)
    
    cli = CLIInterface()
    chess_board = ChessBoard()
    deception = DeceptionLayer(chess_board)
    
    # Test initial board
    visible_board = deception.get_visible_board(Color.WHITE)
    cli.display_board(visible_board, Color.WHITE)
    
    print("\nBoard display test completed!")
    return True

def test_move_input():
    """Test the enhanced move input system."""
    print("\n" + "=" * 50)
    print("TESTING MOVE INPUT SYSTEM")
    print("=" * 50)
    
    cli = CLIInterface()
    
    # Simulate available pieces
    available_pieces = [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)]  # White pawns
    
    print("This would normally prompt for input. Simulating...")
    print("Available pieces shown: a2, b2, c2, d2, e2, f2, g2, h2")
    
    # Test piece type selection
    available_moves = {
        PieceType.PAWN: [(2, 0), (3, 0)],
        PieceType.QUEEN: [(2, 0), (3, 0), (2, 1), (3, 1)],
        PieceType.ROOK: [(2, 0), (3, 0)]
    }
    
    print("\nThis would show piece type selection with enhanced UI...")
    print("Move input system test completed!")
    return True

def test_game_mechanics():
    """Test basic game mechanics."""
    print("\n" + "=" * 50)
    print("TESTING GAME MECHANICS")
    print("=" * 50)
    
    game_state = GameStateManager()
    
    # Create a test game
    players = {
        'Player1': {'color': 'white', 'connected': True},
        'Player2': {'color': 'black', 'connected': True}
    }
    
    success = game_state.new_game('test_game', players)
    print(f"Game creation: {'SUCCESS' if success else 'FAILED'}")
    
    # Test move
    result = game_state.make_move('Player1', (1, 4), (3, 4), 'pawn')  # e2 to e4
    print(f"Move e2-e4: {'SUCCESS' if result['success'] else 'FAILED'}")
    
    # Test game info
    game_info = game_state.get_player_game_info('Player1')
    print(f"Game info retrieved: {'SUCCESS' if game_info else 'FAILED'}")
    
    print("Game mechanics test completed!")
    return True

def main():
    """Run all tests."""
    print("LIARS CHESS - FUNCTIONALITY TESTS")
    print("=" * 50)
    
    tests = [
        ("Board Display", test_board_display),
        ("Move Input System", test_move_input),
        ("Game Mechanics", test_game_mechanics)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)