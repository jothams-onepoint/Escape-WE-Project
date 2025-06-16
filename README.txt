Escape-WE-Project
==================

Overview
--------
Escape-WE-Project is a 2D side-scrolling action-adventure game built with Python and Pygame. The player must navigate through multiple levels, defeat enemies, collect items, and use keys to unlock doors and progress. The game features inventory management, interactive chests, and a variety of enemy types.

Features
--------
- Player Movement: Run, jump, and interact with the environment.
- Combat: Attack enemies using weapons found in chests.
- Inventory System: Manage up to three items, equip weapons, and use keys.
- Chests: Open chests to find weapons and add them to your inventory.
- Enemies: Randomly moving enemies with different sprites and behaviors.
- Keys and Doors: Find keys to unlock doors and advance to the next level.
- Scrolling Levels: Large, scrollable levels with background transitions.
- Win/Lose Conditions: Survive through 10 levels to win; lose all lives and the game ends.

How to Play
-----------
1. Start the Game: Run Environment.py to launch the main game loop.
2. Controls:
   - A / D: Move left/right
   - SPACE: Jump
   - E: Interact (attack, open chests, pick up items, use doors)
   - Q: Drop equipped item
   - Mouse: Select inventory slots and interact with UI
3. Objective: Defeat enemies, collect keys, open doors, and reach the final level to win.

Game Objects
------------
- Player: Can move, jump, attack, and manage inventory.
- Enemies: Move randomly and can damage the player.
- Items: Weapons and keys, each with unique interactions.
- Chests: Contain weapons; require a key to open.
- Doors: Require a key to open and allow progression to the next level.

File Structure
--------------
- Environment.py: Main game loop and environment setup.
- playerClass.py: Player mechanics and controls.
- itemClass.py: Item and weapon logic.
- Enemy.py: Enemy behaviors and sprites.
- Chest.py: Chest and inventory system.
- doorClass.py: Door logic and level progression.
- level.py: Level transition logic.
- Image files (*.png, *.jpg): Sprites for player, enemies, items, backgrounds, etc.

Requirements
------------
- Python 3.x
- Pygame

Install dependencies with:
    pip install pygame

Running the Game
----------------
From the Escape-WE-Project directory, run:
    python Environment.py

Credits
-------
Developed by Onepoint work experience students.
Sprites and assets are included in the repository. 