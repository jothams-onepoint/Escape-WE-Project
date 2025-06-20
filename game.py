"""
Main game file for the Escape-WE-Project game.
Handles the main game loop, rendering, and state management.
"""

import pygame
import sys
import time
import random
from typing import List, Dict, Any
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, RED,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_TEXT_SIZE, TOTAL_LEVELS,
    MAX_BACKGROUND_DUPLICATES, NORMAL_SPEED, load_image, ASSETS, DOOR_SIZE, WEAPON_SIZE, PLAYER_MAX_HEALTH, PLAYER_LIVES
)
from player import Player
from Enemy import Enemy
from item import spawn_key
from chest import Chest, handle_click
from door import Door
from inventory import Inventory


class Game:
    """
    Main game class that manages the game state and loop.
    
    Attributes:
        screen: Pygame display surface
        clock: Pygame clock for FPS control
        current_screen: Current game screen (menu, game, win)
        current_level: Current level number
        player: Player instance
        player_inventory: Player's inventory
        backgrounds: List of background rectangles for scrolling
        dropped_items: List of items dropped in the world
        placing_item: Item being placed in inventory
        displayed_health: Health value for animated health bar
        chest: Chest instance
        door: Door instance
        key: Key item
        enemies: List of enemies
        total_scroll: Current scroll offset
        max_scroll: Maximum scroll offset
        level_complete: Boolean indicating level completion
    """
    
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Escape')
        
        # Game state
        self.clock = pygame.time.Clock()
        self.current_screen = "menu"
        self.current_level = 1
        
        # Load assets
        self._load_assets()
        
        # Initialize game objects
        self.player = Player("Hero", (100, SCREEN_HEIGHT - 250), 50)
        self.player_inventory = Inventory()
        self.dropped_items = []
        self.placing_item: dict[str, Any] = {"item": None, "display_text": None, "display_rect": None}
        
        # Background scrolling
        self.backgrounds = [
            pygame.Rect(x * SCREEN_HEIGHT, 0, SCREEN_WIDTH, SCREEN_HEIGHT) 
            for x in range(MAX_BACKGROUND_DUPLICATES)
        ]
        
        # UI elements
        self._setup_ui()
        
        # Hide system cursor and create custom cursor
        pygame.mouse.set_visible(False)
        self.cursor_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.cursor_surface, RED, (5, 5), 5)
        
        # Health bar animation state
        self.displayed_health = PLAYER_MAX_HEALTH
        
        # Persistent game objects
        self.chest = None
        self.door = None
        self.key = None
        self.enemies = []
        self.total_scroll = 0
        self.max_scroll = 0
        self.level_complete = False

    def _load_assets(self) -> None:
        """Load game assets."""
        self.menu_background = load_image(ASSETS['menu'], (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.game_background = load_image(ASSETS['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.sword_sprite = load_image(ASSETS['sword'], (75, 75))
        self.game_over_background = load_image(ASSETS['background'], (SCREEN_WIDTH, SCREEN_HEIGHT))
        # Load life icons
        self.life_full_img = pygame.image.load('IMG_0110-removebg-preview.png').convert_alpha()
        self.life_empty_img = pygame.image.load('IMG_0111-removebg-preview.png').convert_alpha()
        self.life_full_img = pygame.transform.smoothscale(self.life_full_img, (28, 28))
        self.life_empty_img = pygame.transform.smoothscale(self.life_empty_img, (28, 28))

    def _setup_ui(self) -> None:
        """Setup UI elements."""
        # Fonts
        self.font_title = pygame.font.Font(None, 72)
        self.font_button = pygame.font.Font(None, BUTTON_TEXT_SIZE)
        self.font = pygame.font.SysFont(None, 36)
        self.level_font = pygame.font.Font(None, 48)
        
        # Buttons
        self.start_button_rect = pygame.Rect(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2, 
            (SCREEN_HEIGHT // 2) - 50, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT
        )
        self.exit_button_rect = pygame.Rect(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2, 
            (SCREEN_HEIGHT // 2) + 50, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT
        )
        self.main_menu_button_rect = pygame.Rect(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2, 
            (SCREEN_HEIGHT // 2) + 100, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT
        )
        # Game Over screen buttons
        self.play_again_button_rect = pygame.Rect(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2, 
            (SCREEN_HEIGHT // 2) + 30, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT
        )
        self.exit_game_button_rect = pygame.Rect(
            (SCREEN_WIDTH - BUTTON_WIDTH) // 2, 
            (SCREEN_HEIGHT // 2) + 100, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT
        )

    def _create_button(self, rect: pygame.Rect, text: str) -> tuple:
        """
        Create a button surface and text.
        
        Args:
            rect: Button rectangle
            text: Button text
            
        Returns:
            Tuple of (button_surface, text_surface)
        """
        button_surf = pygame.Surface((rect.width, rect.height))
        button_surf.fill(WHITE)
        text_render = self.font_button.render(text, True, BLACK)
        text_rect = text_render.get_rect(center=rect.center)
        return button_surf, text_render

    def _draw_text(self, text: str, color: tuple, font: pygame.font.Font, rect: pygame.Rect) -> None:
        """
        Draw centered text on screen.
        
        Args:
            text: Text to draw
            color: Text color
            font: Font to use
            rect: Rectangle to center text in
        """
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect(center=rect.center)
        self.screen.blit(text_obj, text_rect)

    def _render_health(self, displayed_health: float) -> None:
        """
        Render a slanted parallelogram health bar in the top left (animated, inspired by image).
        Also draw life icons to the right of the bar.
        Args:
            displayed_health: The health value to display (for animation)
        """
        import pygame
        # Bar settings
        max_bar_width = 110
        bar_height = 18
        slant = 10
        bar_x = 70
        bar_y = 24
        # Parallelogram background (black)
        bg_points = [
            (bar_x, bar_y),
            (bar_x + max_bar_width, bar_y),
            (bar_x + max_bar_width - slant, bar_y + bar_height),
            (bar_x - slant, bar_y + bar_height)
        ]
        pygame.draw.polygon(self.screen, (0, 0, 0), bg_points)
        # Gradient colors
        green = (0, 180, 0)
        yellow = (255, 230, 40)
        # Calculate health ratio
        health_ratio = max(0, min(1, displayed_health / PLAYER_MAX_HEALTH))
        # Bar width for current health
        health_bar_width = int(max_bar_width * health_ratio)
        # Draw health parallelogram (gradient)
        for i in range(health_bar_width):
            t = i / max_bar_width
            r = int(green[0] + (yellow[0] - green[0]) * t)
            g = int(green[1] + (yellow[1] - green[1]) * t)
            b = int(green[2] + (yellow[2] - green[2]) * t)
            color = (r, g, b)
            # Each vertical line is slanted
            x0 = bar_x + i
            y0 = bar_y
            x1 = bar_x + i - slant
            y1 = bar_y + bar_height
            pygame.draw.line(self.screen, color, (x0, y0), (x1, y1))
        # Draw health number (white, bold, left)
        health_text = self.font.render(f"{int(round(displayed_health))}", True, (255, 255, 255))
        text_rect = health_text.get_rect(midright=(bar_x - 10, bar_y + bar_height // 2))
        self.screen.blit(health_text, text_rect)
        # Draw white plus sign on the right
        plus_center = (bar_x + max_bar_width + 12, bar_y + bar_height // 2)
        plus_size = 10
        plus_thickness = 2
        pygame.draw.line(self.screen, (255, 255, 255),
                         (plus_center[0] - plus_size // 2, plus_center[1]),
                         (plus_center[0] + plus_size // 2, plus_center[1]), plus_thickness)
        pygame.draw.line(self.screen, (255, 255, 255),
                         (plus_center[0], plus_center[1] - plus_size // 2),
                         (plus_center[0], plus_center[1] + plus_size // 2), plus_thickness)
        # Draw life icons to the right of the bar
        icon_y = bar_y + bar_height // 2 - 14
        icon_x_start = bar_x + max_bar_width + 32
        lives = max(0, min(3, self.player.lives))
        for i in range(3):
            icon_x = icon_x_start + i * 32
            if i < lives:
                self.screen.blit(self.life_full_img, (icon_x, icon_y))
            else:
                self.screen.blit(self.life_empty_img, (icon_x, icon_y))

    def _handle_menu_events(self, event: pygame.event.Event) -> bool:
        """
        Handle events in menu screen.
        
        Args:
            event: Pygame event
            
        Returns:
            True if game should continue, False to quit
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.start_button_rect.collidepoint(mouse_pos):
                self.current_screen = "game"
                self._reset_level()
            elif self.exit_button_rect.collidepoint(mouse_pos):
                return False
        return True

    def _handle_game_events(self, event: pygame.event.Event, 
                          enemies: List[Enemy], chest: Chest, 
                          door: Door, key, total_scroll: int) -> bool:
        """
        Handle events in game screen.
        
        Args:
            event: Pygame event
            enemies: List of enemies
            chest: Chest instance
            door: Door instance
            key: Key item
            total_scroll: Current scroll offset
            
        Returns:
            True if game should continue, False to quit
        """
        if event.type == pygame.QUIT:
            return False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.jump()
            elif event.key == pygame.K_d:
                self.player.move_right()
            elif event.key == pygame.K_w:
                self.player.jump()
            elif event.key == pygame.K_a:
                self.player.move_left()
            elif event.key == pygame.K_e:
                self._handle_interaction(enemies, chest, door, key, total_scroll)
            elif event.key == pygame.K_q:
                dropped_item = self.player.drop_item()
                if dropped_item:
                    self.dropped_items.append(dropped_item)
                    
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                self.player.stop_move_right()
            elif event.key == pygame.K_a:
                self.player.stop_move_left()
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_click(enemies, chest)
            
        elif event.type == pygame.MOUSEMOTION:
            self.player.update_cursor_pos(event.pos)
            self.player.update(False)
            
        return True

    def _handle_interaction(self, enemies: List[Enemy], chest: Chest, 
                          door: Door, key, total_scroll: int) -> None:
        """
        Handle player interactions.
        
        Args:
            enemies: List of enemies
            chest: Chest instance
            door: Door instance
            key: Key item
            total_scroll: Current scroll offset
        """
        # Key pickup
        if (not self.player.has_key and not key.is_picked_up and 
            key.is_collision(self.player)):
            key.interact(self.player)
            
        # Door interaction
        elif door.is_near(self.player, total_scroll):
            door.use(self.player)
            
        # Chest interaction
        elif chest.rect.colliderect(self.player.rect):
            item_name = chest.open_chest()
            if item_name and not self.player.equipped_item and chest.items:
                # Equip the item directly if player is not holding anything
                item = chest.items[0]
                self.player.equip_item(item)
                chest.remove_item()
            elif item_name:
                # If player is holding something, fallback to old placing_item logic
                from item import Item
                new_item = Item(item_name, "Weapon", (0, 0), WEAPON_SIZE, self.sword_sprite.copy())
                self.placing_item["item"] = new_item
                self.placing_item["display_text"] = self.player_inventory.font.render(item_name, True, BLACK)
                self.placing_item["display_rect"] = self.placing_item["display_text"].get_rect(center=chest.rect.center)
        # Dropped item pickup (sword)
        elif not self.player.equipped_item:
            for item in self.dropped_items[:]:
                # Use rect collision for proximity
                if item.item_type == "Weapon" and item.rect.colliderect(self.player.rect):
                    self.player.equip_item(item)
                    item.is_picked_up = True
                    self.dropped_items.remove(item)
                    break

    def _handle_mouse_click(self, enemies: List[Enemy], chest: Chest) -> None:
        """
        Handle mouse clicks in game.
        
        Args:
            enemies: List of enemies
            chest: Chest instance
        """
        mouse_pos = pygame.mouse.get_pos()
        
        # Inventory slot clicks
        for i in range(self.player_inventory.max_slots):
            slot_rect = self.player_inventory.get_slot_rect(i)
            if slot_rect.collidepoint(mouse_pos):
                # Allow moving equipped item to inventory if slot is empty
                if self.player_inventory.slots[i] is None and self.player.equipped_item:
                    self.player_inventory.add_item(self.player.equipped_item, i)
                    self.player.unequip_item()
                # Allow re-equipping item from inventory if slot is not empty and player is not holding anything
                elif self.player_inventory.slots[i] is not None and not self.player.equipped_item:
                    self.player.equip_item(self.player_inventory.slots[i])
                    self.player_inventory.remove_item(i)
                break

        # Attack with weapon
        if (self.player.equipped_item and 
            self.player.equipped_item.item_type == "Weapon"):
            damage = self.player.attack(time.time())
            for enemy in enemies[:]:
                if damage > 0 and self.player.equipped_item.is_collision(enemy):
                    print(f"Dealt {damage} damage!")
                    enemies.remove(enemy)
                    # Heal player by 3 (capped at max health)
                    self.player.health = min(self.player.health + 3, PLAYER_MAX_HEALTH)

        # Chest interaction
        handle_click(chest, self.player_inventory, self.placing_item, self.player)

    def _reset_level(self) -> None:
        """Reset the current level state."""
        self.player.position = pygame.Vector2((100, SCREEN_HEIGHT - 250))
        self.player.rect.topleft = (int(self.player.position.x), int(self.player.position.y))
        self.player.has_key = False
        self.player_inventory.clear()

    def _update_scrolling(self, keys: pygame.key.ScancodeWrapper, 
                         total_scroll: int, max_scroll: int,
                         chest: Chest, key, enemies: List[Enemy], 
                         door: Door) -> tuple:
        """
        Update screen scrolling and object positions.
        
        Args:
            keys: Pressed keys
            total_scroll: Current scroll offset
            max_scroll: Maximum scroll offset
            chest: Chest instance
            key: Key item
            enemies: List of enemies
            door: Door instance
            
        Returns:
            Tuple of (total_scroll, move_amount, is_scrolling)
        """
        right_boundary = int(SCREEN_WIDTH * 0.75)
        left_boundary = int(SCREEN_WIDTH * 0.25)
        
        move_amount = 0
        scroll_amount = 0
        is_scrolling = False

        if keys[pygame.K_d]:
            if total_scroll < max_scroll:
                if self.player.rect.right < right_boundary:
                    move_amount = NORMAL_SPEED
                elif self.player.rect.right >= right_boundary:
                    scroll_amount = min(NORMAL_SPEED, max_scroll - total_scroll)
                    is_scrolling = True
                    self._scroll_objects(scroll_amount, chest, key, enemies)
                    total_scroll += scroll_amount
            else:
                move_amount = NORMAL_SPEED

        elif keys[pygame.K_a]:
            if total_scroll > 0:
                if self.player.rect.left > left_boundary:
                    move_amount = -NORMAL_SPEED
                elif self.player.rect.left <= left_boundary:
                    scroll_amount = min(NORMAL_SPEED, total_scroll)
                    is_scrolling = True
                    self._scroll_objects(-scroll_amount, chest, key, enemies)
                    total_scroll -= scroll_amount
            else:
                move_amount = -NORMAL_SPEED

        return total_scroll, move_amount, is_scrolling

    def _scroll_objects(self, scroll_amount: int, chest: Chest, 
                       key, enemies: List[Enemy]) -> None:
        """
        Scroll all objects by the given amount.
        
        Args:
            scroll_amount: Amount to scroll
            chest: Chest instance
            key: Key item
            enemies: List of enemies
        """
        # Scroll backgrounds
        for bg in self.backgrounds:
            bg.x -= scroll_amount
            if bg.right <= 0:
                max_right = max(b.right for b in self.backgrounds)
                bg.left = max_right
            elif bg.left >= SCREEN_WIDTH:
                min_left = min(b.left for b in self.backgrounds)
                bg.right = min_left

        # Scroll game objects
        chest.rect.x -= scroll_amount
        if not key.is_picked_up:
            key.rect.x -= scroll_amount
        for enemy in enemies:
            enemy.x -= scroll_amount

    def _draw_menu(self) -> None:
        """Draw the menu screen."""
        self.screen.blit(self.menu_background, (0, 0))
        self._draw_text("Escape", BLACK, self.font_title, 
                       pygame.Rect(0, 50, SCREEN_WIDTH, 100))
        
        # Draw buttons
        start_button_surf, start_button_text = self._create_button(
            self.start_button_rect, "Start"
        )
        exit_button_surf, exit_button_text = self._create_button(
            self.exit_button_rect, "Exit"
        )
        
        self.screen.blit(start_button_surf, self.start_button_rect)
        self.screen.blit(start_button_text, start_button_text.get_rect(
            center=self.start_button_rect.center
        ))
        self.screen.blit(exit_button_surf, self.exit_button_rect)
        self.screen.blit(exit_button_text, exit_button_text.get_rect(
            center=self.exit_button_rect.center
        ))
        
        self.screen.blit(self.cursor_surface, pygame.mouse.get_pos())

    def _draw_game(self, enemies: List[Enemy], chest: Chest, 
                  door: Door, key, total_scroll: int) -> None:
        """
        Draw the game screen.
        
        Args:
            enemies: List of enemies
            chest: Chest instance
            door: Door instance
            key: Key item
            total_scroll: Current scroll offset
        """
        # Draw backgrounds
        for bg in self.backgrounds:
            self.screen.blit(self.game_background, bg.topleft)

        # Draw dropped items
        for item in self.dropped_items[:]:
            item.apply_gravity()
            item.draw(self.screen)

        # Draw enemies
        for enemy in enemies:
            enemy.update()
            enemy.draw(self.screen)
            # Only apply damage if player is not invulnerable
            if enemy.rect.colliderect(self.player.rect):
                # Player takes discrete damage and triggers shake/invulnerability
                dead = self.player.take_damage(10)
                if dead:
                    self.current_screen = "menu"

        # Draw game objects
        door.draw(self.screen, total_scroll)
        self.player.draw(self.screen)
        chest.draw(self.screen)
        
        if not key.is_picked_up:
            key.draw(self.screen)
            
        self.player_inventory.display_inventory(self.screen)
        
        if self.player.equipped_item:
            self.player.equipped_item.draw(self.screen)

        # Draw UI elements
        if self.placing_item["display_text"] and self.placing_item["display_rect"] is not None:
            self.screen.blit(self.placing_item["display_text"], self.placing_item["display_rect"])

        level_text = self.level_font.render(f"Level: {self.current_level}", True, BLACK)
        level_rect = level_text.get_rect(centerx=SCREEN_WIDTH // 2, top=10)
        self.screen.blit(level_text, level_rect)

        # Animate displayed_health toward actual health
        health_speed = 0.5  # units per ms (quicker animation)
        dt = self.clock.get_time() / 1000.0  # seconds
        target = self.player.health
        if abs(self.displayed_health - target) > 0.1:
            diff = target - self.displayed_health
            step = health_speed * PLAYER_MAX_HEALTH * dt
            if abs(diff) < step:
                self.displayed_health = target
            else:
                self.displayed_health += step if diff > 0 else -step
        else:
            self.displayed_health = target
        self._render_health(self.displayed_health)
        self.screen.blit(self.cursor_surface, pygame.mouse.get_pos())

    def _draw_win_screen(self) -> None:
        """Draw the win screen."""
        self.screen.blit(self.menu_background, (0, 0))
        win_text = self.font_title.render("Congratulations! You Win!", True, WHITE)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(win_text, win_rect)

        main_menu_button_surf, main_menu_button_text = self._create_button(
            self.main_menu_button_rect, "Main Menu"
        )
        self.screen.blit(main_menu_button_surf, self.main_menu_button_rect)
        self.screen.blit(main_menu_button_text, main_menu_button_text.get_rect(
            center=self.main_menu_button_rect.center
        ))

        self.screen.blit(self.cursor_surface, pygame.mouse.get_pos())

    def _draw_game_over_screen(self) -> None:
        """Draw the game over screen using background.png."""
        self.screen.blit(self.game_over_background, (0, 0))
        game_over_text = self.font_title.render("Game Over", True, (255, 255, 255))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(game_over_text, text_rect)
        # Play Again button
        play_again_surf, play_again_text = self._create_button(
            self.play_again_button_rect, "Play Again"
        )
        self.screen.blit(play_again_surf, self.play_again_button_rect)
        self.screen.blit(play_again_text, play_again_text.get_rect(
            center=self.play_again_button_rect.center
        ))
        # Exit button
        exit_game_surf, exit_game_text = self._create_button(
            self.exit_game_button_rect, "Exit"
        )
        self.screen.blit(exit_game_surf, self.exit_game_button_rect)
        self.screen.blit(exit_game_text, exit_game_text.get_rect(
            center=self.exit_game_button_rect.center
        ))
        self.screen.blit(self.cursor_surface, pygame.mouse.get_pos())

    def _start_new_level(self):
        """Initialize or reset the current level objects."""
        self.chest = Chest()
        self.door = Door(DOOR_SIZE, SCREEN_WIDTH * 3)
        self.key = spawn_key()
        self.key.rect.topleft = (random.randint(100, SCREEN_WIDTH * 3 - 100), SCREEN_HEIGHT - self.key.rect.height - 30)
        self.enemies = [Enemy() for _ in range(3)]
        self.total_scroll = 0
        self.max_scroll = SCREEN_WIDTH * 3 - SCREEN_WIDTH
        self.level_complete = False

    def run(self) -> None:
        """Run the main game loop."""
        running = True
        game_over = False
        while running:
            current_time = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.current_screen == "menu":
                    running = self._handle_menu_events(event)
                elif self.current_screen == "game":
                    if self.chest is None or self.door is None or self.key is None or self.level_complete:
                        self._start_new_level()
                    # --- BEGIN LEVEL LOOP ---
                    while not self.level_complete and running:
                        current_time = time.time()
                        for level_event in pygame.event.get():
                            if level_event.type == pygame.QUIT:
                                running = False
                                break
                            else:
                                if self.chest is None or self.door is None or self.key is None:
                                    break
                                running = self._handle_game_events(
                                    level_event, self.enemies, self.chest, self.door, self.key, self.total_scroll
                                )
                                if not running:
                                    break
                        if not running or self.chest is None or self.door is None or self.key is None:
                            break
                        keys = pygame.key.get_pressed()
                        self.total_scroll, move_amount, is_scrolling = self._update_scrolling(
                            keys, self.total_scroll, self.max_scroll, self.chest, self.key, self.enemies, self.door
                        )
                        if not is_scrolling:
                            new_x = self.player.rect.x + move_amount
                            if 0 <= new_x <= SCREEN_WIDTH - self.player.rect.width:
                                self.player.rect.x = new_x
                            elif new_x < 0:
                                self.player.rect.left = 0
                            elif new_x > SCREEN_WIDTH - self.player.rect.width:
                                self.player.rect.right = SCREEN_WIDTH
                        self.player.update(is_scrolling)
                        if self.player.equipped_item:
                            self.player.update_cursor_pos(pygame.mouse.get_pos())
                            self.player.update(is_scrolling)
                        if self.door and self.door.is_open:
                            self.level_complete = True
                        if self.player.lives <= 0:
                            self.current_screen = "game_over"
                            break
                        self.screen.fill(WHITE)
                        if self.chest and self.door and self.key:
                            self._draw_game(self.enemies, self.chest, self.door, self.key, self.total_scroll)
                        pygame.display.flip()
                        self.clock.tick(FPS)
                    # --- END LEVEL LOOP ---
                    # Handle level completion
                    if self.level_complete:
                        self.chest = None
                        self.door = None
                        self.key = None
                        self.enemies = []
                        if self.current_level == TOTAL_LEVELS:
                            self.current_screen = "win"
                            while self.current_screen == "win" and running:
                                for win_event in pygame.event.get():
                                    if win_event.type == pygame.QUIT:
                                        running = False
                                    elif (win_event.type == pygame.MOUSEBUTTONDOWN and 
                                          win_event.button == 1):
                                        if self.main_menu_button_rect.collidepoint(win_event.pos):
                                            self.current_screen = "menu"
                                            self.current_level = 1
                                            self._reset_level()
                                            self.player_inventory = Inventory()
                                self.screen.fill(WHITE)
                                self._draw_win_screen()
                                pygame.display.flip()
                                self.clock.tick(FPS)
                        else:
                            self.current_level += 1
                elif self.current_screen == "win":
                    for win_event in pygame.event.get():
                        if win_event.type == pygame.QUIT:
                            running = False
                        elif (win_event.type == pygame.MOUSEBUTTONDOWN and 
                              win_event.button == 1):
                            if self.main_menu_button_rect.collidepoint(win_event.pos):
                                self.current_screen = "menu"
                                self.current_level = 1
                                self._reset_level()
                                self.player_inventory = Inventory()
                elif self.current_screen == "game_over":
                    for go_event in pygame.event.get():
                        if go_event.type == pygame.QUIT:
                            running = False
                        elif (go_event.type == pygame.MOUSEBUTTONDOWN and 
                              go_event.button == 1):
                            if self.play_again_button_rect.collidepoint(go_event.pos):
                                # Play again: reset game state, inventory, equipped items, lives, health
                                self.current_screen = "game"
                                self.current_level = 1
                                self._reset_level()
                                self.player_inventory = Inventory()
                                self.player.lives = PLAYER_LIVES
                                self.player.health = PLAYER_MAX_HEALTH
                                self.player.equipped_item = None
                                self.player.inventory.clear()
                                self.chest = None
                                self.door = None
                                self.key = None
                                self.level_complete = False
                                self.total_scroll = 0
                            elif self.exit_game_button_rect.collidepoint(go_event.pos):
                                running = False
                                pygame.quit()
                                return
                    self.screen.fill(WHITE)
                    self._draw_game_over_screen()
                    pygame.display.flip()
                    self.clock.tick(FPS)
            self.screen.fill(WHITE)
            if self.current_screen == "menu":
                self._draw_menu()
            elif self.current_screen == "win":
                self._draw_win_screen()
            elif self.current_screen == "game_over":
                self._draw_game_over_screen()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


def main():
    """Main function to start the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main() 