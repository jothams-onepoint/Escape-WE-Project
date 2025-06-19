"""
Player class for the Escape-WE-Project game.
Handles player movement, combat, inventory, and interactions.
"""

import pygame
import math
import time
import random
from typing import Optional, Tuple
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SIZE, PLAYER_SPEED, 
    GRAVITY, JUMP_VELOCITY, PLAYER_LIVES, PLAYER_MAX_HEALTH,
    WHITE, BLACK, load_image, ASSETS
)


class Player(pygame.sprite.Sprite):
    """
    Player character class with movement, combat, and inventory capabilities.
    
    Attributes:
        name: Player's name
        position: Current position as pygame.Vector2
        health: Current health points
        lives: Remaining lives
        equipped_item: Currently equipped item
        has_key: Whether player has a key
        inventory: List of items in inventory
    """
    
    def __init__(self, name: str, position: Tuple[int, int], size: int = PLAYER_SIZE):
        """
        Initialize the player.
        
        Args:
            name: Player's name
            position: Starting position (x, y)
            size: Player size (defaults to PLAYER_SIZE)
        """
        super().__init__()
        self.name = name
        self.size = size
        
        # Load and scale player sprite
        self.image = load_image(ASSETS['player_sprite'], (200, 200))
        self.rect = self.image.get_rect(topleft=position)
        
        # Position and movement
        self.position = pygame.Vector2(position)
        self.velocity_y = 0
        self.speed = PLAYER_SPEED
        
        # State flags
        self.is_jumping = False
        self.is_moving_right = False
        self.is_moving_left = False
        self.facing_right = True
        
        # Health and lives
        self.health = PLAYER_MAX_HEALTH
        self.lives = PLAYER_LIVES
        
        # Inventory and equipment
        self.equipped_item = None
        self.equipped_item_angle = 0
        self.equipped_item_distance = 50
        self.has_key = False
        self.inventory = []
        
        # Combat
        self.last_attack_time = 0
        self.attack_cooldown = 0.5
        
        # Mouse tracking
        self.cursor_pos = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def pick_up_key(self, key) -> None:
        """
        Pick up a key item.

        Args:
            key: The key item to pick up.
        """
        self.has_key = True
        print(f"{self.name} picked up the key!")

    def jump(self) -> None:
        """Make the player jump if not already jumping."""
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = JUMP_VELOCITY

    def move_right(self) -> None:
        """Start moving right."""
        self.is_moving_right = True
        self.facing_right = True

    def move_left(self) -> None:
        """Start moving left."""
        self.is_moving_left = True
        self.facing_right = False

    def stop_move_right(self) -> None:
        """Stop moving right."""
        self.is_moving_right = False

    def stop_move_left(self) -> None:
        """Stop moving left."""
        self.is_moving_left = False

    def update(self, is_scrolling: bool = False) -> None:
        """
        Update player position and state.
        
        Args:
            is_scrolling: Whether the screen is currently scrolling
        """
        # Handle jumping and gravity
        if self.is_jumping:
            self.velocity_y += GRAVITY
            self.position.y += self.velocity_y
            
            # Check if landed
            if self.position.y >= SCREEN_HEIGHT - self.rect.height:
                self.position.y = SCREEN_HEIGHT - self.rect.height
                self.is_jumping = False
                self.velocity_y = 0

        # Handle horizontal movement
        if self.is_moving_right:
            self.position.x += self.speed
        elif self.is_moving_left:
            self.position.x -= self.speed

        # Handle boundary constraints
        self._constrain_position(is_scrolling)
        
        # Update rect position
        self.rect.topleft = (int(self.position.x), int(self.position.y))

        # Update equipped item position
        if self.equipped_item:
            self._update_equipped_item_position()

    def _constrain_position(self, is_scrolling: bool) -> None:
        """
        Constrain player position within screen boundaries.
        
        Args:
            is_scrolling: Whether the screen is currently scrolling
        """
        if is_scrolling:
            # Keep player in center area during scrolling
            left_boundary = int(SCREEN_WIDTH * 0.25)
            right_boundary = int(SCREEN_WIDTH * 0.75) - self.rect.width
            
            if self.position.x < left_boundary:
                self.position.x = left_boundary
            elif self.position.x > right_boundary:
                self.position.x = right_boundary
        else:
            # Normal boundary constraints
            if self.position.x < 0:
                self.position.x = 0
            elif self.position.x > SCREEN_WIDTH - self.rect.width:
                self.position.x = SCREEN_WIDTH - self.rect.width

        # Vertical boundaries
        if self.position.y < 0:
            self.position.y = 0
        elif self.position.y > SCREEN_HEIGHT - self.rect.height:
            self.position.y = SCREEN_HEIGHT - self.rect.height

    def _update_equipped_item_position(self) -> None:
        """Update the position of the equipped item based on cursor position."""
        if not self.equipped_item:
            return
            
        player_center = self.position + pygame.Vector2(self.rect.width // 2, self.rect.height // 2)
        dx = self.cursor_pos.x - player_center.x
        dy = self.cursor_pos.y - player_center.y
        angle = math.atan2(dy, dx)
        distance = min(math.hypot(dx, dy), self.equipped_item_distance)

        self.equipped_item_angle = angle
        self.equipped_item.rect.center = (
            player_center.x + distance * math.cos(angle),
            player_center.y + distance * math.sin(angle)
        )
        self.equipped_item.rotate(angle)

    def take_damage(self, damage: float) -> bool:
        """
        Apply damage to the player.
        
        Args:
            damage: Amount of damage to apply
            
        Returns:
            True if player died, False otherwise
        """
        self.health -= damage
        if self.health <= 0:
            self.lives -= 1
            self.health = PLAYER_MAX_HEALTH
            print(f"Lost a life! Lives left: {self.lives}")
            
            if self.lives <= 0:
                print("Game Over! You have lost.")
                self.lives = PLAYER_LIVES
                self.health = PLAYER_MAX_HEALTH
                return True
        return False

    def equip_item(self, item) -> None:
        """
        Equip an item.
        
        Args:
            item: Item to equip
        """
        self.equipped_item = item
        if item:
            print(f"{self.name} equipped {item.item_type}")

    def unequip_item(self):
        """
        Unequip the currently equipped item.
        
        Returns:
            The unequipped item or None
        """
        if self.equipped_item:
            item = self.equipped_item
            print(f"{self.name} unequipped {item.item_type}")
            self.equipped_item = None
            return item
        return None

    def attack(self, current_time: float) -> int:
        """
        Perform an attack with the equipped weapon.
        
        Args:
            current_time: Current game time
            
        Returns:
            Damage dealt (0 if no attack performed)
        """
        if (self.equipped_item and 
            self.equipped_item.item_type == "Weapon" and
            current_time - self.last_attack_time >= self.attack_cooldown):
            self.last_attack_time = current_time
            self.equipped_item.start_attack()
            # Crit logic: 25% chance for 20 damage, else 10 damage
            if random.random() < 0.25:
                return 20  # Crit
            return 10  # Normal hit
        return 0

    def update_cursor_pos(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Update cursor position for weapon aiming.
        
        Args:
            mouse_pos: Current mouse position (x, y)
        """
        self.cursor_pos.x = mouse_pos[0]
        self.cursor_pos.y = mouse_pos[1]
        if self.equipped_item:
            self._update_equipped_item_position()

    def drop_item(self):
        """
        Drop the currently equipped item.
        
        Returns:
            The dropped item or None
        """
        if self.equipped_item:
            # Create a new item at player's position
            from item import Item  # Import here to avoid circular imports
            dropped_item = Item(
                self.equipped_item.name,
                self.equipped_item.item_type,
                (self.rect.centerx, self.rect.centery),
                sprite=self.equipped_item.original_image.copy()
            )
            dropped_item.is_picked_up = False
            self.equipped_item = None
            return dropped_item
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the player on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Draw player sprite with proper facing direction
        if self.is_moving_right:
            flipped_image = pygame.transform.flip(self.image, True, False)
            flipped_rect = flipped_image.get_rect()
            flipped_rect.topleft = self.rect.topleft
            screen.blit(flipped_image, flipped_rect)
        else:
            screen.blit(self.image, self.rect)

        # Draw equipped item
        if self.equipped_item:
            self.equipped_item.draw(screen, self.rect.topleft, self.facing_right) 