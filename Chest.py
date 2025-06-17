"""
Chest class for the Escape-WE-Project game.
Handles chest interactions and item spawning.
"""

import pygame
from typing import Optional, Dict, Any
from config import (
    SCREEN_HEIGHT, CHEST_SIZE, load_image, ASSETS
)
from item import spawn_weapon


class Chest(pygame.sprite.Sprite):
    """
    Chest class for storing and dispensing items.
    
    Attributes:
        opened: Whether the chest has been opened
        items: List of items in the chest
        rect: Pygame rect for collision detection
        image: Chest sprite image
    """
    
    def __init__(self, position: tuple = (50, None)):
        """
        Initialize a chest.
        
        Args:
            position: Chest position (x, y) - y defaults to bottom of screen
        """
        super().__init__()
        
        # Load chest sprites
        self.closed_image = load_image(ASSETS['chest_closed'], CHEST_SIZE)
        self.opened_image = load_image(ASSETS['chest_open'], CHEST_SIZE)
        self.image = self.closed_image
        
        # Position
        x, y = position
        if y is None:
            y = SCREEN_HEIGHT - self.image.get_height() - 20
            
        self.rect = self.image.get_rect(topleft=(x, y))
        
        # State
        self.opened = False
        self.items = [spawn_weapon()]  # Start with one weapon
        self.font = pygame.font.SysFont(None, 24)

    def open_chest(self) -> Optional[str]:
        """
        Open the chest and return the first item's name.
        
        Returns:
            Name of the first item or None if already opened
        """
        if not self.opened and self.items:
            self.opened = True
            self.image = self.opened_image
            return self.items[0].name
        return None

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the chest on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        screen.blit(self.image, self.rect)

        # Draw items if chest is opened
        if self.opened and self.items:
            for item in self.items:
                item.draw(screen)

    def remove_item(self) -> Optional[Any]:
        """
        Remove the first item from the chest.
        
        Returns:
            Removed item or None
        """
        if self.items:
            return self.items.pop(0)
        return None

    def is_empty(self) -> bool:
        """
        Check if the chest is empty.
        
        Returns:
            True if chest has no items
        """
        return len(self.items) == 0


def handle_click(chest: Chest, player_inventory, placing_item: Dict[str, Any], player) -> None:
    """
    Handle mouse clicks for chest and inventory interactions.
    
    Args:
        chest: Chest instance
        player_inventory: Player's inventory
        placing_item: Dictionary containing item being placed
        player: Player instance
    """
    mouse_pos = pygame.mouse.get_pos()

    # Handle chest interaction
    if chest.items and not chest.opened:
        if chest.rect.collidepoint(mouse_pos):
            item_name = chest.open_chest()
            if item_name:
                from item import Item
                placing_item["item"] = Item(item_name, "Weapon", (0, 0))
                placing_item["display_text"] = None
                placing_item["display_rect"] = None

    # Handle item placement
    elif placing_item["item"]:
        # Try to place item in inventory slot
        for i in range(player_inventory.max_slots):
            slot_rect = player_inventory.get_slot_rect(i)
            if slot_rect.collidepoint(mouse_pos) and player_inventory.slots[i] is None:
                player_inventory.add_item(placing_item["item"], i)
                placing_item["item"] = None
                placing_item["display_text"] = None
                placing_item["display_rect"] = None
                chest.remove_item()
                break

        # Handle bin interaction
        if player_inventory.bin_rect.collidepoint(mouse_pos):
            placing_item["item"] = None
            placing_item["display_text"] = None
            placing_item["display_rect"] = None
            chest.remove_item()
            print("Item discarded")

    # Handle inventory item selection
    else:
        for i in range(player_inventory.max_slots):
            slot_rect = player_inventory.get_slot_rect(i)
            if slot_rect.collidepoint(mouse_pos) and player_inventory.slots[i] is not None:
                removed_item = player_inventory.remove_item(i)
                placing_item["item"] = removed_item
                placing_item["display_text"] = None
                placing_item["display_rect"] = None
                break 