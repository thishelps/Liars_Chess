"""
Network manager for Liars Chess.
Handles server-client communication, player management, and reconnection.
"""

import socket
import threading
import json
import time
from typing import Dict, List, Optional, Callable
from enum import Enum
from chess_engine import Color
import uuid


class MessageType(Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    GAME_STATE = "game_state"
    MOVE = "move"
    LIAR_CALL = "liar_call"
    CHECKMATE_CLAIM = "checkmate_claim"
    CHAT = "chat"
    HEARTBEAT = "heartbeat"
    ERROR = "error"
    GAME_OVER = "game_over"


class PlayerConnection:
    def __init__(self, socket: socket.socket, address: tuple, player_id: str, color: Color):
        self.socket = socket
        self.address = address
        self.player_id = player_id
        self.color = color
        self.connected = True
        self.last_heartbeat = time.time()
        self.reconnect_token = str(uuid.uuid4())
    
    def send_message(self, message: Dict) -> bool:
        """Send a message to the client."""
        try:
            message_str = json.dumps(message) + '\n'
            self.socket.send(message_str.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending message to {self.player_id}: {e}")
            self.connected = False
            return False
    
    def close(self):
        """Close the connection."""
        self.connected = False
        try:
            self.socket.close()
        except:
            pass


class GameServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 12000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.players: Dict[str, PlayerConnection] = {}
        self.game_callbacks: Dict[str, Callable] = {}
        self.max_players = 2
        self.game_started = False
        self.heartbeat_interval = 30  # seconds
        
    def register_callback(self, message_type: str, callback: Callable):
        """Register a callback for handling specific message types."""
        self.game_callbacks[message_type] = callback
    
    def start_server(self):
        """Start the game server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"Liars Chess server started on {self.host}:{self.port}")
            
            # Start heartbeat thread
            threading.Thread(target=self._heartbeat_monitor, daemon=True).start()
            
            # Accept connections
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    threading.Thread(target=self._handle_client, args=(client_socket, address), daemon=True).start()
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
                    
        except Exception as e:
            print(f"Error starting server: {e}")
        finally:
            self.stop_server()
    
    def stop_server(self):
        """Stop the game server."""
        self.running = False
        
        # Close all player connections
        for player in list(self.players.values()):
            player.close()
        self.players.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("Server stopped")
    
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle a client connection."""
        player_id = None
        try:
            # Receive initial connection message
            data = client_socket.recv(1024).decode('utf-8').strip()
            if not data:
                return
            
            message = json.loads(data)
            
            if message['type'] == MessageType.CONNECT.value:
                player_id = self._handle_player_connect(client_socket, address, message)
                if not player_id:
                    return
                
                # Handle messages from this client
                buffer = ""
                while self.running and player_id in self.players and self.players[player_id].connected:
                    try:
                        data = client_socket.recv(1024).decode('utf-8')
                        if not data:
                            break
                        
                        buffer += data
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            if line.strip():
                                self._process_message(player_id, json.loads(line.strip()))
                                
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"Error handling client {player_id}: {e}")
                        break
                        
        except Exception as e:
            print(f"Error in client handler: {e}")
        finally:
            if player_id and player_id in self.players:
                self._handle_player_disconnect(player_id)
    
    def _handle_player_connect(self, client_socket: socket.socket, address: tuple, message: Dict) -> Optional[str]:
        """Handle a player connection request."""
        if len(self.players) >= self.max_players:
            # Check for reconnection
            reconnect_token = message.get('reconnect_token')
            if reconnect_token:
                for player in self.players.values():
                    if player.reconnect_token == reconnect_token:
                        # Reconnect existing player
                        player.socket = client_socket
                        player.address = address
                        player.connected = True
                        player.last_heartbeat = time.time()
                        
                        player.send_message({
                            'type': MessageType.CONNECT.value,
                            'status': 'reconnected',
                            'player_id': player.player_id,
                            'color': player.color.value,
                            'reconnect_token': player.reconnect_token
                        })
                        
                        # Notify game of reconnection
                        if 'player_reconnect' in self.game_callbacks:
                            self.game_callbacks['player_reconnect'](player.player_id)
                        
                        return player.player_id
            
            # Server full
            client_socket.send(json.dumps({
                'type': MessageType.ERROR.value,
                'message': 'Server full'
            }).encode('utf-8'))
            client_socket.close()
            return None
        
        # Assign player ID and color
        player_id = message.get('player_name', f"Player{len(self.players) + 1}")
        color = Color.WHITE if len(self.players) == 0 else Color.BLACK
        
        player = PlayerConnection(client_socket, address, player_id, color)
        self.players[player_id] = player
        
        # Send connection confirmation
        player.send_message({
            'type': MessageType.CONNECT.value,
            'status': 'connected',
            'player_id': player_id,
            'color': color.value,
            'reconnect_token': player.reconnect_token
        })
        
        print(f"Player {player_id} connected as {color.value} from {address}")
        
        # Start game if we have enough players
        if len(self.players) == self.max_players and not self.game_started:
            self.game_started = True
            if 'game_start' in self.game_callbacks:
                self.game_callbacks['game_start']()
        
        return player_id
    
    def _handle_player_disconnect(self, player_id: str):
        """Handle a player disconnection."""
        if player_id in self.players:
            player = self.players[player_id]
            player.connected = False
            print(f"Player {player_id} disconnected")
            
            # Notify game of disconnection
            if 'player_disconnect' in self.game_callbacks:
                self.game_callbacks['player_disconnect'](player_id)
    
    def _process_message(self, player_id: str, message: Dict):
        """Process a message from a client."""
        message_type = message.get('type')
        
        if message_type == MessageType.HEARTBEAT.value:
            if player_id in self.players:
                self.players[player_id].last_heartbeat = time.time()
                self.players[player_id].send_message({'type': MessageType.HEARTBEAT.value})
        
        elif message_type in self.game_callbacks:
            self.game_callbacks[message_type](player_id, message)
    
    def _heartbeat_monitor(self):
        """Monitor player connections with heartbeat."""
        while self.running:
            current_time = time.time()
            disconnected_players = []
            
            for player_id, player in self.players.items():
                if player.connected and current_time - player.last_heartbeat > self.heartbeat_interval * 2:
                    print(f"Player {player_id} timed out")
                    player.connected = False
                    disconnected_players.append(player_id)
            
            for player_id in disconnected_players:
                self._handle_player_disconnect(player_id)
            
            time.sleep(self.heartbeat_interval)
    
    def broadcast_message(self, message: Dict, exclude_player: Optional[str] = None):
        """Broadcast a message to all connected players."""
        for player_id, player in self.players.items():
            if player.connected and player_id != exclude_player:
                player.send_message(message)
    
    def send_to_player(self, player_id: str, message: Dict) -> bool:
        """Send a message to a specific player."""
        if player_id in self.players and self.players[player_id].connected:
            return self.players[player_id].send_message(message)
        return False
    
    def get_connected_players(self) -> List[str]:
        """Get list of connected player IDs."""
        return [pid for pid, player in self.players.items() if player.connected]
    
    def get_player_color(self, player_id: str) -> Optional[Color]:
        """Get the color of a player."""
        if player_id in self.players:
            return self.players[player_id].color
        return None


class GameClient:
    def __init__(self, host: str = "localhost", port: int = 12000):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.player_id = None
        self.color = None
        self.reconnect_token = None
        self.message_callbacks: Dict[str, Callable] = {}
        self.heartbeat_thread = None
    
    def register_callback(self, message_type: str, callback: Callable):
        """Register a callback for handling specific message types."""
        self.message_callbacks[message_type] = callback
    
    def connect(self, player_name: str, reconnect_token: Optional[str] = None) -> bool:
        """Connect to the game server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Send connection request
            connect_message = {
                'type': MessageType.CONNECT.value,
                'player_name': player_name
            }
            if reconnect_token:
                connect_message['reconnect_token'] = reconnect_token
            
            self.socket.send((json.dumps(connect_message) + '\n').encode('utf-8'))
            
            # Wait for connection response
            response = self.socket.recv(1024).decode('utf-8').strip()
            message = json.loads(response)
            
            if message['type'] == MessageType.CONNECT.value and message['status'] in ['connected', 'reconnected']:
                self.connected = True
                self.player_id = message['player_id']
                self.color = Color(message['color'])
                self.reconnect_token = message['reconnect_token']
                
                # Start message handling thread
                threading.Thread(target=self._message_handler, daemon=True).start()
                
                # Start heartbeat thread
                self.heartbeat_thread = threading.Thread(target=self._heartbeat_sender, daemon=True)
                self.heartbeat_thread.start()
                
                return True
            else:
                print(f"Connection failed: {message.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server."""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def send_message(self, message: Dict) -> bool:
        """Send a message to the server."""
        if not self.connected:
            return False
        
        try:
            message_str = json.dumps(message) + '\n'
            self.socket.send(message_str.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
            return False
    
    def _message_handler(self):
        """Handle incoming messages from the server."""
        buffer = ""
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        message = json.loads(line.strip())
                        self._process_message(message)
                        
            except Exception as e:
                if self.connected:
                    print(f"Error in message handler: {e}")
                break
        
        self.connected = False
    
    def _process_message(self, message: Dict):
        """Process a message from the server."""
        message_type = message.get('type')
        if message_type in self.message_callbacks:
            self.message_callbacks[message_type](message)
    
    def _heartbeat_sender(self):
        """Send periodic heartbeat messages."""
        while self.connected:
            time.sleep(25)  # Send heartbeat every 25 seconds
            if self.connected:
                self.send_message({'type': MessageType.HEARTBEAT.value})
    
    def make_move(self, from_pos: tuple, to_pos: tuple, claimed_piece: str) -> bool:
        """Send a move to the server."""
        return self.send_message({
            'type': MessageType.MOVE.value,
            'from_pos': from_pos,
            'to_pos': to_pos,
            'claimed_piece': claimed_piece
        })
    
    def call_liar(self) -> bool:
        """Call liar on the opponent's last move."""
        return self.send_message({
            'type': MessageType.LIAR_CALL.value
        })
    
    def claim_checkmate(self) -> bool:
        """Claim checkmate."""
        return self.send_message({
            'type': MessageType.CHECKMATE_CLAIM.value
        })