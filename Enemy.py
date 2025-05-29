import sys
import pygame
import random
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Set display mode
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enemy Class Demo")

# Load and scale enemy sprites
enemy1_image = pygame.image.load('enemy1.png').convert_alpha()
enemy2_image = pygame.image.load('enemy2.png').convert_alpha()
enemy3_image = pygame.image.load('enemy3.png').convert_alpha()

enemy1_image = pygame.transform.scale(enemy1_image, (100, 100))
enemy2_image = pygame.transform.scale(enemy2_image, (100, 100))
enemy3_image = pygame.transform.scale(enemy3_image, (100, 100))

class Enemy:
    def __init__(self):
        self.enemy_type = random.randint(1, 3)  # Randomly choose enemy type
        self.width = 100
        self.height = 100
        self.x = random.randint(0, SCREEN_WIDTH*3 - self.width)  # Randomize initial x position
        self.y = SCREEN_HEIGHT - self.height  # Position at bottom of the screen
        self.speed = 1
        self.image = self.get_enemy_image()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

        # Movement attributes
        self.current_direction = random.choice([-1, 1])
        self.move_timer = 0
        self.move_duration = 60

    def get_enemy_image(self):
        if self.enemy_type == 1:
            return enemy1_image
        elif self.enemy_type == 2:
            return enemy2_image
        elif self.enemy_type == 3:
            return enemy3_image
        else:
            return enemy1_image  # Default to enemy1 if invalid type

    def move(self):
        if self.move_timer <= 0:
            self.current_direction = random.choice([-1, 1])
            self.move_timer = self.move_duration

        self.x += self.current_direction * self.speed
        self.move_timer -= 1
        # self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

    def update(self):
        self.move()
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        # Determine if the image needs flipping based on current direction
        if self.current_direction == 1:
            screen.blit(self.image, self.rect)
        else:
            flipped_image = pygame.transform.flip(self.image, True, False)
            screen.blit(flipped_image, self.rect)

if __name__ == "__main__":
    clock = pygame.time.Clock()

    # Create initial enemies
    enemies = [Enemy() for _ in range(3)]

    # Main loop
    running = True
    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        for enemy in enemies:
            enemy.update()
            enemy.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
