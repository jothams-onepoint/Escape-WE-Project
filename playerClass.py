import pygame
from pygame.locals import *
import time
import math
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 50
PLAYER_COLOR = (0, 128, 255)
GRAVITY = 0.5
JUMP_VELOCITY = -15


class Player(pygame.sprite.Sprite):
    def __init__(self, name, position, size):
        super().__init__()
        self.name = name
        self.image = pygame.image.load('player_sprite.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect(topleft=position)
        self.speed = 5
        self.has_key = False
        self.equipped_item = None
        self.equipped_item_angle = 0
        self.equipped_item_distance = 50  # Maximum distance the sword can be from the player
        self.last_attack_time = 0
        self.attack_cooldown = 0.5  # Reduced cooldown for more responsive combat
        self.cursor_pos = pygame.Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.attack_sound = None

        # Player attributes
        self.playerLives = 3
        self.health = 100
        self.inventory = []
        self.current_item = None
        self.has_key = False
        self.holding_shield = False

        # Position and movement attributes
        self.position = pygame.Vector2(position)
        self.velocity_y = 0
        self.is_jumping = False
        self.is_moving_right = False
        self.is_moving_left = False
        self.facing_right = True

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = JUMP_VELOCITY

    def move_right(self):
        self.is_moving_right = True
        self.facing_right = True

    def move_left(self):
        self.is_moving_left = True
        self.facing_right = False

    def stop_move_right(self):
        self.is_moving_right = False

    def stop_move_left(self):
        self.is_moving_left = False

    def update(self, is_scrolling):
        if self.is_jumping:
            self.velocity_y += GRAVITY
            self.position.y += self.velocity_y
            if self.position.y >= SCREEN_HEIGHT - self.rect.height:
                self.position.y = SCREEN_HEIGHT - self.rect.height
                self.is_jumping = False
                self.velocity_y = 0

        if self.is_moving_right:
            self.position.x += self.speed
        elif self.is_moving_left:
            self.position.x -= self.speed

        if is_scrolling:
            if self.position.x < int(SCREEN_WIDTH * 0.25):
                self.position.x = int(SCREEN_WIDTH * 0.25)
            elif self.position.x > int(SCREEN_WIDTH * 0.75) - self.rect.width:
                self.position.x = int(SCREEN_WIDTH * 0.75)- self.rect.width
        else:
            if self.position.x < 0:
                self.position.x = 0
            elif self.position.x > SCREEN_WIDTH- self.rect.width:
                self.position.x = SCREEN_WIDTH - self.rect.width
        if self.position.y < 0:
            self.position.y = 0
        elif self.position.y > SCREEN_HEIGHT - self.rect.height:
            self.position.y = SCREEN_HEIGHT - self.rect.height

        self.rect.topleft = self.position

        # Always update equipped item position
        if self.equipped_item:
            self.update_equipped_item_position()

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 100
            self.playerLives -= 1
            print(f"Lost a life! Lives left: {self.playerLives}")
            if self.playerLives <= 0:
                print("Unfortunately, you have lost.")
                self.playerLives = 3
                self.health = 100
                return 1

    def update_equipped_item_position(self):
        if self.equipped_item:
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

    def use_item(self):
        if self.current_item:
            print(f"{self.name} uses {self.current_item.name}!")
            if self.current_item.item_type == "Weapon":
                print(f"Attacking with {self.current_item.name}!")

    def pick_up_key(self, key):
        if key.is_collision(self) and not key.is_picked_up:
            print(f"{self.name} picks up {key.name}!")
            key.is_picked_up = True
            self.has_key = True
            self.current_item = key

    def pick_up_item(self, item):
        if item.is_collision(self) and self.has_key and not item.is_picked_up:
            print(f"{self.name} picks up {item.name}!")
            item.is_picked_up = True
            self.inventory.append(item)
            self.current_item = item

    def equip_item(self, item):
        self.equipped_item = item
        if item:
            print(f"{self.name} equipped {item.item_type}")

    def unequip_item(self):
        if self.equipped_item:
            print(f"{self.name} unequipped {self.equipped_item.item_type}")
            item = self.equipped_item
            self.equipped_item = None
            return item
        return None

    def attack(self, current_time):
        if self.equipped_item and self.equipped_item.item_type == "Weapon":
            if current_time - self.last_attack_time >= self.attack_cooldown:
                self.last_attack_time = current_time
                self.equipped_item.start_attack()
                if self.attack_sound:
                    self.attack_sound.play()
                return 50  # Return damage dealt
        return 0

    def draw(self, screen):
        if self.is_moving_right:
            flipped_image = pygame.transform.flip(self.image, True, False)
            flipped_rect = flipped_image.get_rect()
            flipped_rect.topleft = self.rect.topleft
            screen.blit(flipped_image, flipped_rect)
        else:
            screen.blit(self.image, self.rect)

        if self.equipped_item:
            self.equipped_item.draw(screen, self.rect.topleft)

    def update_cursor_pos(self, mouse_pos):
        self.cursor_pos.x = mouse_pos[0]
        self.cursor_pos.y = mouse_pos[1]
        if self.equipped_item:
            self.update_equipped_item_position()

    def drop_item(self):
        if self.equipped_item:
            # Create a new item at the player's position
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

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Player Class Demo")
    clock = pygame.time.Clock()

    player = Player("Hero", (100, 100), PLAYER_SIZE)

    running = True
    while running:
        screen.fill((255, 255, 255))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    player.jump()
                if event.key == K_d:
                    player.move_right()
                if event.key == K_a:
                    player.move_left()

            elif event.type == KEYUP:
                if event.key == K_d:
                    player.stop_move_right()
                if event.key == K_a:
                    player.stop_move_left()

        player.update()
        player.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()