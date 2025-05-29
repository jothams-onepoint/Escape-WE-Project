import pygame
import random
from playerClass import Player  # Import the Player class

class Door:
    is_open = None

    def __init__(self, size, total_width):
        self.x = None
        self.size = size
        self.total_width = total_width  # Total width of the scrollable area
        self.is_open = False

        # Load the door sprite image
        self.image = pygame.image.load("door_sprite.png")
        self.image = pygame.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect()

        self.randomize_position()

    def randomize_position(self):
        screen_height = pygame.display.get_surface().get_size()[1]
        x = random.randint(0, self.total_width - self.size[0])
        y = screen_height - self.size[1]
        self.rect.topleft = (x, y)

    def draw(self, screen, scroll_offset):
        if not self.is_open:
            adjusted_rect = self.rect.copy()
            adjusted_rect.x -= scroll_offset
            if adjusted_rect.right >= 0 and adjusted_rect.left <= screen.get_width():
                screen.blit(self.image, adjusted_rect.topleft)

    def is_near(self, player, scroll_offset):
        adjusted_x = self.rect.x - scroll_offset
        return abs(adjusted_x - player.rect.x) < 100 and abs(self.rect.y - player.rect.y) < 100

    def use(self, player):
        if player.has_key:
            print(f"{player.name} uses the key to open the door and proceeds to the next level!")
            self.is_open = True
            player.has_key = False  # Remove the key after use
        else:
            print("You need a key to open this door!")

    @classmethod
    def interact(cls, player):
        pass

def main():
    # Pygame setup
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Player and Door Interaction")
    clock = pygame.time.Clock()

    # Create a player and a random position door
    player = Player("Hero", (50, screen_height - 80), 50)  # Player is a blue rectangle and starts at the bottom
    door_size = (150, 220)  # Door size (width, height)
    door = Door(door_size, 2400)  # Create the door object with a total width of 2400

    # Game loop
    running = True
    scroll = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    door.use(player)  # Call use method on the door
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                scroll = max(0, scroll - 5)
            if keys[pygame.K_RIGHT]:
                scroll = min(1600, scroll + 5)

        # Update game logic
        player.update()

        # Player and door interaction
        Door.interact(player)  # Call interact method on Door class

        # Check if the door is open and move to the next level
        if door.is_open:
            # Code to transition to the next level or end the game
            print("Proceeding to the next level...")
            running = False  # For simplicity, end the game loop after opening the door

        # Drawing logic
        screen.fill((255, 255, 255))  # Clear screen with white
        door.draw(screen, scroll)  # Draw door with scroll offset
        player.draw(screen)  # Draw player

        # Update the display
        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
