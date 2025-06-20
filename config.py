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

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 128, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Player settings
PLAYER_SIZE = (150, 150)
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_VELOCITY = -20
PLAYER_LIVES = 3
PLAYER_MAX_HEALTH = 100

# Enemy settings
ENEMY_SIZE = (150, 150)
ENEMY_SPEED = 1
ENEMY_MOVE_DURATION = 60

# Item settings
ITEM_SIZE = (60, 60)
WEAPON_SIZE = (80, 80)
KEY_SIZE = (60, 60)
ITEM_GRAVITY = 0.8

# Chest settings
CHEST_SIZE = (100, 100)

# Door settings
DOOR_SIZE = (160, 240)

# UI settings
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_TEXT_SIZE = 36
INVENTORY_SLOT_WIDTH = 80
INVENTORY_SLOT_HEIGHT = 40
INVENTORY_SLOT_MARGIN = 5
INVENTORY_MAX_SLOTS = 3

# Game settings
MAX_BACKGROUND_DUPLICATES = 1
SCROLL_SPEED = 5
NORMAL_SPEED = 5
BORDER_TRANSITION_SPEED = 2
TRANSITION_DISTANCE = 100
TOTAL_LEVELS = 10

# Background size
BACKGROUND_SIZE = (3200, 600)

# Asset paths
ASSETS = {
    'player': 'player_sprite.png',
    'enemy1': 'enemy1.png',
    'enemy2': 'enemy2.png',
    'enemy3': 'enemy3.png',
    'chest_open': 'chest_open.png',
    'chest_closed': 'chest_closed.png',
    'key': 'key_sprite.png',
    'sword': 'sword.png',
    'door': 'door_sprite.png',
    'background': 'background.png',
    'menu': 'menu.png',
    'platform': 'platform.png'
}

PLATFORM_SIZE = (240, 30)

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