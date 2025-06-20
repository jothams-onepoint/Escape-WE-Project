"""
Enemy class for the Escape-WE-Project game.
Handles enemy movement, behavior, and combat.
"""

import pygame
import random
import time
from typing import Tuple, Optional
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_SIZE, ENEMY_SPEED, 
    ENEMY_MOVE_DURATION, load_image, ASSETS, GRAVITY
)
from player import Player
from platform import Platform

class Enemy:
    """
    Enemy class with movement and combat capabilities.
    """
    def __init__(self, x: int = None, y: int = None, platform: Optional[Platform] = None):
        self.enemy_type = random.randint(1, 3)
        self.width, self.height = ENEMY_SIZE
        self.x = x if x is not None else random.randint(0, SCREEN_WIDTH * 3 - self.width)
        self.y = y if y is not None else SCREEN_HEIGHT - self.height
        self.speed = ENEMY_SPEED * random.choice([-1, 1])
        self.move_counter = 0
        self.velocity_y = 0
        self.initial_platform = platform
        self.move_timer = 0
        self.move_duration = ENEMY_MOVE_DURATION
        self.image = self._get_enemy_image()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.health = 50
        self.max_health = 50
        self.drops_key = random.choice([True, False])
        self.shake_timer = 0.0  # Time when shake ends
        self.is_shaking = False

    def _get_enemy_image(self) -> pygame.Surface:
        enemy_images = {
            1: ASSETS['enemy1'],
            2: ASSETS['enemy2'],
            3: ASSETS['enemy3']
        }
        image_path = enemy_images.get(self.enemy_type, ASSETS['enemy1'])
        image = load_image(image_path, ENEMY_SIZE)
        return image

    def move(self) -> None:
        """Move the enemy, staying on its platform if it has one."""
        if self.initial_platform:
            # Move the enemy
            self.x += self.speed

            # Get platform boundaries
            left_bound = self.initial_platform.rect.left
            right_bound = self.initial_platform.rect.right - self.rect.width

            # Check boundaries and reverse direction
            if self.x <= left_bound:
                self.x = left_bound  # Clamp position to prevent getting stuck
                self.speed *= -1
            elif self.x >= right_bound:
                self.x = right_bound # Clamp position
                self.speed *= -1
        else:
            # Original behavior if no platform
            self.x += self.speed
            self.move_counter += 1
            if self.move_counter > ENEMY_MOVE_DURATION:
                self.speed *= -1
                self.move_counter = 0

    def update(self) -> None:
        """Update enemy position and state."""
        self.move()

        # Apply gravity ONLY if the enemy is not on a platform
        if self.initial_platform is None:
            self.velocity_y += GRAVITY
            self.y += self.velocity_y
        
        # Update rect position from self.x and self.y
        self.rect.topleft = (self.x, self.y)

        # Collision with the ground for ground-based enemies
        if self.initial_platform is None and self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.y = self.rect.y
            self.velocity_y = 0

    def draw(self, screen: pygame.Surface) -> None:
        # Handle shake animation
        shake_offset = (0, 0)
        if self.is_shaking:
            if time.time() < self.shake_timer:
                shake_offset = (random.randint(-8, 8), random.randint(-8, 8))
            else:
                self.is_shaking = False
        draw_rect = self.rect.move(shake_offset)
        if self.speed > 0:
            screen.blit(self.image, draw_rect)
        else:
            flipped_image = pygame.transform.flip(self.image, True, False)
            screen.blit(flipped_image, draw_rect)
        bar_width = self.rect.width
        bar_height = 6
        health_ratio = max(self.health, 0) / self.max_health
        health_bar_width = int(bar_width * health_ratio)
        bar_x = draw_rect.x
        bar_y = draw_rect.y - bar_height - 4
        pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, health_bar_width, bar_height))

    def take_damage(self, damage: int) -> bool:
        self.health -= damage
        # Start shake animation for 300ms
        self.is_shaking = True
        self.shake_timer = time.time() + 0.2
        if self.health <= 0:
            print(f"Enemy defeated! Drops key: {self.drops_key}")
            return True
        return False

    def is_collision(self, entity) -> bool:
        return self.rect.colliderect(entity.rect) 