#!/usr/bin/env python3
"""
Demo script showing Liars Chess gameplay.
"""

from chess_engine import ChessBoard, Color, PieceType
from deception_layer import DeceptionLayer, LiarCallResult
from cli_interface import CLIInterface
import time


def demo_game():
    """Demonstrate a sample game of Liars Chess."""
    cli = CLIInterface()
    board = ChessBoard()
    deception = DeceptionLayer(board)
    
    cli.clear_screen()
    cli.display_title()
    
    print("🎭 Welcome to the Liars Chess Demo!")
    print("This demo shows how deception works in the game.\n")
    
    # Show initial board from White's perspective
    print("=== Initial Board (White's View) ===")
    visible_board = deception.get_visible_board(Color.WHITE)
    cli.display_board(visible_board, Color.WHITE)
    
    input("\nPress Enter to continue...")
    
    # White makes a normal pawn move
    print("\n=== White's Turn ===")
    print("White moves pawn from e2 to e4 (telling the truth)")
    success = deception.make_deceptive_move((6, 4), (4, 4), PieceType.PAWN, Color.WHITE)
    print(f"Move successful: {success}")
    
    # Show board from Black's perspective
    print("\n=== Board from Black's View ===")
    visible_board = deception.get_visible_board(Color.BLACK)
    cli.display_board(visible_board, Color.BLACK)
    
    input("\nPress Enter to continue...")
    
    # Black makes a lying move
    print("\n=== Black's Turn ===")
    print("Black moves pawn from d7 to d5, but CLAIMS it's a QUEEN move!")
    success = deception.make_deceptive_move((1, 3), (3, 3), PieceType.QUEEN, Color.BLACK)
    print(f"Deceptive move successful: {success}")
    print("Black is lying! The piece is actually a pawn, not a queen.")
    
    # Show board from White's perspective
    print("\n=== Board from White's View ===")
    visible_board = deception.get_visible_board(Color.WHITE)
    cli.display_board(visible_board, Color.WHITE)
    
    input("\nPress Enter to continue...")
    
    # White calls liar
    print("\n=== White Calls Liar! ===")
    print("White suspects Black is lying about the queen move...")
    result = deception.call_liar(Color.WHITE)
    
    if result == LiarCallResult.SUCCESSFUL:
        print("🎯 Liar call SUCCESSFUL! Black was indeed lying!")
        print("The 'queen' is revealed to be a pawn and stays revealed for the rest of the game.")
    elif result == LiarCallResult.FAILED:
        print("💥 Liar call FAILED! Black was telling the truth.")
        print("White loses their next turn as penalty.")
    
    # Show final board state
    print("\n=== Final Board State ===")
    print("Notice how the revealed piece is now visible to White:")
    visible_board = deception.get_visible_board(Color.WHITE)
    cli.display_board(visible_board, Color.WHITE)
    
    print("\n🎭 Demo Complete!")
    print("Key takeaways:")
    print("• Players can lie about their piece movements")
    print("• Opponents can call 'liar' to reveal the truth")
    print("• Successful liar calls reveal the lying piece permanently")
    print("• Failed liar calls result in losing a turn")
    print("• The psychological element adds a whole new dimension to chess!")


def main():
    """Run the demo."""
    try:
        demo_game()
    except KeyboardInterrupt:
        print("\nDemo interrupted. Thanks for watching!")
    except Exception as e:
        print(f"Demo error: {e}")


if __name__ == "__main__":
    main()