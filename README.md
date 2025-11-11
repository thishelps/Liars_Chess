# Liars Chess

A deceptive twist on traditional chess where players can lie about their piece movements!

## Game Rules

### Basic Concept
- Standard chess setup, but you can only see your own pieces
- Enemy pieces appear as generic "unknown" pieces
- Players can make any piece move like any other piece (lie about the move)
- Opponents can call "liar" to reveal the truth

### Gameplay Flow
1. **Move Phase**: Choose a piece and declare what type of move you're making
2. **Opponent's Choice**: 
   - Make their own move, OR
   - Call "liar" on your previous move

### Liar Calling Rules
- **Successful call** (opponent was lying): Lying piece is revealed permanently
- **False accusation** (opponent was telling truth): Accuser loses their next turn
- **Checkmate lies**: If you claim checkmate while lying, and opponent calls "liar":
  - If truly checkmate: Accuser loses immediately
  - If not checkmate: All your pieces are revealed permanently

### Victory Conditions
- Traditional checkmate (but opponent can call "liar" on checkmate claims)
- Opponent forfeits or disconnects

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Run the main game
python main.py

# Or try the demo first
python demo.py
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## Features
- Cross-platform (Linux/Windows)
- Local network multiplayer
- Game saving/loading
- Player reconnection handling
- Scalable architecture for future features

## Architecture
- `chess_engine.py`: Core chess logic and rules
- `deception_layer.py`: Handles piece visibility and lying mechanics
- `network_manager.py`: Server/client networking
- `game_state.py`: Game state management and persistence
- `cli_interface.py`: Terminal user interface
- `main.py`: Entry point and game coordinator