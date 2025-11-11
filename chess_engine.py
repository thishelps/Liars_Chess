"""
Core chess engine for Liars Chess.
Handles standard chess rules, piece movements, and board logic.
"""

from enum import Enum
from typing import List, Tuple, Optional, Dict
import copy


class PieceType(Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"


class Color(Enum):
    WHITE = "white"
    BLACK = "black"


class Piece:
    def __init__(self, piece_type: PieceType, color: Color, position: Tuple[int, int]):
        self.type = piece_type
        self.color = color
        self.position = position
        self.has_moved = False
        self.is_revealed = False  # For liar mechanics
    
    def __str__(self):
        symbols = {
            (PieceType.KING, Color.WHITE): "♔",
            (PieceType.QUEEN, Color.WHITE): "♕",
            (PieceType.ROOK, Color.WHITE): "♖",
            (PieceType.BISHOP, Color.WHITE): "♗",
            (PieceType.KNIGHT, Color.WHITE): "♘",
            (PieceType.PAWN, Color.WHITE): "♙",
            (PieceType.KING, Color.BLACK): "♚",
            (PieceType.QUEEN, Color.BLACK): "♛",
            (PieceType.ROOK, Color.BLACK): "♜",
            (PieceType.BISHOP, Color.BLACK): "♝",
            (PieceType.KNIGHT, Color.BLACK): "♞",
            (PieceType.PAWN, Color.BLACK): "♟",
        }
        return symbols.get((self.type, self.color), "?")


class ChessBoard:
    def __init__(self):
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = Color.WHITE
        self.game_over = False
        self.winner = None
        self.move_history = []
        self.setup_initial_position()
    
    def setup_initial_position(self):
        """Set up the standard chess starting position."""
        # Black pieces (top of board)
        piece_order = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
                      PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK]
        
        for col in range(8):
            # Black back rank
            self.board[0][col] = Piece(piece_order[col], Color.BLACK, (0, col))
            # Black pawns
            self.board[1][col] = Piece(PieceType.PAWN, Color.BLACK, (1, col))
            # White pawns
            self.board[6][col] = Piece(PieceType.PAWN, Color.WHITE, (6, col))
            # White back rank
            self.board[7][col] = Piece(piece_order[col], Color.WHITE, (7, col))
    
    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """Get piece at given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None
    
    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        """Set piece at given position."""
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece
            if piece:
                piece.position = (row, col)
    
    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if position is within board bounds."""
        return 0 <= row < 8 and 0 <= col < 8
    
    def get_legal_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get all legal moves for a piece based on chess rules."""
        if not piece:
            return []
        
        moves = []
        row, col = piece.position
        
        if piece.type == PieceType.PAWN:
            moves = self._get_pawn_moves(piece)
        elif piece.type == PieceType.ROOK:
            moves = self._get_rook_moves(piece)
        elif piece.type == PieceType.KNIGHT:
            moves = self._get_knight_moves(piece)
        elif piece.type == PieceType.BISHOP:
            moves = self._get_bishop_moves(piece)
        elif piece.type == PieceType.QUEEN:
            moves = self._get_queen_moves(piece)
        elif piece.type == PieceType.KING:
            moves = self._get_king_moves(piece)
        
        # Filter out moves that would put own king in check
        legal_moves = []
        for move in moves:
            if self._is_legal_move(piece, move):
                legal_moves.append(move)
        
        return legal_moves
    
    def _get_pawn_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get pawn moves."""
        moves = []
        row, col = piece.position
        direction = -1 if piece.color == Color.WHITE else 1
        
        # Forward move
        new_row = row + direction
        if self.is_valid_position(new_row, col) and not self.get_piece(new_row, col):
            moves.append((new_row, col))
            
            # Double move from starting position
            if not piece.has_moved:
                new_row = row + 2 * direction
                if self.is_valid_position(new_row, col) and not self.get_piece(new_row, col):
                    moves.append((new_row, col))
        
        # Diagonal captures
        for dc in [-1, 1]:
            new_row, new_col = row + direction, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if target and target.color != piece.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_rook_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get rook moves."""
        moves = []
        row, col = piece.position
        
        # Horizontal and vertical directions
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if not self.is_valid_position(new_row, new_col):
                    break
                
                target = self.get_piece(new_row, new_col)
                if target:
                    if target.color != piece.color:
                        moves.append((new_row, new_col))
                    break
                else:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_knight_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get knight moves."""
        moves = []
        row, col = piece.position
        
        knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if not target or target.color != piece.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_bishop_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get bishop moves."""
        moves = []
        row, col = piece.position
        
        # Diagonal directions
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if not self.is_valid_position(new_row, new_col):
                    break
                
                target = self.get_piece(new_row, new_col)
                if target:
                    if target.color != piece.color:
                        moves.append((new_row, new_col))
                    break
                else:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _get_queen_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get queen moves (combination of rook and bishop)."""
        return self._get_rook_moves(piece) + self._get_bishop_moves(piece)
    
    def _get_king_moves(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get king moves."""
        moves = []
        row, col = piece.position
        
        # All adjacent squares
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                     (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid_position(new_row, new_col):
                target = self.get_piece(new_row, new_col)
                if not target or target.color != piece.color:
                    moves.append((new_row, new_col))
        
        return moves
    
    def _is_legal_move(self, piece: Piece, target_pos: Tuple[int, int]) -> bool:
        """Check if move doesn't put own king in check."""
        # Make temporary move
        original_pos = piece.position
        target_piece = self.get_piece(target_pos[0], target_pos[1])
        
        self.set_piece(original_pos[0], original_pos[1], None)
        self.set_piece(target_pos[0], target_pos[1], piece)
        
        # Check if king is in check
        king_safe = not self.is_in_check(piece.color)
        
        # Restore board
        self.set_piece(original_pos[0], original_pos[1], piece)
        self.set_piece(target_pos[0], target_pos[1], target_piece)
        
        return king_safe
    
    def is_in_check(self, color: Color) -> bool:
        """Check if the king of given color is in check."""
        king_pos = self.find_king(color)
        if not king_pos:
            return False
        
        # Check if any enemy piece can attack the king
        enemy_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == enemy_color:
                    if king_pos in self._get_attack_squares(piece):
                        return True
        
        return False
    
    def find_king(self, color: Color) -> Optional[Tuple[int, int]]:
        """Find the king of given color."""
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.type == PieceType.KING and piece.color == color:
                    return (row, col)
        return None
    
    def _get_attack_squares(self, piece: Piece) -> List[Tuple[int, int]]:
        """Get squares that a piece attacks (for check detection)."""
        # Similar to get_legal_moves but doesn't filter for check
        row, col = piece.position
        attacks = []
        
        if piece.type == PieceType.PAWN:
            direction = -1 if piece.color == Color.WHITE else 1
            for dc in [-1, 1]:
                new_row, new_col = row + direction, col + dc
                if self.is_valid_position(new_row, new_col):
                    attacks.append((new_row, new_col))
        else:
            # For other pieces, attack squares are the same as move squares
            # but we need to calculate them without the check filter
            if piece.type == PieceType.ROOK:
                attacks = self._get_rook_moves(piece)
            elif piece.type == PieceType.KNIGHT:
                attacks = self._get_knight_moves(piece)
            elif piece.type == PieceType.BISHOP:
                attacks = self._get_bishop_moves(piece)
            elif piece.type == PieceType.QUEEN:
                attacks = self._get_queen_moves(piece)
            elif piece.type == PieceType.KING:
                attacks = self._get_king_moves(piece)
        
        return attacks
    
    def is_checkmate(self, color: Color) -> bool:
        """Check if the given color is in checkmate."""
        if not self.is_in_check(color):
            return False
        
        # Check if any legal move exists
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    if self.get_legal_moves(piece):
                        return False
        
        return True
    
    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Make a move on the board. Returns True if successful."""
        piece = self.get_piece(from_pos[0], from_pos[1])
        if not piece or piece.color != self.current_turn:
            return False
        
        legal_moves = self.get_legal_moves(piece)
        if to_pos not in legal_moves:
            return False
        
        # Make the move
        captured_piece = self.get_piece(to_pos[0], to_pos[1])
        self.set_piece(from_pos[0], from_pos[1], None)
        self.set_piece(to_pos[0], to_pos[1], piece)
        piece.has_moved = True
        
        # Record move
        self.move_history.append({
            'from': from_pos,
            'to': to_pos,
            'piece': piece.type,
            'captured': captured_piece.type if captured_piece else None,
            'turn': self.current_turn
        })
        
        # Switch turns
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        # Check for checkmate
        if self.is_checkmate(self.current_turn):
            self.game_over = True
            self.winner = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        return True
    
    def make_deceptive_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Make a move without validating against piece's actual legal moves (for deception layer)."""
        piece = self.get_piece(from_pos[0], from_pos[1])
        if not piece or piece.color != self.current_turn:
            return False
        
        # Make the move without legal move validation
        captured_piece = self.get_piece(to_pos[0], to_pos[1])
        self.set_piece(from_pos[0], from_pos[1], None)
        self.set_piece(to_pos[0], to_pos[1], piece)
        piece.has_moved = True
        
        # Record move
        self.move_history.append({
            'from': from_pos,
            'to': to_pos,
            'piece': piece.type,
            'captured': captured_piece.type if captured_piece else None,
            'turn': self.current_turn
        })
        
        # Switch turns
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        # Check for checkmate
        if self.is_checkmate(self.current_turn):
            self.game_over = True
            self.winner = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        return True
    
    def get_board_state(self) -> Dict:
        """Get current board state for serialization."""
        state = {
            'board': [],
            'current_turn': self.current_turn.value,
            'game_over': self.game_over,
            'winner': self.winner.value if self.winner else None,
            'move_history': self.move_history
        }
        
        for row in range(8):
            board_row = []
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece:
                    board_row.append({
                        'type': piece.type.value,
                        'color': piece.color.value,
                        'has_moved': piece.has_moved,
                        'is_revealed': piece.is_revealed
                    })
                else:
                    board_row.append(None)
            state['board'].append(board_row)
        
        return state
    
    def load_board_state(self, state: Dict):
        """Load board state from serialized data."""
        self.current_turn = Color(state['current_turn'])
        self.game_over = state['game_over']
        self.winner = Color(state['winner']) if state['winner'] else None
        self.move_history = state['move_history']
        
        for row in range(8):
            for col in range(8):
                piece_data = state['board'][row][col]
                if piece_data:
                    piece = Piece(
                        PieceType(piece_data['type']),
                        Color(piece_data['color']),
                        (row, col)
                    )
                    piece.has_moved = piece_data['has_moved']
                    piece.is_revealed = piece_data['is_revealed']
                    self.set_piece(row, col, piece)
                else:
                    self.set_piece(row, col, None)