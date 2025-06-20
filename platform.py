import pygame
from typing import Tuple
from config import SCREEN_HEIGHT, SCREEN_WIDTH, load_image

class Platform:
    """
    Represents a platform in the game that the player can stand on, jump on, or collide with.

    Attributes:
        rect (pygame.Rect): The rectangle representing the platform's position and size.
        image (pygame.Surface): The image used to render the platform.
    """
    def __init__(self, position: Tuple[int, int], size: Tuple[int, int] = (150, 30)) -> None:
        """
        Initialize a Platform object.

        Args:
            position (Tuple[int, int]): The (x, y) position of the platform's top-left corner.
            size (Tuple[int, int], optional): The (width, height) of the platform. Defaults to (150, 30).
        """
        self.rect = pygame.Rect(position, size)
        self.image = load_image('platform.jpeg', size)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the platform on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw the platform on.
        """
        surface.blit(self.image, self.rect.topleft)

    def collides_with(self, rect: pygame.Rect) -> bool:
        """
        Check if the given rect collides with this platform.

        Args:
            rect (pygame.Rect): The rectangle to check collision with.

        Returns:
            bool: True if there is a collision, False otherwise.
        """
        return self.rect.colliderect(rect) 