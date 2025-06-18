# Escape-WE-Project

## Overview

**Escape-WE-Project** is a 2D side-scrolling action-adventure game built with Python and Pygame. The player must navigate through multiple levels, defeat enemies, collect items, and use keys to unlock doors and progress. The game features inventory management, interactive chests, and a variety of enemy types.

## Features

- **Player Movement:** Run, jump, and interact with the environment
- **Combat:** Attack enemies using weapons found in chests
- **Inventory System:** Manage up to three items, equip weapons, and use keys
- **Chests:** Open chests to find weapons and add them to your inventory
- **Enemies:** Randomly moving enemies with different sprites and behaviors
- **Keys and Doors:** Find keys to unlock doors and advance to the next level
- **Scrolling Levels:** Large, scrollable levels with background transitions

## How to Play

1. **Start the Game:** Run `game.py` to launch the main game loop
2. **Controls:**
   - `A` / `D`: Move left/right
   - `SPACE`: Jump
   - `E`: Interact (attack, open chests, pick up items, use doors)
   - `Q`: Drop equipped item
   - Mouse: Select inventory slots and interact with UI
3. **Objective:** Defeat enemies, collect keys, open doors, and reach the final level to win

## Game Objects

- **Player:** Can move, jump, attack, and manage inventory
- **Enemies:** Move randomly and can damage the player
- **Items:** Weapons and keys, each with unique interactions
- **Chests:** Contain weapons; require a key to open
- **Doors:** Require a key to open and allow progression to the next level

## File Structure

### Core Files
- `game.py`: Main game loop and state management
- `config.py`: Centralized configuration and constants
- `player.py`: Player mechanics and controls
- `item.py`: Item and weapon logic
- `enemy.py`: Enemy behaviors and sprites
- `chest.py`: Chest and inventory system
- `door.py`: Door logic and level progression
- `inventory.py`: Inventory management system

### Assets
- `*.png`, `*.jpg`: Sprites for player, enemies, items, backgrounds, etc.

## Code Quality Improvements

The codebase has been completely rewritten and optimized with the following improvements:

- **Centralized Configuration:** All constants moved to `config.py`
- **Type Annotations:** Full type hints throughout the codebase
- **Modular Design:** Clean separation of concerns with dedicated modules
- **Documentation:** Comprehensive docstrings for all classes and methods
- **Error Handling:** Robust error handling and fallback mechanisms
- **Code Reusability:** Eliminated code duplication and redundant files
- **Modern Python:** Uses Python 3.10+ features and best practices

## Requirements

- Python 3.10+
- Pygame

Install dependencies with:
```bash
pip install pygame
```

## Running the Game

From the `Escape-WE-Project` directory, run:
```bash
python game.py
```

## Development

The codebase follows modern Python development practices:

- **Type Safety:** Full type annotations for better IDE support and error catching
- **Documentation:** Google-style docstrings for all public APIs
- **Modularity:** Each class has a single responsibility
- **Configuration:** Centralized settings for easy modification
- **Asset Management:** Centralized asset loading with error handling

## Credits

Developed by Onepoint work experience students.  
Sprites and assets are included in the repository. 