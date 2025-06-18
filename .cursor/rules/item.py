"""
Item class for the Escape-WE-Project game.
Handles weapons, keys, and other collectible items.
"""

import pygame
import math
import random
from typing import Optional, Tuple
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ITEM_SIZE, WEAPON_SIZE, KEY_SIZE,
    ITEM_GRAVITY, load_image, ASSETS
)


class Item:
    """
    Base item class for weapons, keys, and other collectibles.
    
    Attributes:
        name: Item name
        item_type: Type of item (Weapon, Key, etc.)
        is_picked_up: Whether item has been collected
        rect: Pygame rect for collision detection
        image: Item sprite image
    """
    
    def __init__(self, name: str, item_type: str, position: Tuple[int, int], 
                 size: Tuple[int, int] = ITEM_SIZE, sprite: Optional[pygame.Surface] = None):
        """
        Initialize an item.
        
        Args:
            name: Item name
            item_type: Type of item (Weapon, Key, etc.)
            position: Starting position (x, y)
            size: Item size (width, height)
            sprite: Optional sprite image
        """
        self.name = name
        self.item_type = item_type
        self.is_picked_up = False
        
        # Physics
        self.gravity = ITEM_GRAVITY
        self.y_velocity = 0
        
        # Sprite handling
        self.sprite = sprite.copy() if sprite else None
        self.original_image = self.sprite if self.sprite else pygame.Surface(size)
        if not self.sprite:
            self.original_image.fill((255, 0, 0))  # Red fallback
        self.image = self.original_image.copy()
        
        # Position and collision
        self.rect = self.image.get_rect(center=position)
        
        # Equipment properties
        self.equipped_offset = (50, 90)
        self.rotation_angle = 0
        
        # Combat properties
        self.attack_animation = False
        self.attack_progress = 0
        self.attack_speed = 0.2

    def draw(self, screen: pygame.Surface, player_position: Optional[Tuple[int, int]] = None) -> None:
        """
        Draw the item on the screen.
        
        Args:
            screen: Pygame surface to draw on
            player_position: Player position for equipped items
        """
        if self.is_picked_up and player_position:
            self._draw_equipped(screen, player_position)
        else:
            self._draw_world(screen)

    def _draw_equipped(self, screen: pygame.Surface, player_position: Tuple[int, int]) -> None:
        """Draw item when equipped by player."""
        if self.item_type == "Weapon":
            # Calculate position based on player and rotation
            center_x = player_position[0] + self.equipped_offset[0]
            center_y = player_position[1] + self.equipped_offset[1]
            
            # Handle attack animation
            if self.attack_animation:
                self.attack_progress += self.attack_speed
                if self.attack_progress >= 1:
                    self.attack_animation = False
                    self.attack_progress = 0
                
                # Add swing animation
                swing_angle = 45 * (1 - self.attack_progress)
                self.rotation_angle += swing_angle
            
            # Rotate and draw
            rotated_image = pygame.transform.rotate(self.original_image, self.rotation_angle)
            rotated_rect = rotated_image.get_rect(center=(center_x, center_y))
            screen.blit(rotated_image, rotated_rect)
            self.rect = rotated_rect
            
        elif self.item_type == "Key" and self.sprite:
            # Draw key at equipped position
            screen.blit(self.sprite, (
                player_position[0] + self.equipped_offset[0],
                player_position[1] + self.equipped_offset[1]
            ))

    def _draw_world(self, screen: pygame.Surface) -> None:
        """Draw item in the world (not equipped)."""
        if self.item_type == "Weapon":
            screen.blit(self.image, self.rect.topleft)
        elif self.item_type == "Key" and self.sprite:
            screen.blit(self.sprite, self.rect.topleft)

    def rotate(self, angle: float) -> None:
        """
        Rotate the item image.
        
        Args:
            angle: Rotation angle in radians
        """
        self.rotation_angle = math.degrees(angle)
        self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def start_attack(self) -> None:
        """Start the attack animation."""
        self.attack_animation = True
        self.attack_progress = 0

    def is_collision(self, entity) -> bool:
        """
        Check collision with another entity.
        
        Args:
            entity: Entity to check collision with
            
        Returns:
            True if collision detected
        """
        if self.item_type == "Weapon":
            if not self.attack_animation:
                return False
            # Create larger hitbox during attack
            attack_rect = self.rect.inflate(20, 20)
            return attack_rect.colliderect(entity.rect)
        else:
            # For keys and other items, just use rect collision
            return self.rect.colliderect(entity.rect)

    def interact(self, player) -> None:
        """
        Handle interaction with player.
        
        Args:
            player: Player instance
        """
        if not self.is_collision(player):
            return
            
        if self.item_type == "Key" and not self.is_picked_up:
            player.pick_up_key(self)
            self.is_picked_up = True
        elif self.item_type == "Weapon" and player.has_key and not self.is_picked_up:
            player.pick_up_item(self)
            player.has_key = False
            self.is_picked_up = True
        elif self.item_type == "Weapon" and not player.has_key:
            print(f"You need a key to pick up {self.name}.")

    def apply_gravity(self) -> None:
        """Apply gravity to the item if not picked up."""
        if self.is_picked_up:
            return
        self.y_velocity += self.gravity
        self.rect.y += int(self.y_velocity)
        # Check floor collision
        floor_level = SCREEN_HEIGHT - self.rect.height - 50
        if self.rect.y >= floor_level:
            self.rect.y = floor_level
            self.y_velocity = 0


def spawn_key() -> Item:
    """
    Create a new key item at a random position.
    
    Returns:
        New key item
    """
    key_sprite = load_image(ASSETS['key'], KEY_SIZE)
    x = random.randint(50, SCREEN_WIDTH - 50)
    y = SCREEN_HEIGHT - 100
    return Item("Golden Key", "Key", (x, y), KEY_SIZE, key_sprite)


def spawn_weapon() -> Item:
    """
    Create a new weapon item.
    
    Returns:
        New weapon item
    """
    sword_sprite = load_image(ASSETS['sword'], WEAPON_SIZE)
    return Item("Sword", "Weapon", (50, SCREEN_HEIGHT - 100), WEAPON_SIZE, sword_sprite) 