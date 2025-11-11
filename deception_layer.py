"""
Deception layer for Liars Chess.
Handles piece visibility, lying mechanics, and liar calling.
"""

from typing import Dict, List, Tuple, Optional, Set
from enum import Enum
from chess_engine import ChessBoard, Piece, PieceType, Color
import copy


class MoveType(Enum):
    NORMAL = "normal"
    LIE = "lie"


class LiarCallResult(Enum):
    SUCCESSFUL = "successful"  # Opponent was lying
    FAILED = "failed"  # Opponent was telling truth
    INVALID = "invalid"  # Can't call liar on this move


class DeceptionMove:
    def __init__(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                 claimed_piece: PieceType, actual_piece: PieceType, 
                 player_color: Color):
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.claimed_piece = claimed_piece
        self.actual_piece = actual_piece
        self.player_color = player_color
        self.is_lie = claimed_piece != actual_piece
        self.timestamp = None
    
    def __str__(self):
        return f"Move from {self.from_pos} to {self.to_pos}, claimed {self.claimed_piece.value}, actual {self.actual_piece.value}"


class DeceptionLayer:
    def __init__(self, chess_board: ChessBoard):
        self.chess_board = chess_board
        self.revealed_pieces: Set[Tuple[int, int]] = set()  # Positions of revealed pieces
        self.last_move: Optional[DeceptionMove] = None
        self.liar_call_available = False
        self.turn_penalties: Dict[Color, int] = {Color.WHITE: 0, Color.BLACK: 0}  # Turns to skip
        self.checkmate_claims: List[Dict] = []  # Track checkmate claims for liar calling
    
    def can_see_piece(self, piece_pos: Tuple[int, int], viewer_color: Color) -> bool:
        """Determine if a player can see what type a piece is."""
        piece = self.chess_board.get_piece(piece_pos[0], piece_pos[1])
        if not piece:
            return False
        
        # Players can always see their own pieces
        if piece.color == viewer_color:
            return True
        
        # Can see enemy pieces that have been revealed
        if piece_pos in self.revealed_pieces or piece.is_revealed:
            return True
        
        return False
    
    def get_visible_board(self, viewer_color: Color) -> List[List[Optional[str]]]:
        """Get board representation from a player's perspective."""
        visible_board = []
        
        for row in range(8):
            board_row = []
            for col in range(8):
                piece = self.chess_board.get_piece(row, col)
                if not piece:
                    board_row.append(None)
                elif self.can_see_piece((row, col), viewer_color):
                    board_row.append(str(piece))
                else:
                    # Show as unknown enemy piece
                    enemy_symbol = "●" if piece.color == Color.BLACK else "○"
                    board_row.append(enemy_symbol)
            visible_board.append(board_row)
        
        return visible_board
    
    def validate_claimed_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                            claimed_piece: PieceType, player_color: Color) -> bool:
        """Validate if a claimed move is legal for the claimed piece type."""
        # Create a temporary piece of the claimed type to check if move is legal
        temp_piece = Piece(claimed_piece, player_color, from_pos)
        temp_piece.has_moved = self.chess_board.get_piece(from_pos[0], from_pos[1]).has_moved
        
        # Temporarily replace the piece to check legal moves
        original_piece = self.chess_board.get_piece(from_pos[0], from_pos[1])
        self.chess_board.set_piece(from_pos[0], from_pos[1], temp_piece)
        
        legal_moves = self.chess_board.get_legal_moves(temp_piece)
        is_valid = to_pos in legal_moves
        
        # Restore original piece
        self.chess_board.set_piece(from_pos[0], from_pos[1], original_piece)
        
        return is_valid
    
    def make_deceptive_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], 
                          claimed_piece: PieceType, player_color: Color) -> bool:
        """Make a move with potential deception."""
        piece = self.chess_board.get_piece(from_pos[0], from_pos[1])
        if not piece or piece.color != player_color:
            return False
        
        # Check if player is skipping turns due to penalty
        if self.turn_penalties[player_color] > 0:
            self.turn_penalties[player_color] -= 1
            self.chess_board.current_turn = Color.BLACK if player_color == Color.WHITE else Color.WHITE
            return False
        
        # Validate the claimed move is legal for the claimed piece type
        if not self.validate_claimed_move(from_pos, to_pos, claimed_piece, player_color):
            return False
        
        # Create deception move record
        deception_move = DeceptionMove(from_pos, to_pos, claimed_piece, piece.type, player_color)
        
        # Make the actual move on the chess board
        if self.chess_board.make_move(from_pos, to_pos):
            self.last_move = deception_move
            self.liar_call_available = True
            return True
        
        return False
    
    def call_liar(self, calling_player: Color) -> LiarCallResult:
        """Handle a liar call on the last move."""
        if not self.liar_call_available or not self.last_move:
            return LiarCallResult.INVALID
        
        self.liar_call_available = False
        
        if self.last_move.is_lie:
            # Successful liar call - reveal the lying piece
            piece_pos = self.last_move.to_pos
            self.revealed_pieces.add(piece_pos)
            piece = self.chess_board.get_piece(piece_pos[0], piece_pos[1])
            if piece:
                piece.is_revealed = True
            return LiarCallResult.SUCCESSFUL
        else:
            # Failed liar call - calling player loses next turn
            self.turn_penalties[calling_player] = 1
            return LiarCallResult.FAILED
    
    def claim_checkmate(self, claiming_player: Color) -> bool:
        """Handle a checkmate claim."""
        enemy_color = Color.BLACK if claiming_player == Color.WHITE else Color.WHITE
        
        # Record the checkmate claim
        claim = {
            'player': claiming_player,
            'turn': len(self.chess_board.move_history),
            'board_state': self.chess_board.get_board_state()
        }
        self.checkmate_claims.append(claim)
        
        # Check if it's actually checkmate
        return self.chess_board.is_checkmate(enemy_color)
    
    def call_liar_on_checkmate(self, calling_player: Color) -> LiarCallResult:
        """Handle liar call on checkmate claim."""
        if not self.checkmate_claims:
            return LiarCallResult.INVALID
        
        last_claim = self.checkmate_claims[-1]
        claiming_player = last_claim['player']
        enemy_color = Color.BLACK if claiming_player == Color.WHITE else Color.WHITE
        
        # Check if the checkmate claim was true
        is_actually_checkmate = self.chess_board.is_checkmate(enemy_color)
        
        if not is_actually_checkmate:
            # Checkmate claim was a lie - reveal all pieces of the lying player
            self.reveal_all_pieces(claiming_player)
            return LiarCallResult.SUCCESSFUL
        else:
            # Checkmate claim was true - calling player loses immediately
            self.chess_board.game_over = True
            self.chess_board.winner = claiming_player
            return LiarCallResult.FAILED
    
    def reveal_all_pieces(self, player_color: Color):
        """Reveal all pieces of a player (penalty for lying about checkmate)."""
        for row in range(8):
            for col in range(8):
                piece = self.chess_board.get_piece(row, col)
                if piece and piece.color == player_color:
                    self.revealed_pieces.add((row, col))
                    piece.is_revealed = True
    
    def get_move_options(self, piece_pos: Tuple[int, int], player_color: Color) -> Dict[PieceType, List[Tuple[int, int]]]:
        """Get all possible moves for each piece type from a position."""
        piece = self.chess_board.get_piece(piece_pos[0], piece_pos[1])
        if not piece or piece.color != player_color:
            return {}
        
        move_options = {}
        
        # Check moves for each piece type
        for piece_type in PieceType:
            temp_piece = Piece(piece_type, player_color, piece_pos)
            temp_piece.has_moved = piece.has_moved
            
            # Temporarily replace piece
            self.chess_board.set_piece(piece_pos[0], piece_pos[1], temp_piece)
            legal_moves = self.chess_board.get_legal_moves(temp_piece)
            
            if legal_moves:
                move_options[piece_type] = legal_moves
            
            # Restore original piece
            self.chess_board.set_piece(piece_pos[0], piece_pos[1], piece)
        
        return move_options
    
    def get_game_state(self) -> Dict:
        """Get current deception layer state for serialization."""
        return {
            'revealed_pieces': list(self.revealed_pieces),
            'last_move': {
                'from_pos': self.last_move.from_pos,
                'to_pos': self.last_move.to_pos,
                'claimed_piece': self.last_move.claimed_piece.value,
                'actual_piece': self.last_move.actual_piece.value,
                'player_color': self.last_move.player_color.value,
                'is_lie': self.last_move.is_lie
            } if self.last_move else None,
            'liar_call_available': self.liar_call_available,
            'turn_penalties': {color.value: penalty for color, penalty in self.turn_penalties.items()},
            'checkmate_claims': self.checkmate_claims
        }
    
    def load_game_state(self, state: Dict):
        """Load deception layer state from serialized data."""
        self.revealed_pieces = set(tuple(pos) for pos in state['revealed_pieces'])
        
        if state['last_move']:
            move_data = state['last_move']
            self.last_move = DeceptionMove(
                tuple(move_data['from_pos']),
                tuple(move_data['to_pos']),
                PieceType(move_data['claimed_piece']),
                PieceType(move_data['actual_piece']),
                Color(move_data['player_color'])
            )
        else:
            self.last_move = None
        
        self.liar_call_available = state['liar_call_available']
        self.turn_penalties = {Color(color): penalty for color, penalty in state['turn_penalties'].items()}
        self.checkmate_claims = state['checkmate_claims']
    
    def get_game_info(self, player_color: Color) -> Dict:
        """Get game information visible to a specific player."""
        return {
            'visible_board': self.get_visible_board(player_color),
            'current_turn': self.chess_board.current_turn.value,
            'can_call_liar': self.liar_call_available and self.chess_board.current_turn == player_color,
            'turn_penalty': self.turn_penalties[player_color],
            'game_over': self.chess_board.game_over,
            'winner': self.chess_board.winner.value if self.chess_board.winner else None,
            'in_check': self.chess_board.is_in_check(player_color),
            'last_move_summary': f"Opponent moved from {self.last_move.from_pos} to {self.last_move.to_pos} as {self.last_move.claimed_piece.value}" if self.last_move and self.last_move.player_color != player_color else None
        }