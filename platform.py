"""
Platform class for the Escape-WE-Project game.
"""

import pygame
from typing import Tuple
from config import load_image, ASSETS


class Platform(pygame.sprite.Sprite):
    """
    Represents a single platform in the game.
    
    Attributes:
        image: The platform's sprite.
        rect: The platform's rectangle for positioning and collision.
    """
    
    def __init__(self, position: Tuple[int, int], size: Tuple[int, int]):
        """
        Initializes a platform.
        
        Args:
            position: The (x, y) coordinates of the top-left corner.
            size: The (width, height) of the platform.
        """
        super().__init__()
        self.image = load_image(ASSETS['platform'], size)
        self.rect = self.image.get_rect(topleft=position)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draws the platform on the screen.
        
        Args:
            screen: The pygame.Surface to draw on.
        """
        screen.blit(self.image, self.rect) 