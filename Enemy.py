"""
Enemy class for the Escape-WE-Project game.
Handles enemy movement, behavior, and combat.
"""

import pygame
import random
import time
from typing import Tuple
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_SIZE, ENEMY_SPEED, 
    ENEMY_MOVE_DURATION, load_image, ASSETS
)

class Enemy:
    """
    Enemy class with movement and combat capabilities.
    """
    def __init__(self, x: int = None, y: int = None):
        self.enemy_type = random.randint(1, 3)
        self.width = ENEMY_SIZE
        self.height = ENEMY_SIZE
        if x is None:
            x = random.randint(0, SCREEN_WIDTH * 3 - self.width)
        if y is None:
            y = SCREEN_HEIGHT - self.height
        self.x = x
        self.y = y
        self.speed = ENEMY_SPEED
        self.current_direction = random.choice([-1, 1])
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
        return load_image(image_path, (ENEMY_SIZE, ENEMY_SIZE))

    def move(self) -> None:
        if self.move_timer <= 0:
            self.current_direction = random.choice([-1, 1])
            self.move_timer = self.move_duration
        self.x += self.current_direction * self.speed
        self.move_timer -= 1

    def update(self) -> None:
        self.move()
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen: pygame.Surface) -> None:
        # Handle shake animation
        shake_offset = (0, 0)
        if self.is_shaking:
            if time.time() < self.shake_timer:
                shake_offset = (random.randint(-8, 8), random.randint(-8, 8))
            else:
                self.is_shaking = False
        draw_rect = self.rect.move(shake_offset)
        if self.current_direction == 1:
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