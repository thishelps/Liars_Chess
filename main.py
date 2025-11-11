"""
Main entry point for Liars Chess.
Coordinates all game components and handles the main game loop.
"""

import sys
import threading
import time
import uuid
from typing import Optional, Dict
from chess_engine import Color, PieceType
from deception_layer import LiarCallResult
from network_manager import GameServer, GameClient, MessageType
from game_state import GameStateManager
from cli_interface import CLIInterface


class LiarsChessGame:
    def __init__(self):
        self.cli = CLIInterface()
        self.game_state = GameStateManager()
        self.server = None
        self.client = None
        self.is_server = False
        self.running = False
        self.player_id = None
        self.player_color = None
        
    def main_menu(self):
        """Display main menu and handle user choice."""
        while True:
            self.cli.clear_screen()
            self.cli.display_title()
            
            options = [
                "Host a new game (Server)",
                "Join a game (Client)",
                "Load saved game",
                "View saved games",
                "Exit"
            ]
            
            choice = self.cli.get_menu_choice(options, "Main Menu")
            
            if choice is None or choice == 4:  # Exit
                self.cli.display_info("Thanks for playing Liars Chess!")
                sys.exit(0)
            elif choice == 0:  # Host game
                self.host_game()
            elif choice == 1:  # Join game
                self.join_game()
            elif choice == 2:  # Load saved game
                self.load_game_menu()
            elif choice == 3:  # View saved games
                self.view_saved_games()
    
    def host_game(self):
        """Host a new game as server."""
        self.cli.clear_screen()
        self.cli.display_info("Setting up game server...")
        
        # Get server configuration
        port = self.cli.get_text_input("Server port", "12000")
        if port is None:
            return
        
        try:
            port = int(port)
        except ValueError:
            self.cli.display_error("Invalid port number")
            self.cli.wait_for_enter()
            return
        
        player_name = self.cli.get_text_input("Your player name", "Host")
        if player_name is None:
            return
        
        # Start server
        self.server = GameServer(port=port)
        self.is_server = True
        
        # Register server callbacks
        self.server.register_callback('game_start', self.on_game_start)
        self.server.register_callback('player_disconnect', self.on_player_disconnect)
        self.server.register_callback('player_reconnect', self.on_player_reconnect)
        self.server.register_callback(MessageType.MOVE.value, self.on_move_received)
        self.server.register_callback(MessageType.LIAR_CALL.value, self.on_liar_call_received)
        self.server.register_callback(MessageType.CHECKMATE_CLAIM.value, self.on_checkmate_claim_received)
        
        # Start server in background thread
        server_thread = threading.Thread(target=self.server.start_server, daemon=True)
        server_thread.start()
        
        # Connect as client to own server
        time.sleep(1)  # Give server time to start
        self.client = GameClient(port=port)
        
        if self.client.connect(player_name):
            self.player_id = self.client.player_id
            self.player_color = self.client.color
            
            # Register client callbacks
            self.client.register_callback(MessageType.GAME_STATE.value, self.on_game_state_received)
            self.client.register_callback(MessageType.ERROR.value, self.on_error_received)
            
            self.cli.display_success(f"Server started! Waiting for opponent...")
            self.cli.display_info(f"Other players can connect to: localhost:{port}")
            self.cli.display_player_info(self.player_id, self.player_color)
            
            self.wait_for_game_start()
        else:
            self.cli.display_error("Failed to connect to own server")
            self.cli.wait_for_enter()
    
    def join_game(self):
        """Join an existing game as client."""
        self.cli.clear_screen()
        self.cli.display_info("Joining game...")
        
        # Get connection details
        host = self.cli.get_text_input("Server address", "localhost")
        if host is None:
            return
        
        port = self.cli.get_text_input("Server port", "12000")
        if port is None:
            return
        
        try:
            port = int(port)
        except ValueError:
            self.cli.display_error("Invalid port number")
            self.cli.wait_for_enter()
            return
        
        player_name = self.cli.get_text_input("Your player name", "Player")
        if player_name is None:
            return
        
        # Connect to server
        self.client = GameClient(host, port)
        
        if self.client.connect(player_name):
            self.player_id = self.client.player_id
            self.player_color = self.client.color
            
            # Register client callbacks
            self.client.register_callback(MessageType.GAME_STATE.value, self.on_game_state_received)
            self.client.register_callback(MessageType.ERROR.value, self.on_error_received)
            
            self.cli.display_success("Connected to server!")
            self.cli.display_player_info(self.player_id, self.player_color)
            
            self.wait_for_game_start()
        else:
            self.cli.display_error("Failed to connect to server")
            self.cli.wait_for_enter()
    
    def wait_for_game_start(self):
        """Wait for game to start with enough players."""
        self.cli.display_info("Waiting for game to start...")
        
        while not hasattr(self, 'game_started') or not self.game_started:
            time.sleep(1)
        
        self.start_game_loop()
    
    def start_game_loop(self):
        """Start the main game loop."""
        self.running = True
        
        while self.running:
            try:
                # Get current game state
                game_info = self.game_state.get_player_game_info(self.player_id)
                
                # Display game state
                self.cli.clear_screen()
                self.cli.display_title()
                self.cli.display_player_info(self.player_id, self.player_color, game_info.get('opponent'))
                self.cli.display_board(game_info['visible_board'], self.player_color)
                self.cli.display_game_status(game_info)
                
                # Check if game is over
                if game_info.get('game_over'):
                    winner = game_info.get('winner', 'Unknown')
                    self.cli.display_info(f"Game Over! Winner: {winner}")
                    self.cli.wait_for_enter("Press Enter to return to main menu...")
                    break
                
                # Check if it's player's turn
                if game_info['current_turn'] != self.player_color.value:
                    self.cli.display_info("Waiting for opponent's move...")
                    time.sleep(2)
                    continue
                
                # Check for turn penalty
                if game_info.get('turn_penalty', 0) > 0:
                    self.cli.display_warning("You must skip this turn due to a failed liar call")
                    time.sleep(3)
                    continue
                
                # Get player input
                from_pos, to_pos = self.cli.get_move_input()
                
                if from_pos is None:  # Quit
                    break
                elif from_pos == 'liar':  # Call liar
                    self.handle_liar_call()
                elif from_pos == 'checkmate':  # Claim checkmate
                    self.handle_checkmate_claim()
                else:  # Regular move
                    self.handle_move(from_pos, to_pos)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.cli.display_error(f"Game error: {e}")
                time.sleep(2)
        
        self.cleanup()
    
    def handle_move(self, from_pos: tuple, to_pos: tuple):
        """Handle a move attempt."""
        # Get available moves for the piece
        piece = self.game_state.chess_board.get_piece(from_pos[0], from_pos[1])
        if not piece or piece.color != self.player_color:
            self.cli.display_error("Invalid piece selection")
            self.cli.wait_for_enter()
            return
        
        # Get move options for different piece types
        move_options = self.game_state.deception_layer.get_move_options(from_pos, self.player_color)
        
        # Filter options that include the target position
        valid_options = {pt: moves for pt, moves in move_options.items() if to_pos in moves}
        
        if not valid_options:
            self.cli.display_error("No piece type can make that move")
            self.cli.wait_for_enter()
            return
        
        # Let player choose piece type to claim
        claimed_piece_type = self.cli.get_piece_type_input(valid_options)
        if claimed_piece_type is None:
            return
        
        # Send move to server/game state
        if self.client:
            success = self.client.make_move(from_pos, to_pos, claimed_piece_type.value)
            if not success:
                self.cli.display_error("Failed to send move")
        else:
            result = self.game_state.make_move(self.player_id, from_pos, to_pos, claimed_piece_type.value)
            self.cli.display_move_result(result['success'], result.get('error', ''))
        
        time.sleep(1)
    
    def handle_liar_call(self):
        """Handle a liar call."""
        if self.client:
            success = self.client.call_liar()
            if not success:
                self.cli.display_error("Failed to call liar")
        else:
            result = self.game_state.call_liar(self.player_id)
            if result['success']:
                self.cli.display_liar_call_result(result['result'], result['message'])
            else:
                self.cli.display_error(result['error'])
        
        self.cli.wait_for_enter()
    
    def handle_checkmate_claim(self):
        """Handle a checkmate claim."""
        if not self.cli.confirm_action("Are you sure you want to claim checkmate?"):
            return
        
        if self.client:
            success = self.client.claim_checkmate()
            if not success:
                self.cli.display_error("Failed to claim checkmate")
        else:
            result = self.game_state.claim_checkmate(self.player_id)
            if result['success']:
                self.cli.display_success(result['message'])
            else:
                self.cli.display_error(result['error'])
        
        self.cli.wait_for_enter()
    
    def load_game_menu(self):
        """Display menu for loading saved games."""
        saved_games = self.game_state.list_saved_games()
        
        if not saved_games:
            self.cli.display_warning("No saved games found")
            self.cli.wait_for_enter()
            return
        
        self.cli.clear_screen()
        self.cli.display_saved_games(saved_games)
        
        game_id = self.cli.get_text_input("Enter game ID to load")
        if game_id and game_id in saved_games:
            if self.game_state.load_game(game_id):
                self.cli.display_success(f"Game {game_id} loaded successfully!")
                # TODO: Resume multiplayer game if needed
            else:
                self.cli.display_error("Failed to load game")
        
        self.cli.wait_for_enter()
    
    def view_saved_games(self):
        """View all saved games."""
        self.cli.clear_screen()
        saved_games = self.game_state.list_saved_games()
        self.cli.display_saved_games(saved_games)
        self.cli.wait_for_enter()
    
    def cleanup(self):
        """Clean up resources."""
        self.running = False
        
        if self.client:
            self.client.disconnect()
        
        if self.server:
            self.server.stop_server()
    
    # Network event handlers
    def on_game_start(self):
        """Handle game start event."""
        game_id = str(uuid.uuid4())
        players = {}
        
        for player_id in self.server.get_connected_players():
            color = self.server.get_player_color(player_id)
            players[player_id] = {
                'color': color.value,
                'connected': True
            }
        
        self.game_state.new_game(game_id, players)
        self.game_started = True
        
        # Broadcast game start
        self.server.broadcast_message({
            'type': MessageType.GAME_STATE.value,
            'game_started': True
        })
    
    def on_player_disconnect(self, player_id: str):
        """Handle player disconnection."""
        self.game_state.handle_player_disconnect(player_id)
    
    def on_player_reconnect(self, player_id: str):
        """Handle player reconnection."""
        self.game_state.handle_player_reconnect(player_id)
    
    def on_move_received(self, player_id: str, message: Dict):
        """Handle move received from client."""
        result = self.game_state.make_move(
            player_id,
            tuple(message['from_pos']),
            tuple(message['to_pos']),
            message['claimed_piece']
        )
        
        # Broadcast move result to all players
        self.server.broadcast_message({
            'type': MessageType.MOVE.value,
            'success': result['success'],
            'player': player_id,
            'move': result.get('move'),
            'error': result.get('error')
        })
    
    def on_liar_call_received(self, player_id: str, message: Dict):
        """Handle liar call from client."""
        result = self.game_state.call_liar(player_id)
        
        self.server.broadcast_message({
            'type': MessageType.LIAR_CALL.value,
            'player': player_id,
            'success': result['success'],
            'result': result.get('result'),
            'message': result.get('message'),
            'error': result.get('error')
        })
    
    def on_checkmate_claim_received(self, player_id: str, message: Dict):
        """Handle checkmate claim from client."""
        result = self.game_state.claim_checkmate(player_id)
        
        self.server.broadcast_message({
            'type': MessageType.CHECKMATE_CLAIM.value,
            'player': player_id,
            'success': result['success'],
            'is_checkmate': result.get('is_checkmate'),
            'message': result.get('message'),
            'error': result.get('error')
        })
    
    def on_game_state_received(self, message: Dict):
        """Handle game state update from server."""
        if message.get('game_started'):
            self.game_started = True
    
    def on_error_received(self, message: Dict):
        """Handle error message from server."""
        self.cli.display_error(message.get('message', 'Unknown error'))


def main():
    """Main entry point."""
    try:
        game = LiarsChessGame()
        game.main_menu()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()