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
    WHITE, BLACK, load_image, ASSETS, WEAPON_SIZE
)
from inventory import Inventory
from item import Item


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
    
    def __init__(self, name: str, position: Tuple[int, int], size: Tuple[int, int] = PLAYER_SIZE):
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
        self.image = load_image(ASSETS['player'], self.size)
        self.rect = self.image.get_rect(topleft=position)

        # Create a smaller hitbox for damage detection
        self.hitbox = self.rect.inflate(-self.rect.width * 0.5, -self.rect.height * 0.4)
        
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

        # Invulnerability and shaking state
        self.is_invulnerable: bool = False
        self.invulnerable_until: float = 0.0
        self.is_shaking: bool = False
        self.shake_end_time: float = 0.0
        self._shake_offset: Tuple[int, int] = (0, 0)
        self._last_shake_time: float = 0.0

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

    def update(self, is_scrolling: bool = False, platforms: list = None) -> None:
        """
        Update player state, including movement, gravity, and animations.
        
        Args:
            is_scrolling: True if the screen is scrolling
            platforms: A list of platform objects for collision detection
        """
        # --- Handle Timers and Effects ---
        current_time = time.time()
        if self.is_shaking and current_time >= self.shake_end_time:
            self.is_shaking = False
        if self.is_invulnerable and current_time >= self.invulnerable_until:
            self.is_invulnerable = False
        
        # Update shake offset if shaking
        if self.is_shaking:
            if current_time - self._last_shake_time > 0.02:
                self._shake_offset = (random.randint(-8, 8), random.randint(-8, 8))
                self._last_shake_time = current_time
        else:
            self._shake_offset = (0, 0)

        # --- Horizontal Movement ---
        if self.is_moving_right:
            self.position.x += self.speed
        if self.is_moving_left:
            self.position.x -= self.speed

        # --- Vertical Movement & Gravity ---
        self.velocity_y += GRAVITY
        self.position.y += self.velocity_y
        self.rect.topleft = (int(self.position.x), int(self.position.y))

        # --- Collision Detection ---
        # Ground collision
        landed = False
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.position.y = self.rect.y
            self.velocity_y = 0
            self.is_jumping = False
            landed = True
            
        # Platform collision
        if not landed and platforms:
            for platform in platforms:
                # Check for downward collision and that player is above platform
                if (self.velocity_y > 0 and 
                    self.rect.colliderect(platform.rect) and
                    self.rect.bottom <= platform.rect.top + self.velocity_y): # Check against top of platform
                    self.rect.bottom = platform.rect.top
                    self.position.y = self.rect.y
                    self.velocity_y = 0
                    self.is_jumping = False
                    break # Stop checking after landing on one platform

        self._constrain_position(is_scrolling)
        
        # After all position changes, update the rect and hitbox
        self.rect.topleft = (int(self.position.x), int(self.position.y))
        self.hitbox.center = self.rect.center
        
        # --- Update Equipped Item ---
        self._update_equipped_item_position()

    def _constrain_position(self, is_scrolling: bool) -> None:
        """
        Constrain player position to screen boundaries.
        
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
            
        player_center = self.rect.center
        dx = self.cursor_pos.x - player_center[0]
        dy = self.cursor_pos.y - player_center[1]
        angle = math.atan2(dy, dx)
        distance = min(math.hypot(dx, dy), self.equipped_item_distance)

        self.equipped_item_angle = angle
        self.equipped_item.rect.center = (
            player_center[0] + distance * math.cos(angle),
            player_center[1] + distance * math.sin(angle)
        )
        self.equipped_item.rotate(angle)

    def take_damage(self, damage: float) -> bool:
        """
        Apply damage to the player, with invulnerability and shaking logic.
        Args:
            damage: Amount of damage to apply (ignored, always 10)
        Returns:
            True if player died, False otherwise
        """
        current_time = time.time()
        if self.is_invulnerable:
            return False
        # Always apply 10 damage per hit
        self.health -= 10
        # Start shaking for 0.7s
        self.is_shaking = True
        self.shake_end_time = current_time + 0.7
        # Become invulnerable for 0.7 + 0.3 = 1.0s
        self.is_invulnerable = True
        self.invulnerable_until = current_time + 1.0
        if self.health <= 0:
            self.lives -= 1
            self.health = PLAYER_MAX_HEALTH
            print(f"Lost a life! Lives left: {self.lives}")
            if self.lives <= 0:
                print("Game Over! You have lost.")
                # Do not reset lives here; let the game handle it on new game
                return True
        return False

    def equip_item(self, item) -> None:
        """
        Equip an item.
        Args:
            item: Item to equip
        """
        if item:
            item.reset_for_equip(self.rect.center)
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
            dropped_item = self.equipped_item
            dropped_item.reset_for_drop((self.rect.centerx, self.rect.centery))
            self.equipped_item = None
            return dropped_item
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the player on the screen, with shaking (no flicker) and invulnerability effect.
        Args:
            screen: Pygame surface to draw on
        """
        # Calculate draw position with shake offset
        draw_pos = (self.rect.x + self._shake_offset[0], self.rect.y + self._shake_offset[1])
        
        current_image = self.image
        if self.facing_right:
            current_image = pygame.transform.flip(self.image, True, False)

        # Handle invulnerability visual effect (flashing)
        if self.is_invulnerable:
            # Flashes every ~100ms
            if int(time.time() * 10) % 2 == 0:
                current_image.set_alpha(128)
            else:
                current_image.set_alpha(255)
        else:
            current_image.set_alpha(255)
            
        screen.blit(current_image, draw_pos)
        
        # Draw equipped item
        if self.equipped_item:
            self.equipped_item.draw(screen, draw_pos, self.facing_right)

    def _update_animation(self) -> None:
        """Placeholder for future animation logic."""
        # This can be expanded with sprite sheets etc.
        pass
