"""
Configuration file for the Escape-WE-Project game.
Contains all constants and settings used throughout the game.
"""

import pygame
from typing import Tuple

# Display settings
BASE_SCREEN_WIDTH = 800
BASE_SCREEN_HEIGHT = 600
SCREEN_WIDTH = BASE_SCREEN_WIDTH
SCREEN_HEIGHT = BASE_SCREEN_HEIGHT
FPS = 60
SCALE = 1.0  # Will be set dynamically in game.py for fullscreen

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 128, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Player settings
PLAYER_SIZE = int(150 * SCALE)
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_VELOCITY = -20
PLAYER_LIVES = 3
PLAYER_MAX_HEALTH = 100

# Enemy settings
ENEMY_SIZE = PLAYER_SIZE
ENEMY_SPEED = 1
ENEMY_MOVE_DURATION = 60

# Item settings
ITEM_SIZE = (int(75 * SCALE), int(75 * SCALE))
WEAPON_SIZE = (int(100 * SCALE), int(100 * SCALE))
KEY_SIZE = (int(50 * SCALE), int(50 * SCALE))
ITEM_GRAVITY = 0.8

# Chest settings
CHEST_SIZE = (int(130 * SCALE), int(100 * SCALE))

# Door settings
DOOR_SIZE = (int(150 * SCALE), int(220 * SCALE))

# UI settings
BUTTON_WIDTH = int(200 * SCALE)
BUTTON_HEIGHT = int(50 * SCALE)
BUTTON_TEXT_SIZE = int(36 * SCALE)
INVENTORY_SLOT_WIDTH = int(80 * SCALE)
INVENTORY_SLOT_HEIGHT = int(40 * SCALE)
INVENTORY_SLOT_MARGIN = int(5 * SCALE)
INVENTORY_MAX_SLOTS = 3

# Game settings
MAX_BACKGROUND_DUPLICATES = 1
SCROLL_SPEED = 5
NORMAL_SPEED = 5
BORDER_TRANSITION_SPEED = 2
TRANSITION_DISTANCE = 100
TOTAL_LEVELS = 10

# Background size
BACKGROUND_SIZE = (int(3200 * SCALE), int(600 * SCALE))

# Asset paths
ASSETS = {
    'player_sprite': 'player_sprite.png',
    'enemy1': 'enemy1.png',
    'enemy2': 'enemy2.png',
    'enemy3': 'enemy3.png',
    'sword': 'sword.png',
    'key': 'key_sprite.png',
    'chest_closed': 'chest_closed.png',
    'chest_open': 'chest_open.png',
    'door': 'door_sprite.png',
    'background': 'background.png',
    'menu': 'menu.jpg'
}

def load_image(path: str, size: Tuple[int, int] | None = None) -> pygame.Surface:
    """
    Load and optionally scale an image.
    
    Args:
        path: Path to the image file
        size: Optional tuple of (width, height) to scale the image
        
    Returns:
        Loaded pygame Surface
    """
    try:
        image = pygame.image.load(path).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Error loading image {path}: {e}")
        # Return a colored surface as fallback
        fallback = pygame.Surface((50, 50))
        fallback.fill(RED)
        return fallback 