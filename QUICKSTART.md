# Liars Chess - Quick Start Guide

## Installation

1. **Install Python 3.7+** (if not already installed)
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

### Option 1: Start the Main Game
```bash
python main.py
```

### Option 2: Run the Demo
```bash
python demo.py
```

### Option 3: Run Tests
```bash
python test_game.py
```

## How to Play

### Game Setup
1. **Host a Game**: One player hosts a server
2. **Join a Game**: Other player connects to the host's IP and port
3. **Game Starts**: When 2 players are connected

### Basic Rules
- **Standard Chess Setup**: Normal chess board and pieces
- **Limited Visibility**: You can only see your own pieces
- **Enemy Pieces**: Appear as ● (black) or ○ (white) - you don't know what they are
- **Deception**: When moving, you can claim any piece type (lie about your move!)

### Making Moves
1. Enter move in format: `e2 e4`
2. Choose what piece type to claim (can be different from actual piece)
3. Opponent can either:
   - Make their move
   - Call "liar" on your move

### Liar Calling
- Type `liar` to call out the opponent's last move
- **If successful**: Opponent was lying, their piece gets revealed permanently
- **If failed**: You were wrong, you lose your next turn

### Special Commands
- `liar` - Call liar on opponent's last move
- `checkmate` - Claim checkmate (opponent can call liar on this too!)
- `help` - Show help
- `quit` - Exit game

### Winning
- **Checkmate**: Same as regular chess, but opponent can call liar on checkmate claims
- **Opponent Disconnects**: You win by default

## Network Play

### Hosting a Game
1. Choose "Host a new game"
2. Set port (default: 12000)
3. Share your IP address with the other player
4. Wait for opponent to connect

### Joining a Game
1. Choose "Join a game"
2. Enter host's IP address
3. Enter port number
4. Wait for game to start

## Game Features

✅ **Cross-platform** (Linux/Windows/Mac)  
✅ **Local network multiplayer**  
✅ **Game saving/loading**  
✅ **Player reconnection**  
✅ **Colored terminal interface**  
✅ **Deception mechanics**  
✅ **Liar calling system**  
✅ **Turn penalties**  
✅ **Checkmate verification**  

## Tips for Playing

1. **Psychology is Key**: The game is as much about reading your opponent as chess skill
2. **Mix Truth and Lies**: Don't lie every move - be unpredictable
3. **Watch for Patterns**: Opponents might have tells when they're lying
4. **Use Revealed Pieces**: Once a piece is revealed, you know exactly what it can do
5. **Checkmate Carefully**: Claiming false checkmate reveals all your pieces!

## Troubleshooting

### Connection Issues
- Make sure both players are on the same network
- Check firewall settings
- Try different port numbers if 12000 is blocked

### Game Crashes
- Check that all dependencies are installed
- Make sure you have Python 3.7+
- Run `python test_game.py` to verify installation

### Display Issues
- Make sure your terminal supports colored output
- Try resizing your terminal window
- On Windows, make sure you're using a modern terminal (Windows Terminal, PowerShell, etc.)

## Advanced Features

### Game Persistence
- Games are automatically saved after each move
- Reconnect using the same player name if disconnected
- Load previous games from the main menu

### Scalability
The codebase is designed to be easily extensible:
- Add new piece types
- Implement different game modes
- Add AI opponents
- Create tournament systems

Enjoy playing Liars Chess! 🎭♟️