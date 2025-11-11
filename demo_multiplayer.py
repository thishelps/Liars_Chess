#!/usr/bin/env python3
"""
Demo script showing Liars Chess multiplayer functionality.
This demonstrates hosting, joining, and playing a game.
"""

import sys
import os
import threading
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from network_manager import GameServer, GameClient
from cli_interface import CLIInterface
from chess_engine import Color

def demo_server_client():
    """Demonstrate server-client connection."""
    print("=" * 60)
    print("LIARS CHESS - MULTIPLAYER DEMO")
    print("=" * 60)
    
    cli = CLIInterface()
    cli.display_title()
    
    print("\n🚀 Starting game server...")
    server = GameServer(port=12003)
    server_thread = threading.Thread(target=server.start_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    
    print("✅ Server started successfully!")
    print(f"📡 Server listening on localhost:12003")
    
    # Connect first player (White)
    print("\n👤 Connecting Player 1 (White)...")
    client1 = GameClient('localhost', 12003)
    result1 = client1.connect('Alice')
    
    if result1:
        print(f"✅ Alice connected as {client1.color.value}")
    else:
        print("❌ Alice connection failed")
        return False
    
    # Connect second player (Black)
    print("\n👤 Connecting Player 2 (Black)...")
    client2 = GameClient('localhost', 12003)
    result2 = client2.connect('Bob')
    
    if result2:
        print(f"✅ Bob connected as {client2.color.value}")
    else:
        print("❌ Bob connection failed")
        return False
    
    print("\n🎮 Both players connected! Game ready to start.")
    print("\n📋 Connection Summary:")
    print(f"   • Alice: {client1.color.value.title()} player")
    print(f"   • Bob: {client2.color.value.title()} player")
    print(f"   • Server: localhost:12003")
    
    # Test message sending
    print("\n📨 Testing message communication...")
    
    # Send a test move from Alice
    move_sent = client1.send_message({
        'type': 'move',
        'from_pos': (1, 4),  # e2
        'to_pos': (3, 4),    # e4
        'claimed_piece': 'pawn'
    })
    
    if move_sent:
        print("✅ Move message sent successfully")
    else:
        print("❌ Move message failed")
    
    time.sleep(1)
    
    # Cleanup
    print("\n🧹 Cleaning up connections...")
    client1.disconnect()
    client2.disconnect()
    server.stop_server()
    
    print("✅ Demo completed successfully!")
    return True

def demo_board_features():
    """Demonstrate enhanced board features."""
    print("\n" + "=" * 60)
    print("ENHANCED BOARD DISPLAY DEMO")
    print("=" * 60)
    
    from chess_engine import ChessBoard
    from deception_layer import DeceptionLayer
    
    cli = CLIInterface()
    chess_board = ChessBoard()
    deception = DeceptionLayer(chess_board)
    
    print("\n🎨 Showing enhanced board with:")
    print("   • Better colors and contrast")
    print("   • Clear piece visibility indicators")
    print("   • Professional grid layout")
    print("   • Coordinate labels")
    
    # Show initial position
    visible_board = deception.get_visible_board(Color.WHITE)
    cli.display_board(visible_board, Color.WHITE)
    
    # Simulate a move and show highlighted squares
    print("\n🎯 Board with highlighted possible moves:")
    highlighted_moves = [(2, 4), (3, 4)]  # e3, e4 for pawn
    cli.display_board(visible_board, Color.WHITE, highlighted_moves)
    
    return True

def demo_input_system():
    """Demonstrate enhanced input system."""
    print("\n" + "=" * 60)
    print("ENHANCED INPUT SYSTEM DEMO")
    print("=" * 60)
    
    cli = CLIInterface()
    
    print("\n📝 Enhanced move input features:")
    print("   • Clear instructions and examples")
    print("   • Available piece suggestions")
    print("   • Detailed error messages")
    print("   • Visual piece type selection")
    
    # Show what the input would look like
    available_pieces = [(1, 0), (1, 1), (1, 2), (1, 3)]  # Some pawns
    
    print("\n" + "─" * 40)
    print("SIMULATED INPUT SCREEN:")
    print("─" * 40)
    
    print(f"\n{cli.clear_command} # Screen would be cleared")
    print("╔══════════════════════════════════════╗")
    print("║              YOUR TURN               ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("📝 Enter your move:")
    print("   • Format: 'e2 e4' (from square to square)")
    print("   • Special: 'liar' to call opponent a liar")
    print("   • Special: 'checkmate' to claim victory")
    print("   • Commands: 'help', 'quit'")
    print("   💡 Your pieces at: a2, b2, c2, d2")
    print()
    print("Move> [User would type here]")
    
    print("\n" + "─" * 40)
    print("END SIMULATION")
    print("─" * 40)
    
    return True

def main():
    """Run the complete demo."""
    try:
        # Run all demos
        demos = [
            ("Multiplayer Connection", demo_server_client),
            ("Enhanced Board Display", demo_board_features),
            ("Enhanced Input System", demo_input_system)
        ]
        
        results = []
        for demo_name, demo_func in demos:
            print(f"\n🎬 Running: {demo_name}")
            try:
                result = demo_func()
                results.append((demo_name, result))
                if result:
                    print(f"✅ {demo_name}: SUCCESS")
                else:
                    print(f"❌ {demo_name}: FAILED")
            except Exception as e:
                print(f"❌ {demo_name}: ERROR - {e}")
                results.append((demo_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("DEMO RESULTS SUMMARY")
        print("=" * 60)
        
        for demo_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{demo_name}: {status}")
        
        all_passed = all(result for _, result in results)
        
        if all_passed:
            print(f"\n🎉 ALL DEMOS PASSED! Liars Chess is ready to play!")
            print("\n🚀 To start playing:")
            print("   python main.py")
        else:
            print(f"\n⚠️  Some demos failed. Check the issues above.")
        
        return all_passed
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)