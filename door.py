"""
Door class for the Escape-WE-Project game.
Handles door interactions and level progression.
"""

import pygame
import random
from typing import Tuple
from config import (
    SCREEN_HEIGHT, DOOR_SIZE, load_image, ASSETS, PLAYER_MAX_HEALTH
)


class Door:
    """
    Door class for level progression.
    
    Attributes:
        is_open: Whether the door is open
        rect: Pygame rect for collision detection
        image: Door sprite image
        total_width: Total width of the scrollable area
    """
    
    def __init__(self, size: Tuple[int, int], total_width: int):
        """
        Initialize a door.
        
        Args:
            size: Door size (width, height)
            total_width: Total width of the scrollable area
        """
        self.size = size
        self.total_width = total_width
        self.is_open = False

        # Load door sprite
        self.image = load_image(ASSETS['door'], size)
        self.rect = self.image.get_rect()

        # Randomize position
        self._randomize_position()

    def _randomize_position(self) -> None:
        """Set door to a random position within the level."""
        x = random.randint(0, self.total_width - self.size[0])
        y = SCREEN_HEIGHT - self.size[1]
        self.rect.topleft = (x, y)

    def draw(self, screen: pygame.Surface, scroll_offset: int) -> None:
        """
        Draw the door on the screen.
        
        Args:
            screen: Pygame surface to draw on
            scroll_offset: Current scroll offset
        """
        if not self.is_open:
            adjusted_rect = self.rect.copy()
            adjusted_rect.x -= scroll_offset
            
            # Only draw if door is visible on screen
            if adjusted_rect.right >= 0 and adjusted_rect.left <= screen.get_width():
                screen.blit(self.image, adjusted_rect.topleft)

    def is_near(self, player, scroll_offset: int) -> bool:
        """
        Check if player is near the door.
        
        Args:
            player: Player instance
            scroll_offset: Current scroll offset
            
        Returns:
            True if player is near the door
        """
        adjusted_x = self.rect.x - scroll_offset
        return (abs(adjusted_x - player.rect.x) < 100 and 
                abs(self.rect.y - player.rect.y) < 100)

    def use(self, player) -> None:
        """
        Use the door with a key.
        
        Args:
            player: Player instance
        """
        if player.has_key:
            print(f"{player.name} uses the key to open the door and proceeds to the next level!")
            self.is_open = True
            player.has_key = False  # Remove key after use
            # Heal player by 5 (capped at max health)
            player.health = min(player.health + 5, PLAYER_MAX_HEALTH)
        else:
            print("You need a key to open this door!")

    def reset(self) -> None:
        """Reset the door to closed state and randomize position."""
        self.is_open = False
        self._randomize_position() 