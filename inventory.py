"""
Inventory system for the Escape-WE-Project game.
Handles item storage, management, and UI display.
"""

import pygame
from typing import Optional, List, Any
from config import (
    SCREEN_WIDTH, INVENTORY_SLOT_WIDTH, INVENTORY_SLOT_HEIGHT,
    INVENTORY_SLOT_MARGIN, INVENTORY_MAX_SLOTS, WHITE, BLACK, YELLOW
)


class Inventory:
    """
    Inventory system for managing player items.
    
    Attributes:
        max_slots: Maximum number of inventory slots
        slots: List of items in inventory
        selected_slot: Currently selected slot index
        font: Font for rendering text
    """
    
    def __init__(self, max_slots: int = INVENTORY_MAX_SLOTS):
        """
        Initialize the inventory.
        
        Args:
            max_slots: Maximum number of inventory slots
        """
        self.max_slots = max_slots
        self.slots = [None] * max_slots
        self.selected_slot = None
        self.font = pygame.font.SysFont(None, 24)
        
        # UI elements
        self.bin_rect = pygame.Rect(0, 0, 60, 30)

    def add_item(self, item, slot_index: int) -> bool:
        """
        Add an item to a specific slot, preventing duplicates.
        
        Args:
            item: Item to add
            slot_index: Slot index to add item to
            
        Returns:
            True if item was added successfully
        """
        # Prevent adding the same item object to multiple slots
        if item in self.slots:
            return False
        if 0 <= slot_index < self.max_slots and self.slots[slot_index] is None:
            self.slots[slot_index] = item
            return True
        return False

    def remove_item(self, slot_index: int):
        """
        Remove an item from a specific slot.
        
        Args:
            slot_index: Slot index to remove item from
            
        Returns:
            Removed item or None
        """
        if 0 <= slot_index < self.max_slots and self.slots[slot_index]:
            item = self.slots[slot_index]
            self.slots[slot_index] = None
            return item
        return None

    def select_item(self, slot_index: int):
        """
        Select an item from a specific slot.
        
        Args:
            slot_index: Slot index to select
            
        Returns:
            Selected item or None
        """
        if 0 <= slot_index < self.max_slots:
            self.selected_slot = slot_index
            return self.slots[slot_index]
        return None

    def get_item_name(self, slot_index: int) -> Optional[str]:
        """
        Get the name of an item in a specific slot.
        
        Args:
            slot_index: Slot index to check
            
        Returns:
            Item name or None
        """
        item = self.slots[slot_index] if 0 <= slot_index < self.max_slots else None
        if item is not None and hasattr(item, 'name'):
            return item.name
        return None

    def get_slot_rect(self, index: int) -> pygame.Rect:
        """
        Get the rectangle for a specific inventory slot.
        
        Args:
            index: Slot index
            
        Returns:
            Pygame rect for the slot
        """
        inventory_width = self.max_slots * (INVENTORY_SLOT_WIDTH + INVENTORY_SLOT_MARGIN) - INVENTORY_SLOT_MARGIN
        x = SCREEN_WIDTH - inventory_width - 50
        y = 20
        
        slot_x = x + index * (INVENTORY_SLOT_WIDTH + INVENTORY_SLOT_MARGIN)
        return pygame.Rect(slot_x, y, INVENTORY_SLOT_WIDTH, INVENTORY_SLOT_HEIGHT)

    def display_inventory(self, screen: pygame.Surface) -> None:
        """
        Display the inventory UI on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        inventory_width = self.max_slots * (INVENTORY_SLOT_WIDTH + INVENTORY_SLOT_MARGIN) - INVENTORY_SLOT_MARGIN
        x = SCREEN_WIDTH - inventory_width - 50
        y = 20

        # Draw inventory slots
        for i in range(self.max_slots):
            slot_x = x + i * (INVENTORY_SLOT_WIDTH + INVENTORY_SLOT_MARGIN)
            slot_rect = pygame.Rect(slot_x, y, INVENTORY_SLOT_WIDTH, INVENTORY_SLOT_HEIGHT)
            
            # Draw slot border
            pygame.draw.rect(screen, WHITE, slot_rect, 2)

            # Highlight selected slot
            if i == self.selected_slot:
                pygame.draw.rect(screen, YELLOW, slot_rect, 4)

            # Draw item name
            item_name = self.get_item_name(i)
            text_surface = self.font.render(item_name if item_name else "Empty", True, BLACK)
            text_rect = text_surface.get_rect(center=slot_rect.center)
            screen.blit(text_surface, text_rect)

        # Draw bin button
        bin_x = x + inventory_width + INVENTORY_SLOT_MARGIN
        self.bin_rect.topleft = (bin_x, y)
        pygame.draw.rect(screen, BLACK, self.bin_rect, 2)
        bin_text = self.font.render("Bin", True, BLACK)
        bin_text_rect = bin_text.get_rect(center=self.bin_rect.center)
        screen.blit(bin_text, bin_text_rect)

    def is_full(self) -> bool:
        """
        Check if inventory is full.
        
        Returns:
            True if all slots are occupied
        """
        return all(slot is not None for slot in self.slots)

    def get_first_empty_slot(self) -> Optional[int]:
        """
        Get the index of the first empty slot.
        
        Returns:
            Index of first empty slot or None if full
        """
        for i, slot in enumerate(self.slots):
            if slot is None:
                return i
        return None

    def clear(self) -> None:
        """Clear all items from inventory."""
        self.slots = [None] * self.max_slots
        self.selected_slot = None 