import pygame
import random
import math
from pygame.locals import *
import sys
from playerClass import Player

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 50

class Item:
    def __init__(self, name, item_type, position, size=(50, 50), sprite=None):
        self.name = name
        self.item_type = item_type
        self.is_picked_up = False
        self.gravity = 0.8
        self.y_velocity = 0
        
        # Handle sprite and image initialization
        self.sprite = sprite.copy() if sprite else None
        self.original_image = self.sprite if self.sprite else pygame.Surface(size)
        if not self.sprite:
            self.original_image.fill((255, 0, 0))  # Red color for items without sprite
        self.image = self.original_image.copy()
        
        # Initialize rect and position
        self.rect = self.image.get_rect(center=position)
        
        # Equipment and animation properties
        self.equipped_offset = (50, 90)  # Offset when equipped
        self.rotation_angle = 0
        self.attack_animation = False
        self.attack_progress = 0
        self.attack_speed = 0.2  # Speed of the attack animation

    def draw(self, screen, player_position=None):
        if self.is_picked_up:
            if player_position and self.item_type == "Weapon":
                # Calculate the position based on player position and rotation
                center_x = player_position[0] + self.equipped_offset[0]
                center_y = player_position[1] + self.equipped_offset[1]
                
                # Apply attack animation if active
                if self.attack_animation:
                    self.attack_progress += self.attack_speed
                    if self.attack_progress >= 1:
                        self.attack_animation = False
                        self.attack_progress = 0
                    
                    # Add a swing animation
                    swing_angle = 45 * (1 - self.attack_progress)  # Swing from 45 to 0 degrees
                    self.rotation_angle += swing_angle
                
                # Rotate the image
                rotated_image = pygame.transform.rotate(self.original_image, self.rotation_angle)
                rotated_rect = rotated_image.get_rect(center=(center_x, center_y))
                screen.blit(rotated_image, rotated_rect)
                self.rect = rotated_rect  # Update the rect for collision detection
            elif player_position and self.item_type == "Key" and self.sprite:
                screen.blit(self.sprite, (player_position[0] + self.equipped_offset[0],
                                        player_position[1] + self.equipped_offset[1]))
        else:
            if self.item_type == "Weapon":
                screen.blit(self.image, self.rect.topleft)
            elif self.item_type == "Key" and self.sprite:
                screen.blit(self.sprite, self.rect.topleft)

    def rotate(self, angle):
        self.rotation_angle = math.degrees(angle)
        self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def start_attack(self):
        self.attack_animation = True
        self.attack_progress = 0

    def is_collision(self, enemy):
        if not self.attack_animation:
            return False
        # Create a larger hitbox during attack
        attack_rect = self.rect.inflate(20, 20)
        return attack_rect.colliderect(enemy.rect)

    def interact(self, player):
        if self.is_collision(player):
            if self.item_type == "Key" and not self.is_picked_up:
                player.pick_up_key(self)
                self.is_picked_up = True
            elif self.item_type == "Weapon" and player.has_key and not self.is_picked_up:
                player.pick_up_item(self)
                player.has_key = False
                self.is_picked_up = True
            elif self.item_type == "Weapon" and not player.has_key:
                print(f"You need a key to pick up {self.name}.")

    def apply_gravity(self):
        if not self.is_picked_up:
            self.y_velocity += self.gravity
            self.rect.y += self.y_velocity

            floor_level = SCREEN_HEIGHT - self.rect.height - 50
            if self.rect.y >= floor_level:
                self.rect.y = floor_level
                self.y_velocity = 0

def load_sprite(image_path, size):
    sprite = pygame.image.load(image_path).convert_alpha()
    return pygame.transform.scale(sprite, size)

def spawn_key():
    key_sprite = load_sprite("key_sprite.png", (50, 50))
    return Item("Golden Key", "Key", (random.randint(50, SCREEN_WIDTH - 50), SCREEN_HEIGHT - 100), (50, 50), key_sprite)

def spawn_weapon():
    sword_sprite = load_sprite("sword.png", (100, 100))  # Load the sword sprite
    return Item("Sword", "Weapon", (random.randint(50, SCREEN_WIDTH - 50), SCREEN_HEIGHT - 100), (100, 100), sword_sprite)  # Spawn with the sprite

def main_game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Player and Items Interaction")
    clock = pygame.time.Clock()

    player = Player("Hero", (100, 100), PLAYER_SIZE)

    key = spawn_key()
    weapon = spawn_weapon()

    running = True
    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    player.jump()
                elif event.key == K_d:
                    player.move_right()
                elif event.key == K_a:
                    player.move_left()
                elif event.key == K_e:
                    key.interact(player)
                    weapon.interact(player)

            elif event.type == KEYUP:
                if event.key == K_d:
                    player.stop_move_right()
                elif event.key == K_a:
                    player.stop_move_left()

        key.apply_gravity()
        weapon.apply_gravity()

        player.update()
        screen.blit(player.image, player.rect)

        key.draw(screen)
        weapon.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_game_loop()
