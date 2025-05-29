import sys
import pygame
from pygame.locals import *
import random
from itemClass import Item, spawn_weapon
from playerClass import Player, PLAYER_SIZE

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Inventory:
    def __init__(self, max_slots=3):
        self.max_slots = max_slots
        self.slot_width = 80
        self.slot_height = 40
        self.slot_margin = 5
        self.slots = [None] * max_slots
        self.bin_rect = pygame.Rect(0, 0, 60, 30)
        self.font = pygame.font.SysFont(None, 24)
        self.selected_slot = None

    def add_item(self, item, slot_index):
        if 0 <= slot_index < self.max_slots:
            self.slots[slot_index] = item
            return True
        return False

    def select_item(self, slot_index):
        if 0 <= slot_index < self.max_slots:
            self.selected_slot = slot_index
            return self.slots[slot_index]
        return None

    def get_item_name(self, slot_index):
        if 0 <= slot_index < self.max_slots and self.slots[slot_index]:
            return self.slots[slot_index].name
        return None

    def display_inventory(self, screen):
        inventory_width = self.max_slots * (self.slot_width + self.slot_margin) - self.slot_margin
        x = SCREEN_WIDTH - inventory_width - 50
        y = 20

        for i in range(self.max_slots):
            slot_x = x + i * (self.slot_width + self.slot_margin)
            pygame.draw.rect(screen, WHITE, (slot_x, y, self.slot_width, self.slot_height), 2)

            if i == self.selected_slot:
                pygame.draw.rect(screen, (255, 255, 0), (slot_x, y, self.slot_width, self.slot_height), 4)

            item_name = self.get_item_name(i)
            text_surface = self.font.render(item_name if item_name else "Empty", True, BLACK)
            text_rect = text_surface.get_rect(center=(slot_x + self.slot_width // 2, y + self.slot_height // 2))
            screen.blit(text_surface, text_rect)

        bin_x = x + inventory_width + self.slot_margin
        self.bin_rect.topleft = (bin_x, y)
        pygame.draw.rect(screen, BLACK, self.bin_rect, 2)
        bin_text = self.font.render("Bin", True, BLACK)
        bin_text_rect = bin_text.get_rect(center=self.bin_rect.center)
        screen.blit(bin_text, bin_text_rect)

    def get_slot_rect(self, index):
        slot_x = SCREEN_WIDTH - (
                    (self.max_slots - index) * (self.slot_width + self.slot_margin) - self.slot_margin) - 50
        slot_y = 20
        return pygame.Rect(slot_x, slot_y, self.slot_width, self.slot_height)

    def remove_item(self, slot_index):
        if 0 <= slot_index < self.max_slots and self.slots[slot_index]:
            item = self.slots[slot_index]
            self.slots[slot_index] = None
            return item
        return None

class Chest(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.closed_image = pygame.image.load('chest_closed.png').convert_alpha()
        self.closed_image = pygame.transform.scale(self.closed_image, (100, 80))
        self.opened_image = pygame.image.load('chest_open.png').convert_alpha()
        self.opened_image = pygame.transform.scale(self.opened_image, (100, 80))
        self.image = self.closed_image
        self.rect = self.image.get_rect(topleft=(50, SCREEN_HEIGHT - self.image.get_height() - 20))
        self.items = [spawn_weapon()]
        self.opened = False
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        if self.opened and self.items:
            for item in self.items:
                item.draw(screen)

    def open_chest(self):
        if not self.opened:
            self.opened = True
            self.image = self.opened_image
            if self.items:
                return self.items[0].name
        return None

def handle_click(chest, player_inventory, placing_item, player):
    mouse_pos = pygame.mouse.get_pos()

    if chest.items and not chest.opened:
        chest_rect = chest.rect
        if chest_rect.collidepoint(mouse_pos):
            item_name = chest.open_chest()
            if item_name:
                placing_item["item"] = Item(item_name, "Weapon", (0, 0))
                placing_item["display_text"] = None
                placing_item["display_rect"] = None

    elif placing_item["item"]:
        for i in range(player_inventory.max_slots):
            slot_rect = player_inventory.get_slot_rect(i)
            if slot_rect.collidepoint(mouse_pos) and player_inventory.slots[i] is None:
                player_inventory.add_item(placing_item["item"], i)
                placing_item["item"] = None
                placing_item["display_text"] = None
                placing_item["display_rect"] = None
                if chest.items:
                    chest.items.pop(0)
                break

        if player_inventory.bin_rect.collidepoint(mouse_pos):
            placing_item["item"] = None
            placing_item["display_text"] = None
            placing_item["display_rect"] = None
            if chest.items:
                chest.items.pop(0)
            print("Item discarded")

    else:
        for i in range(player_inventory.max_slots):
            slot_rect = player_inventory.get_slot_rect(i)
            if slot_rect.collidepoint(mouse_pos) and player_inventory.slots[i] is not None:
                removed_item = player_inventory.remove_item(i)
                placing_item["item"] = removed_item
                placing_item["display_text"] = None
                placing_item["display_rect"] = None
                break

def main_game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Player and Items Interaction")
    clock = pygame.time.Clock()

    player = Player("Hero", (100, 100), PLAYER_SIZE)
    chest = Chest()
    player_inventory = Inventory()

    placing_item = {"item": None, "display_text": None, "display_rect": None}

    running = True
    while running:
        screen.fill(WHITE)

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
                    if chest.rect.colliderect(player.rect):
                        chest.open_chest()
            elif event.type == KEYUP:
                if event.key == K_d:
                    player.stop_move_right()
                elif event.key == K_a:
                    player.stop_move_left()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                handle_click(chest, player_inventory, placing_item, player)

        for item in chest.items:
            item.apply_gravity()

        player.update()
        screen.blit(player.image, player.rect)

        chest.draw(screen)
        player_inventory.display_inventory(screen)

        # Draw placing item image if any
        if placing_item["item"]:
            screen.blit(placing_item["item"].image, placing_item["item"].rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_game_loop()
