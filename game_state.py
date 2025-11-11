"""
Game state management and persistence for Liars Chess.
Handles saving/loading games and managing overall game state.
"""

import json
import os
import time
from typing import Dict, Optional
from datetime import datetime
from chess_engine import ChessBoard, Color
from deception_layer import DeceptionLayer


class GameStateManager:
    def __init__(self, save_directory: str = "saved_games"):
        self.save_directory = save_directory
        self.chess_board = ChessBoard()
        self.deception_layer = DeceptionLayer(self.chess_board)
        self.game_id = None
        self.players = {}  # player_id -> player_info
        self.game_metadata = {}
        
        # Create save directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)
    
    def new_game(self, game_id: str, players: Dict[str, Dict]) -> bool:
        """Start a new game with given players."""
        try:
            self.game_id = game_id
            self.players = players
            self.chess_board = ChessBoard()
            self.deception_layer = DeceptionLayer(self.chess_board)
            
            self.game_metadata = {
                'game_id': game_id,
                'created_at': datetime.now().isoformat(),
                'players': players,
                'status': 'active'
            }
            
            # Save initial state
            self.save_game()
            return True
            
        except Exception as e:
            print(f"Error creating new game: {e}")
            return False
    
    def save_game(self, auto_save: bool = True) -> bool:
        """Save current game state to file."""
        if not self.game_id:
            return False
        
        try:
            game_state = {
                'metadata': self.game_metadata,
                'chess_board': self.chess_board.get_board_state(),
                'deception_layer': self.deception_layer.get_game_state(),
                'players': self.players,
                'saved_at': datetime.now().isoformat(),
                'auto_save': auto_save
            }
            
            filename = f"{self.game_id}.json"
            filepath = os.path.join(self.save_directory, filename)
            
            with open(filepath, 'w') as f:
                json.dump(game_state, f, indent=2)
            
            if not auto_save:
                print(f"Game saved to {filepath}")
            
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, game_id: str) -> bool:
        """Load a game from file."""
        try:
            filename = f"{game_id}.json"
            filepath = os.path.join(self.save_directory, filename)
            
            if not os.path.exists(filepath):
                print(f"Save file not found: {filepath}")
                return False
            
            with open(filepath, 'r') as f:
                game_state = json.load(f)
            
            # Restore game state
            self.game_id = game_id
            self.game_metadata = game_state['metadata']
            self.players = game_state['players']
            
            # Restore chess board
            self.chess_board = ChessBoard()
            self.chess_board.load_board_state(game_state['chess_board'])
            
            # Restore deception layer
            self.deception_layer = DeceptionLayer(self.chess_board)
            self.deception_layer.load_game_state(game_state['deception_layer'])
            
            print(f"Game {game_id} loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
    
    def list_saved_games(self) -> Dict[str, Dict]:
        """List all saved games with metadata."""
        saved_games = {}
        
        try:
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json'):
                    game_id = filename[:-5]  # Remove .json extension
                    filepath = os.path.join(self.save_directory, filename)
                    
                    try:
                        with open(filepath, 'r') as f:
                            game_state = json.load(f)
                        
                        saved_games[game_id] = {
                            'metadata': game_state['metadata'],
                            'saved_at': game_state.get('saved_at', 'Unknown'),
                            'file_size': os.path.getsize(filepath),
                            'players': list(game_state['players'].keys())
                        }
                    except Exception as e:
                        print(f"Error reading save file {filename}: {e}")
                        
        except Exception as e:
            print(f"Error listing saved games: {e}")
        
        return saved_games
    
    def delete_saved_game(self, game_id: str) -> bool:
        """Delete a saved game file."""
        try:
            filename = f"{game_id}.json"
            filepath = os.path.join(self.save_directory, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Deleted save file: {filepath}")
                return True
            else:
                print(f"Save file not found: {filepath}")
                return False
                
        except Exception as e:
            print(f"Error deleting save file: {e}")
            return False
    
    def get_game_summary(self) -> Dict:
        """Get a summary of the current game state."""
        if not self.game_id:
            return {}
        
        return {
            'game_id': self.game_id,
            'players': self.players,
            'current_turn': self.chess_board.current_turn.value,
            'move_count': len(self.chess_board.move_history),
            'game_over': self.chess_board.game_over,
            'winner': self.chess_board.winner.value if self.chess_board.winner else None,
            'created_at': self.game_metadata.get('created_at'),
            'status': self.game_metadata.get('status', 'unknown')
        }
    
    def update_player_info(self, player_id: str, info: Dict):
        """Update information for a player."""
        if player_id in self.players:
            self.players[player_id].update(info)
            self.save_game()
    
    def handle_player_disconnect(self, player_id: str):
        """Handle a player disconnection."""
        if player_id in self.players:
            self.players[player_id]['connected'] = False
            self.players[player_id]['disconnected_at'] = datetime.now().isoformat()
            self.save_game()
    
    def handle_player_reconnect(self, player_id: str):
        """Handle a player reconnection."""
        if player_id in self.players:
            self.players[player_id]['connected'] = True
            if 'disconnected_at' in self.players[player_id]:
                del self.players[player_id]['disconnected_at']
            self.save_game()
    
    def end_game(self, winner: Optional[Color] = None, reason: str = "game_over"):
        """End the current game."""
        if self.game_id:
            self.game_metadata['status'] = 'completed'
            self.game_metadata['ended_at'] = datetime.now().isoformat()
            self.game_metadata['end_reason'] = reason
            
            if winner:
                self.game_metadata['winner'] = winner.value
            
            self.save_game(auto_save=False)
    
    def get_player_game_info(self, player_id: str) -> Dict:
        """Get game information specific to a player."""
        if player_id not in self.players:
            return {}
        
        # Check if game is properly initialized
        if not self.game_id or not self.deception_layer:
            return {}
        
        try:
            player_color = Color(self.players[player_id]['color'])
            game_info = self.deception_layer.get_game_info(player_color)
            
            # Add additional player-specific information
            game_info.update({
                'player_id': player_id,
                'player_color': player_color.value,
                'game_id': self.game_id,
                'move_count': len(self.chess_board.move_history),
                'opponent': [pid for pid in self.players.keys() if pid != player_id][0] if len(self.players) > 1 else None
            })
            
            return game_info
        except Exception as e:
            print(f"Error getting player game info: {e}")
            return {}
    
    def make_move(self, player_id: str, from_pos: tuple, to_pos: tuple, claimed_piece: str) -> Dict:
        """Process a move from a player."""
        if player_id not in self.players:
            return {'success': False, 'error': 'Player not found'}
        
        player_color = Color(self.players[player_id]['color'])
        
        if self.chess_board.current_turn != player_color:
            return {'success': False, 'error': 'Not your turn'}
        
        if self.chess_board.game_over:
            return {'success': False, 'error': 'Game is over'}
        
        try:
            from chess_engine import PieceType
            claimed_piece_type = PieceType(claimed_piece)
            
            success = self.deception_layer.make_deceptive_move(
                from_pos, to_pos, claimed_piece_type, player_color
            )
            
            if success:
                self.save_game()  # Auto-save after each move
                return {
                    'success': True,
                    'move': {
                        'from': from_pos,
                        'to': to_pos,
                        'claimed_piece': claimed_piece,
                        'player': player_id
                    }
                }
            else:
                return {'success': False, 'error': 'Invalid move'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def call_liar(self, player_id: str) -> Dict:
        """Process a liar call from a player."""
        if player_id not in self.players:
            return {'success': False, 'error': 'Player not found'}
        
        player_color = Color(self.players[player_id]['color'])
        
        try:
            from deception_layer import LiarCallResult
            result = self.deception_layer.call_liar(player_color)
            
            if result == LiarCallResult.INVALID:
                return {'success': False, 'error': 'Cannot call liar right now'}
            
            self.save_game()  # Auto-save after liar call
            
            return {
                'success': True,
                'result': result.value,
                'message': self._get_liar_call_message(result)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def claim_checkmate(self, player_id: str) -> Dict:
        """Process a checkmate claim from a player."""
        if player_id not in self.players:
            return {'success': False, 'error': 'Player not found'}
        
        player_color = Color(self.players[player_id]['color'])
        
        try:
            is_checkmate = self.deception_layer.claim_checkmate(player_color)
            self.save_game()
            
            return {
                'success': True,
                'is_checkmate': is_checkmate,
                'message': 'Checkmate claimed! Opponent can call liar or accept defeat.'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_liar_call_message(self, result) -> str:
        """Get a descriptive message for liar call result."""
        from deception_layer import LiarCallResult
        
        if result == LiarCallResult.SUCCESSFUL:
            return "Liar call successful! Opponent's piece has been revealed."
        elif result == LiarCallResult.FAILED:
            return "Liar call failed! You lose your next turn."
        else:
            return "Invalid liar call."