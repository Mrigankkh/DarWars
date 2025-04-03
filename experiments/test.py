import pygame
import random
import numpy as np

# --- Game Settings ---
GRID_SIZE = 10
CELL_SIZE = 60
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Actions
ACTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # UP, DOWN, LEFT, RIGHT

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hunter AI Grid Game")
clock = pygame.time.Clock()

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0

    def move(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            self.x, self.y = nx, ny

class HunterAI:
    def __init__(self):
        self.x = GRID_SIZE - 1
        self.y = GRID_SIZE - 1

    def get_state(self, player):
        return (self.x - player.x, self.y - player.y)

    def choose_action(self, player):
        # Simple greedy move towards the player (replace with Q-table for RL)
        dx = np.sign(player.x - self.x)
        dy = np.sign(player.y - self.y)

        if abs(player.x - self.x) > abs(player.y - self.y):
            return dx, 0
        else:
            return 0, dy

    def move(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            self.x, self.y = nx, ny

def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

def draw_entity(x, y, color):
    pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    player = Player()
    hunter = HunterAI()
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player.move(0, -1)
        elif keys[pygame.K_DOWN]:
            player.move(0, 1)
        elif keys[pygame.K_LEFT]:
            player.move(-1, 0)
        elif keys[pygame.K_RIGHT]:
            player.move(1, 0)

        # Hunter AI move
        dx, dy = hunter.choose_action(player)
        hunter.move(dx, dy)

        # Check collision
        if player.x == hunter.x and player.y == hunter.y:
            print("You got caught!")
            running = False

        # Draw
        screen.fill(WHITE)
        draw_grid()
        draw_entity(player.x, player.y, BLUE)
        draw_entity(hunter.x, hunter.y, RED)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
