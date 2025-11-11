"""
CLI interface for Liars Chess.
Handles terminal display, user input, and cross-platform compatibility.
"""

import os
import sys
from typing import List, Optional, Tuple, Dict
from chess_engine import PieceType, Color
from colorama import init, Fore, Back, Style
import re

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class CLIInterface:
    def __init__(self):
        self.board_size = 8
        self.clear_command = 'cls' if os.name == 'nt' else 'clear'
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system(self.clear_command)
    
    def display_title(self):
        """Display the game title."""
        title = """
╔══════════════════════════════════════╗
║            LIARS CHESS               ║
║     Where Deception Meets Strategy   ║
╚══════════════════════════════════════╝
        """
        print(Fore.CYAN + title)
    
    def display_board(self, visible_board: List[List[Optional[str]]], 
                     player_color: Color, highlighted_moves: List[Tuple[int, int]] = None):
        """Display the chess board from a player's perspective."""
        if highlighted_moves is None:
            highlighted_moves = []
        
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════╗")
        print(f"{Fore.CYAN}║              GAME BOARD              ║")
        print(f"{Fore.CYAN}╚══════════════════════════════════════╝")
        
        print(f"\n{Fore.YELLOW}🔵 Your pieces: {player_color.value.title()}")
        print(f"{Fore.RED}🔴 Enemy pieces: {'●' if player_color == Color.WHITE else '○'} (hidden)")
        print(f"{Fore.GREEN}✅ Revealed enemy pieces: shown as actual pieces")
        
        if highlighted_moves:
            print(f"{Fore.MAGENTA}🎯 Highlighted: possible moves")
        print()
        
        # Column labels with better spacing
        print("     " + "   ".join([f"{Fore.CYAN}{chr(ord('a') + i)}" for i in range(8)]))
        print(f"   {Fore.WHITE}┌" + "───┬" * 7 + "───┐")
        
        # Display board rows with improved formatting
        for row in range(8):
            display_row = 8 - row if player_color == Color.WHITE else row + 1
            row_str = f" {Fore.CYAN}{display_row} {Fore.WHITE}│"
            
            for col in range(8):
                board_row = row if player_color == Color.WHITE else 7 - row
                piece = visible_board[board_row][col]
                
                # Determine background color with better contrast
                is_light_square = (board_row + col) % 2 == 0
                if (board_row, col) in highlighted_moves:
                    bg_color = Back.MAGENTA
                    text_color = Fore.WHITE
                elif is_light_square:
                    bg_color = Back.LIGHTWHITE_EX
                    text_color = Fore.BLACK
                else:
                    bg_color = Back.LIGHTBLACK_EX
                    text_color = Fore.WHITE
                
                # Format piece display with better symbols
                if piece:
                    if piece in ['●', '○']:  # Unknown enemy pieces
                        piece_display = f"{bg_color}{Fore.RED} {piece} "
                    else:  # Known pieces
                        if piece in "♔♕♖♗♘♙":  # White pieces
                            piece_display = f"{bg_color}{Fore.BLUE} {piece} "
                        else:  # Black pieces
                            piece_display = f"{bg_color}{Fore.RED} {piece} "
                else:
                    piece_display = f"{bg_color}{text_color}   "
                
                row_str += piece_display + f"{Style.RESET_ALL}{Fore.WHITE}│"
            
            print(row_str)
            
            # Add horizontal separator between rows (except last)
            if row < 7:
                print(f"   {Fore.WHITE}├" + "───┼" * 7 + "───┤")
        
        print(f"   {Fore.WHITE}└" + "───┴" * 7 + "───┘")
        print("     " + "   ".join([f"{Fore.CYAN}{chr(ord('a') + i)}" for i in range(8)]))
        print(f"{Style.RESET_ALL}")
    
    def display_game_status(self, game_info: Dict):
        """Display current game status information."""
        print(f"\n{Fore.CYAN}═══ GAME STATUS ═══")
        print(f"{Fore.WHITE}Turn: {Fore.YELLOW}{game_info['current_turn'].title()}")
        
        if game_info.get('in_check'):
            print(f"{Fore.RED}⚠️  You are in CHECK!")
        
        if game_info.get('can_call_liar'):
            print(f"{Fore.GREEN}📢 You can call LIAR on the last move!")
        
        if game_info.get('turn_penalty', 0) > 0:
            print(f"{Fore.RED}⏸️  You must skip {game_info['turn_penalty']} turn(s)")
        
        if game_info.get('last_move_summary'):
            print(f"{Fore.MAGENTA}Last move: {game_info['last_move_summary']}")
        
        if game_info.get('game_over'):
            winner = game_info.get('winner', 'Unknown')
            print(f"\n{Fore.YELLOW}🏆 GAME OVER! Winner: {winner.title()}")
    
    def get_move_input(self, available_pieces: List[Tuple[int, int]] = None) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """Get move input from user with enhanced suggestions."""
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════╗")
        print(f"{Fore.CYAN}║              YOUR TURN               ║")
        print(f"{Fore.CYAN}╚══════════════════════════════════════╝")
        
        print(f"\n{Fore.YELLOW}📝 Enter your move:")
        print(f"{Fore.WHITE}   • Format: 'e2 e4' (from square to square)")
        print(f"{Fore.WHITE}   • Special: 'liar' to call opponent a liar")
        print(f"{Fore.WHITE}   • Special: 'checkmate' to claim victory")
        print(f"{Fore.WHITE}   • Commands: 'help', 'quit'")
        
        if available_pieces:
            coords_to_algebraic = lambda pos: chr(ord('a') + pos[1]) + str(pos[0] + 1)
            piece_squares = [coords_to_algebraic(pos) for pos in available_pieces[:6]]  # Show first 6
            if len(available_pieces) > 6:
                piece_squares.append("...")
            print(f"{Fore.GREEN}   💡 Your pieces at: {', '.join(piece_squares)}")
        
        while True:
            user_input = input(f"\n{Fore.CYAN}Move> {Fore.WHITE}").strip().lower()
            
            if user_input in ['quit', 'exit', 'q']:
                return None, None
            
            if user_input == 'help':
                self.display_help()
                continue
            
            if user_input == 'liar':
                return 'liar', None
            
            if user_input == 'checkmate':
                return 'checkmate', None
            
            # Parse move input with better error messages
            move_pattern = r'^([a-h][1-8])\s+([a-h][1-8])$'
            match = re.match(move_pattern, user_input)
            
            if match:
                from_square, to_square = match.groups()
                from_pos = self.algebraic_to_coords(from_square)
                to_pos = self.algebraic_to_coords(to_square)
                
                # Validate squares are different
                if from_pos == to_pos:
                    print(f"{Fore.RED}❌ Cannot move to the same square!")
                    continue
                    
                return from_pos, to_pos
            
            # Provide specific error messages
            if len(user_input.split()) != 2:
                print(f"{Fore.RED}❌ Please enter two squares separated by space (e.g., 'e2 e4')")
            elif not re.match(r'^[a-h][1-8]', user_input.split()[0]):
                print(f"{Fore.RED}❌ First square invalid. Use format like 'e2' (column a-h, row 1-8)")
            elif not re.match(r'^[a-h][1-8]', user_input.split()[1]):
                print(f"{Fore.RED}❌ Second square invalid. Use format like 'e4' (column a-h, row 1-8)")
            else:
                print(f"{Fore.RED}❌ Invalid format. Use 'e2 e4' or type 'help' for more options")
    
    def get_piece_type_input(self, available_moves: Dict[PieceType, List[Tuple[int, int]]]) -> Optional[PieceType]:
        """Get the piece type the player wants to claim."""
        print(f"\n{Fore.CYAN}╔══════════════════════════════════════╗")
        print(f"{Fore.CYAN}║           CHOOSE PIECE TYPE          ║")
        print(f"{Fore.CYAN}╚══════════════════════════════════════╝")
        
        print(f"\n{Fore.YELLOW}🎭 What piece do you want to pretend to be?")
        print(f"{Fore.WHITE}   (Remember: You can lie about your piece type!)")
        
        piece_options = []
        piece_symbols = {
            PieceType.PAWN: "♟",
            PieceType.ROOK: "♜", 
            PieceType.KNIGHT: "♞",
            PieceType.BISHOP: "♝",
            PieceType.QUEEN: "♛",
            PieceType.KING: "♚"
        }
        
        for i, (piece_type, moves) in enumerate(available_moves.items(), 1):
            piece_name = piece_type.value.title()
            symbol = piece_symbols.get(piece_type, "?")
            move_count = len(moves)
            
            # Show first few moves as examples
            example_moves = [self.coords_to_algebraic(move) for move in moves[:3]]
            examples = ", ".join(example_moves)
            if len(moves) > 3:
                examples += "..."
                
            print(f"{Fore.WHITE}{i}. {symbol} {piece_name} - {Fore.GREEN}{move_count} moves {Fore.CYAN}({examples})")
            piece_options.append(piece_type)
        
        print(f"\n{Fore.MAGENTA}💡 Tip: Choose wisely - your opponent might call you a liar!")
        
        while True:
            try:
                choice = input(f"\n{Fore.CYAN}Select> {Fore.WHITE}").strip()
                
                if choice.lower() in ['quit', 'exit', 'q', 'back']:
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(piece_options):
                    selected_piece = piece_options[choice_num - 1]
                    symbol = piece_symbols.get(selected_piece, "?")
                    print(f"{Fore.GREEN}✅ You chose to move as: {symbol} {selected_piece.value.title()}")
                    return selected_piece
                else:
                    print(f"{Fore.RED}❌ Please enter a number between 1 and {len(piece_options)}")
                    
            except ValueError:
                print(f"{Fore.RED}❌ Please enter a valid number (1-{len(piece_options)})")
    
    def display_possible_moves(self, moves: List[Tuple[int, int]]):
        """Display possible moves for a piece."""
        if not moves:
            print(f"{Fore.RED}No legal moves available for this piece type")
            return
        
        print(f"{Fore.GREEN}Possible moves:")
        move_strs = [self.coords_to_algebraic(move) for move in moves]
        for i, move in enumerate(move_strs):
            if i % 8 == 0 and i > 0:
                print()
            print(f"{move:4}", end=" ")
        print()
    
    def algebraic_to_coords(self, algebraic: str) -> Tuple[int, int]:
        """Convert algebraic notation (e.g., 'e4') to board coordinates."""
        col = ord(algebraic[0]) - ord('a')
        row = 8 - int(algebraic[1])
        return (row, col)
    
    def coords_to_algebraic(self, coords: Tuple[int, int]) -> str:
        """Convert board coordinates to algebraic notation."""
        row, col = coords
        return chr(ord('a') + col) + str(8 - row)
    
    def display_help(self):
        """Display help information."""
        help_text = f"""
{Fore.CYAN}═══ LIARS CHESS COMMANDS ═══

{Fore.WHITE}Movement:
  e2 e4     - Move piece from e2 to e4
  
{Fore.WHITE}Special Actions:
  liar      - Call liar on opponent's last move
  checkmate - Claim checkmate
  
{Fore.WHITE}General:
  help      - Show this help
  quit      - Exit game

{Fore.YELLOW}═══ HOW TO PLAY ═══

{Fore.WHITE}• You can only see your own pieces
• Enemy pieces appear as ● or ○
• When moving, choose what piece type to imitate
• You can lie about your piece type!
• Opponents can call "liar" to reveal lying pieces
• Win by checkmate (but opponents can call liar on checkmate claims!)

{Fore.GREEN}Good luck, and remember... trust no one! 🎭
        """
        print(help_text)
    
    def display_connection_status(self, status: str, details: str = ""):
        """Display network connection status."""
        status_colors = {
            'connecting': Fore.YELLOW,
            'connected': Fore.GREEN,
            'disconnected': Fore.RED,
            'error': Fore.RED,
            'waiting': Fore.CYAN
        }
        
        color = status_colors.get(status, Fore.WHITE)
        print(f"{color}🌐 {status.title()}: {details}")
    
    def display_player_info(self, player_id: str, color: Color, opponent: str = None):
        """Display player information."""
        print(f"\n{Fore.CYAN}═══ PLAYER INFO ═══")
        print(f"{Fore.WHITE}You: {Fore.YELLOW}{player_id} ({color.value.title()})")
        if opponent:
            opponent_color = "Black" if color == Color.WHITE else "White"
            print(f"{Fore.WHITE}Opponent: {Fore.YELLOW}{opponent} ({opponent_color})")
    
    def get_menu_choice(self, options: List[str], title: str = "Choose an option") -> Optional[int]:
        """Display a menu and get user choice."""
        print(f"\n{Fore.CYAN}{title}:")
        
        for i, option in enumerate(options, 1):
            print(f"{Fore.WHITE}{i}. {option}")
        
        while True:
            try:
                choice = input(f"{Fore.WHITE}Enter choice (1-{len(options)}) or 'q' to quit: ").strip()
                
                if choice.lower() in ['quit', 'exit', 'q']:
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(options):
                    return choice_num - 1
                else:
                    print(f"{Fore.RED}Please enter a number between 1 and {len(options)}")
                    
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number")
    
    def get_text_input(self, prompt: str, default: str = None) -> Optional[str]:
        """Get text input from user."""
        full_prompt = f"{Fore.WHITE}{prompt}"
        if default:
            full_prompt += f" (default: {default})"
        full_prompt += ": "
        
        user_input = input(full_prompt).strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            return None
        
        return user_input if user_input else default
    
    def display_saved_games(self, saved_games: Dict[str, Dict]):
        """Display list of saved games."""
        if not saved_games:
            print(f"{Fore.YELLOW}No saved games found.")
            return
        
        print(f"\n{Fore.CYAN}═══ SAVED GAMES ═══")
        
        for game_id, info in saved_games.items():
            players = ", ".join(info['players'])
            saved_at = info['saved_at'][:19] if len(info['saved_at']) > 19 else info['saved_at']
            
            print(f"{Fore.WHITE}Game ID: {Fore.YELLOW}{game_id}")
            print(f"{Fore.WHITE}Players: {players}")
            print(f"{Fore.WHITE}Saved: {saved_at}")
            print(f"{Fore.WHITE}Status: {info['metadata'].get('status', 'unknown')}")
            print("-" * 40)
    
    def display_error(self, message: str):
        """Display an error message."""
        print(f"{Fore.RED}❌ Error: {message}")
    
    def display_success(self, message: str):
        """Display a success message."""
        print(f"{Fore.GREEN}✅ {message}")
    
    def display_info(self, message: str):
        """Display an info message."""
        print(f"{Fore.CYAN}ℹ️  {message}")
    
    def display_warning(self, message: str):
        """Display a warning message."""
        print(f"{Fore.YELLOW}⚠️  {message}")
    
    def wait_for_enter(self, message: str = "Press Enter to continue..."):
        """Wait for user to press Enter."""
        input(f"{Fore.WHITE}{message}")
    
    def display_liar_call_result(self, result: str, message: str):
        """Display the result of a liar call."""
        if result == 'successful':
            print(f"{Fore.GREEN}🎯 {message}")
        elif result == 'failed':
            print(f"{Fore.RED}💥 {message}")
        else:
            print(f"{Fore.YELLOW}❓ {message}")
    
    def display_move_result(self, success: bool, message: str = ""):
        """Display the result of a move attempt."""
        if success:
            print(f"{Fore.GREEN}✅ Move successful!")
        else:
            print(f"{Fore.RED}❌ Move failed: {message}")
    
    def confirm_action(self, message: str) -> bool:
        """Get confirmation from user for an action."""
        response = input(f"{Fore.YELLOW}{message} (y/n): ").strip().lower()
        return response in ['y', 'yes', '1', 'true']