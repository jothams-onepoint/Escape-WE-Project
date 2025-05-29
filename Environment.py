import pygame
from pygame.locals import *
import sys
import random
import time
from Chest import Inventory, Chest, handle_click, Item, spawn_weapon
from Enemy import Enemy
from playerClass import Player, PLAYER_SIZE
from itemClass import spawn_key
from doorClass import Door

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_TEXT_SIZE = 36
MAX_BACKGROUND_DUPLICATES = 3
SCROLL_SPEED = 5
NORMAL_SPEED = 5
BORDER_TRANSITION_SPEED = 2
TRANSITION_DISTANCE = 100

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Escape')

# Load background images
MENU_BACKGROUND = pygame.image.load('menu.jpg').convert()
MENU_BACKGROUND = pygame.transform.scale(MENU_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
GAME_BACKGROUND = pygame.image.load('background.png').convert()
GAME_BACKGROUND = pygame.transform.scale(GAME_BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load and scale enemy sprites
enemy1_image = pygame.image.load('enemy1.png').convert_alpha()
enemy2_image = pygame.image.load('enemy2.png').convert_alpha()
enemy3_image = pygame.image.load('enemy3.png').convert_alpha()
SWORD_SPRITE= pygame.image.load('sword.png').convert_alpha()
SWORD_SPRITE = pygame.transform.scale(SWORD_SPRITE, (75,75))

enemy1_image = pygame.transform.scale(enemy1_image, (100, 100))
enemy2_image = pygame.transform.scale(enemy2_image, (100, 100))
enemy3_image = pygame.transform.scale(enemy3_image, (100, 100))

# Font and text settings
font_title = pygame.font.Font(None, 72)
font_button = pygame.font.Font(None, BUTTON_TEXT_SIZE)
font = pygame.font.SysFont(None, 36)

# Function to draw text on screen
def draw_text(surface, text, color, font, rect):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect(center=rect.center)
    surface.blit(text_obj, text_rect)

# Function to create a button
def create_button(surface, rect, text):
    button_surf = pygame.Surface((rect.width, rect.height))
    button_surf.fill(WHITE)
    text_render = font_button.render(text, True, BLACK)
    text_rect = text_render.get_rect(center=rect.center)
    surface.blit(button_surf, rect)
    surface.blit(text_render, text_rect)
    return button_surf, text_render

# Function to render health
def render_health(surface, player):
    health_font = pygame.font.Font(None, 36)
    health_text = health_font.render(f"Health: {player.health}", True, (255, 0, 0))
    health_rect = health_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    surface.blit(health_text, health_rect)

# Variables for background scrolling
backgrounds = [pygame.Rect(x * SCREEN_WIDTH, 0, SCREEN_WIDTH, SCREEN_HEIGHT) for x in range(MAX_BACKGROUND_DUPLICATES)]

def render_health(surface, player):
    health_font = pygame.font.Font(None, 36)
    health_text = health_font.render(f"Health: {player.health}", True, (255, 0, 0))
    health_rect = health_text.get_rect(topleft=(10, 10))
    surface.blit(health_text, health_rect)

def main_game_loop():
    global current_screen

    current_screen = "menu"
    current_level = 1

    # Create a Player instance
    player = Player("Hero", (100, SCREEN_HEIGHT - PLAYER_SIZE - 20), PLAYER_SIZE)
    player.has_key = False

    # Create player inventory
    player_inventory = Inventory()

    # Item being placed
    placing_item = {"item": None, "display_text": None, "display_rect": None}
    
    # List to store dropped items
    dropped_items = []
    
    clock = pygame.time.Clock()

    # Font for level display
    level_font = pygame.font.Font(None, 48)

    # Create buttons
    start_button_rect = pygame.Rect((SCREEN_WIDTH - BUTTON_WIDTH) // 2, (SCREEN_HEIGHT // 2) - 50, BUTTON_WIDTH, BUTTON_HEIGHT)
    start_button_surf, start_button_text = create_button(screen, start_button_rect, "Start")
    exit_button_rect = pygame.Rect((SCREEN_WIDTH - BUTTON_WIDTH) // 2, (SCREEN_HEIGHT // 2) + 50, BUTTON_WIDTH, BUTTON_HEIGHT)
    exit_button_surf, exit_button_text = create_button(screen, exit_button_rect, "Exit")
    main_menu_button_rect = pygame.Rect((SCREEN_WIDTH - BUTTON_WIDTH) // 2, (SCREEN_HEIGHT // 2) + 100, BUTTON_WIDTH, BUTTON_HEIGHT)
    main_menu_button_surf, main_menu_button_text = create_button(screen, main_menu_button_rect, "Main Menu")

    # Total scrollable width
    total_width = SCREEN_WIDTH * 3

    # Hide the system cursor
    pygame.mouse.set_visible(False)

    # Create a custom cursor surface
    cursor_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(cursor_surface, (255, 0, 0), (5, 5), 5)

    # Game loop
    running = True
    while running:
        current_time = time.time()
        mouse_pos = pygame.mouse.get_pos()

        # Reset game state for each level
        chest = Chest()
        door = Door((150, 220), total_width)
        key = spawn_key()
        key.rect.topleft = (random.randint(100, total_width - 100), SCREEN_HEIGHT - key.rect.height - 30)

        mouse_pos = pygame.mouse.get_pos()

        # Variables for screen scrolling
        total_scroll = 0
        max_scroll = total_width - SCREEN_WIDTH
        scroll_speed_multiplier = 1
        screen_fully_scrolled = False

        # Reset player position
        player.position = pygame.Vector2((100, SCREEN_HEIGHT - PLAYER_SIZE - 20))
        player.rect.topleft = player.position
        player.has_key = False

        # Initialize enemies
        enemies = [Enemy() for _ in range(3)]

        # Level loop
        level_complete = False
        while not level_complete and running:
            current_time = time.time()
            mouse_pos = pygame.mouse.get_pos()

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
                    elif event.key == pygame.K_d:
                        player.move_right()
                    elif event.key == pygame.K_a:
                        player.move_left()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_d:
                        player.stop_move_right()
                    elif event.key == pygame.K_a:
                        player.stop_move_left()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if current_screen == "menu":
                        if start_button_rect.collidepoint(mouse_pos):
                            current_screen = "game"
                            player.position = pygame.Vector2((100, SCREEN_HEIGHT - PLAYER_SIZE - 20))
                            player.rect.topleft = player.position
                        elif exit_button_rect.collidepoint(mouse_pos):
                            running = False
                    elif current_screen == "game":
                        # Check if an inventory slot is clicked
                        for i in range(player_inventory.max_slots):
                            slot_rect = player_inventory.get_slot_rect(i)
                            if slot_rect.collidepoint(mouse_pos):
                                if player_inventory.slots[i] is None and player.equipped_item:
                                    player_inventory.add_item(player.equipped_item, i)
                                player.equip_item(player_inventory.slots[i])
                                break

                        # Attack if holding a weapon
                        if player.equipped_item and player.equipped_item.item_type == "Weapon":
                            damage = player.attack(current_time)
                            for enemy in enemies[:]:  # Create a copy of the list to safely remove items
                                if damage > 0 and player.equipped_item.is_collision(enemy):
                                    print(f"Dealt {damage} damage!")
                                    enemies.remove(enemy)

                        handle_click(chest, player_inventory, placing_item, player)

                if current_screen == "game" and player.equipped_item:
                    player.update_cursor_pos(mouse_pos)
                    player.update(False)
                    if player.equipped_item.item_type == "Weapon":
                        player.equipped_item.rotate(player.equipped_item_angle)
                elif event.type == pygame.KEYDOWN:
                    if current_screen == "game":
                        if event.key == pygame.K_e:
                            if not player.has_key and not key.is_picked_up and key.is_collision(player):
                                key.interact(player)
                            elif door.is_near(player, total_scroll):
                                door.use(player)
                                if door.is_open:
                                    level_complete = True
                            elif chest.rect.colliderect(player.rect):
                                item_name = chest.open_chest()
                                if item_name:
                                    new_item = Item(item_name, "Weapon", (0, 0), sprite=SWORD_SPRITE.copy())
                                    placing_item["item"] = new_item
                                    placing_item["display_text"] = player_inventory.font.render(item_name, True, BLACK)
                                    placing_item["display_rect"] = placing_item["display_text"].get_rect(center=chest.rect.center)
                        elif event.key == pygame.K_q:
                            # Drop equipped item
                            dropped_item = player.drop_item()
                            if dropped_item:
                                dropped_items.append(dropped_item)

                elif event.type == pygame.KEYUP:
                    if current_screen == "game":
                        if event.key == pygame.K_d:
                            player.stop_move_right()
                        elif event.key == pygame.K_a:
                            player.stop_move_left()

                if event.type == pygame.MOUSEMOTION:
                    player.update_cursor_pos(mouse_pos)
                    player.update(False)

            # Handle player movement and background scrolling
            if current_screen == "game":
                keys = pygame.key.get_pressed()

                right_boundary = int(SCREEN_WIDTH * 0.75)
                left_boundary = int(SCREEN_WIDTH * 0.25)

                move_amount = 0
                scroll_amount = 0
                is_scrolling = False

                if keys[pygame.K_d]:
                    if total_scroll < max_scroll:
                        if player.rect.right < right_boundary:
                            move_amount = NORMAL_SPEED
                        elif player.rect.right >= right_boundary:
                            scroll_amount = min(NORMAL_SPEED * scroll_speed_multiplier, max_scroll - total_scroll)
                            is_scrolling = True
                            for bg in backgrounds:
                                bg.x -= scroll_amount
                                if bg.right < 0:
                                    bg.left = max(bg.right for bg in backgrounds)
                            chest.rect.x -= scroll_amount
                            if not key.is_picked_up:
                                key.rect.x -= scroll_amount
                            for enemy in enemies:
                                enemy.x -= scroll_amount
                            total_scroll += scroll_amount
                            door_offset = total_scroll
                            door.draw(screen, door_offset)
                    else:
                        move_amount = NORMAL_SPEED

                elif keys[pygame.K_a]:
                    if total_scroll > 0:
                        if player.rect.left > left_boundary:
                            move_amount = -NORMAL_SPEED
                        elif player.rect.left <= left_boundary:
                            scroll_amount = min(NORMAL_SPEED * scroll_speed_multiplier, total_scroll)
                            is_scrolling = True
                            for bg in backgrounds:
                                bg.x += scroll_amount
                                if bg.left > SCREEN_WIDTH:
                                    bg.right = min(bg.left for bg in backgrounds)
                            chest.rect.x += scroll_amount
                            if not key.is_picked_up:
                                key.rect.x += scroll_amount
                            for enemy in enemies:
                                enemy.x += scroll_amount
                            total_scroll -= scroll_amount
                            door_offset = total_scroll
                            door.draw(screen, door_offset)
                    else:
                        move_amount = -NORMAL_SPEED

                # Apply the calculated movement
                if not is_scrolling:
                    new_x = player.rect.x + move_amount
                    if 0 <= new_x <= SCREEN_WIDTH - player.rect.width:
                        player.rect.x = new_x
                    elif new_x < 0:
                        player.rect.left = 0
                    elif new_x > SCREEN_WIDTH - player.rect.width:
                        player.rect.right = SCREEN_WIDTH

                screen_fully_scrolled = (total_scroll >= max_scroll)

                # Inside the level loop
                player.update(is_scrolling)
                if player.equipped_item:
                    player.update_cursor_pos(mouse_pos)
                    player.update(is_scrolling)

            screen.fill(WHITE)
            if current_screen == "menu":
                screen.blit(MENU_BACKGROUND, (0, 0))
                draw_text(screen, "Escape", BLACK, font_title, pygame.Rect(0, 50, SCREEN_WIDTH, 100))
                screen.blit(start_button_surf, start_button_rect)
                screen.blit(start_button_text, start_button_text.get_rect(center=start_button_rect.center))
                screen.blit(exit_button_surf, exit_button_rect)
                screen.blit(exit_button_text, exit_button_text.get_rect(center=exit_button_rect.center))
                screen.blit(cursor_surface, mouse_pos)

            elif current_screen == "game":
                for bg in backgrounds:
                    screen.blit(GAME_BACKGROUND, bg.topleft)

                # Update and draw dropped items
                for item in dropped_items[:]:
                    item.apply_gravity()
                    item.draw(screen)
                    # Check if player can pick up the dropped item
                    if item.is_collision(player) and not player.equipped_item:
                        if item.item_type == "Weapon":
                            player.equip_item(item)
                            dropped_items.remove(item)

                # Update and draw enemies
                for enemy in enemies:
                    enemy.update()
                    enemy.draw(screen)
                    if enemy.rect.colliderect(player.rect):
                        dead = player.take_damage(0.5)
                        if dead:
                            current_screen = "menu"
                door.draw(screen, total_scroll)
                player.draw(screen)
                chest.draw(screen)
                screen.blit(cursor_surface, mouse_pos)
                if not key.is_picked_up:
                    key.draw(screen)
                player_inventory.display_inventory(screen)
                if player.equipped_item:
                    player.equipped_item.draw(screen)

                if placing_item["display_text"]:
                    screen.blit(placing_item["display_text"], placing_item["display_rect"])

                # Draw current level
                level_text = level_font.render(f"Level: {current_level}", True, BLACK)
                level_rect = level_text.get_rect(centerx=SCREEN_WIDTH // 2, top=10)
                screen.blit(level_text, level_rect)

                # Add this line to render the health
                render_health(screen, player)

            # Update display
            pygame.display.flip()
            clock.tick(60)

        # Check if the game is completed
        if level_complete:
            if current_level == 10:
                # Display "You Won" screen
                current_screen = "win"
                while current_screen == "win":
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            current_screen = "quit"
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if main_menu_button_rect.collidepoint(event.pos):
                                current_screen = "menu"
                                current_level = 1
                                player.position = pygame.Vector2((100, SCREEN_HEIGHT - PLAYER_SIZE - 20))
                                player.rect.topleft = player.position
                                player.has_key = False
                                player_inventory = Inventory()

                    screen.blit(MENU_BACKGROUND, (0, 0))
                    win_text = font_title.render("Congratulations! You Win!", True, WHITE)
                    win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
                    screen.blit(win_text, win_rect)

                    screen.blit(main_menu_button_surf, main_menu_button_rect)
                    screen.blit(main_menu_button_text,
                                main_menu_button_text.get_rect(center=main_menu_button_rect.center))

                    screen.blit(cursor_surface, pygame.mouse.get_pos())
                    pygame.display.flip()
                    clock.tick(60)
            else:
                current_level += 1

    pygame.quit()
if __name__ == "__main__":
    main_game_loop()