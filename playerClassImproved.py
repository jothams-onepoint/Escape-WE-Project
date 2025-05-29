import pygame
import sys
import math

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_LEVEL = 500

class Player:
    def __init__(self):
        self.playerLives = 3
        self.health = 100
        self.inventory = []
        self.current_item = None
        self.has_key = False
        self.holding_shield = False
        self.position = pygame.Vector2(400, GROUND_LEVEL)
        self.max_inventory_size = 10
        self.level = 1
        self.width = 50
        self.height = 100
        self.is_jumping = False
        self.jump_velocity = -15
        self.gravity = 1
        self.velocity_y = 0
        self.move_left = False
        self.move_right = False

    def move(self, direction):
        if direction == 'left':
            self.move_left = True
        elif direction == 'right':
            self.move_right = True

    def stop_move(self, direction):
        if direction == 'left':
            self.move_left = False
        elif direction == 'right':
            self.move_right = False

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.velocity_y = self.jump_velocity

    def update(self):
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.position.y += self.velocity_y
            if self.move_left:
                self.position.x -= 10
            if self.move_right:
                self.position.x += 10

            if self.position.y >= GROUND_LEVEL:
                self.position.y = GROUND_LEVEL
                self.is_jumping = False
                self.velocity_y = 0

    def attack(self, enemy):
        if self.current_item and self.current_item['type'] == 'weapon':
            enemy.health -= self.current_item['damage']
            if enemy.health <= 0:
                self.enemy_died(enemy)

    def defend(self, attack_strength):
        if self.holding_shield:
            pass  # Negate attack
        else:
            self.health -= attack_strength
            if self.health <= 0:
                self.playerLives -= 1
                if self.playerLives == 0:
                    print("Unfortunately, you have lost")
                else:
                    self.health = 100

    def interact_with_chest(self, chest):
        if self.has_key:
            if len(self.inventory) < self.max_inventory_size:
                self.inventory.append(chest.item)
            else:
                self.switch_inventory_item(chest.item)
        else:
            print("You must have a key to unlock this chest")

    def interact_with_door(self):
        if self.level >= 20:
            print("Game over. You win!")
        else:
            self.level += 1
            print("Level up")

    def switch_inventory_item(self, new_item):
        print("Inventory full. Do you want to switch an item in your inventory for this item (y/n)?")
        choice = input()
        if choice.lower() == 'y':
            print("Select the item number to replace:")
            for idx, item in enumerate(self.inventory):
                print(f"{idx}: {item['name']}")
            item_index = int(input())
            if 0 <= item_index < len(self.inventory):
                self.inventory[item_index] = new_item
            else:
                print("Invalid item number")
        else:
            print("Item not added to inventory")

    def enemy_died(self, enemy):
        if enemy.drops_key:
            self.has_key = True

    def set_current_item(self):
        print("Select an item to hold from your inventory:")
        for idx, item in enumerate(self.inventory):
            print(f"{idx}: {item['name']}")
        item_index = int(input())
        if 0 <= item_index < len(self.inventory):
            if self.inventory[item_index]['type'] == 'weapon':
                if self.current_item and self.current_item['type'] == 'weapon':
                    print("You can only hold one weapon at a time")
                else:
                    self.current_item = self.inventory[item_index]
            else:
                self.current_item = self.inventory[item_index]
        else:
            print("Invalid item number")

def draw_triangle(screen, color, position, size):
    half_size = size / 2
    points = [
        (position.x, position.y - half_size),  # Top point
        (position.x - half_size, position.y + half_size),  # Bottom left
        (position.x + half_size, position.y + half_size)  # Bottom right
    ]
    pygame.draw.polygon(screen, color, points)

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Player Test")

    # Create a Player instance
    player = Player()

    # Example enemy for testing
    class Enemy:
        def __init__(self):
            self.health = 100
            self.drops_key = True
            self.position = pygame.Vector2(200, GROUND_LEVEL)  # Arbitrary position
            self.size = 50  # Size of the enemy square

    enemy = Enemy()

    # Example item for testing
    class Item:
        def __init__(self, item_type, size):
            self.type = item_type
            self.size = size
            self.position = pygame.Vector2(600, GROUND_LEVEL)  # Arbitrary position

    chest = Item('chest', 70)
    weapon = Item('weapon', 40)
    key = Item('key', 20)

    # Handling player input (simplified):
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    player.move('left')
                elif event.key == pygame.K_d:
                    player.move('right')
                elif event.key == pygame.K_SPACE:
                    player.jump()
                elif event.key == pygame.K_e:
                    # Simulate interaction logic
                    player.attack(enemy)
                    print(f"Enemy health: {enemy.health}")
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    player.stop_move('left')
                elif event.key == pygame.K_d:
                    player.stop_move('right')

        # Update player status
        player.update()

        # Fill the screen with a color (white)
        screen.fill((255, 255, 255))

        # Draw the player (blue rectangle)
        pygame.draw.rect(screen, (0, 0, 255), (player.position.x, player.position.y - player.height, player.width, player.height))

        # Draw the enemy (red triangle)
        draw_triangle(screen, (255, 0, 0), enemy.position, enemy.size)

        # Draw the items
        pygame.draw.rect(screen, (0, 255, 0), (chest.position.x, chest.position.y - chest.size, chest.size, chest.size))  # Chest (large square)
        pygame.draw.rect(screen, (255, 255, 0), (weapon.position.x, weapon.position.y - weapon.size, weapon.size, weapon.size))  # Weapon (medium square)
        pygame.draw.rect(screen, (0, 255, 255), (key.position.x, key.position.y - key.size, key.size, key.size))  # Key (tiny square)

        # Collision detection and prevention
        player_rect = pygame.Rect(player.position.x, player.position.y - player.height, player.width, player.height)
        enemy_rect = pygame.Rect(enemy.position.x, enemy.position.y - enemy.size, enemy.size, enemy.size)
        chest_rect = pygame.Rect(chest.position.x, chest.position.y - chest.size, chest.size, chest.size)
        weapon_rect = pygame.Rect(weapon.position.x, weapon.position.y - weapon.size, weapon.size, weapon.size)
        key_rect = pygame.Rect(key.position.x, key.position.y - key.size, key.size, key.size)

        # Prevent player from moving into enemy
        if player_rect.colliderect(enemy_rect):
            if player.position.x < enemy.position.x:
                player.position.x = enemy.position.x - player.width
            else:
                player.position.x = enemy.position.x + enemy.size

        # Prevent player from moving into chest
        if player_rect.colliderect(chest_rect):
            if player.position.x < chest.position.x:
                player.position.x = chest.position.x - player.width
            else:
                player.position.x = chest.position.x + chest.size

        # Prevent player from moving into weapon
        if player_rect.colliderect(weapon_rect):
            if player.position.x < weapon.position.x:
                player.position.x = weapon.position.x - player.width
            else:
                player.position.x = weapon.position.x + weapon.size

        # Prevent player from moving into key
        if player_rect.colliderect(key_rect):
            if player.position.x < key.position.x:
                player.position.x = key.position.x - player.width
            else:
                player.position.x = key.position.x + key.size

        # Debug output to check player's position and state
        print(f"Player position: {player.position}, Health: {player.health}, Lives: {player.playerLives}")

        # Update the display
        pygame.display.flip()
        clock.tick(60)  # Cap the frame rate at 60 FPS

    # Quit Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()