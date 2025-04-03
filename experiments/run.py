import pygame
import numpy as np
import random

# --- Parameters ---
GRID_SIZE = 50             # Size of the grid
NUM_OBSTACLES = 100        # Number of obstacles in the grid
CAPTURE_THRESHOLD = 2      # If the distance between seeker and hider is <= 2 cells, capture occurs

CELL_SIZE = 12             # Size of each grid cell in pixels
WINDOW_SIZE = GRID_SIZE * CELL_SIZE

PERCEPTION_RANGE = 5       # For this simple model, we compute dx, dy directly

# --- Directions ---
# 0: Up, 1: Down, 2: Left, 3: Right
DIRECTIONS = {
    0: (-1, 0),
    1: (1, 0),
    2: (0, -1),
    3: (0, 1),
}

# --- Colors ---
COLOR_BG = (30, 30, 30)
COLOR_OBSTACLE = (100, 100, 100)
COLOR_HIDER = (0, 255, 0)
COLOR_SEEKER = (255, 0, 0)

# --- Environment Class ---
class Environment:
    def __init__(self, grid_size=GRID_SIZE, num_obstacles=NUM_OBSTACLES):
        self.grid_size = grid_size
        self.num_obstacles = num_obstacles
        self.grid = np.zeros((grid_size, grid_size), dtype=int)
        self._place_obstacles()
        
    def _place_obstacles(self):
        count = 0
        while count < self.num_obstacles:
            i = np.random.randint(0, self.grid_size)
            j = np.random.randint(0, self.grid_size)
            if self.grid[i, j] == 0:
                self.grid[i, j] = 1
                count += 1
                
    def is_valid_position(self, pos):
        x, y = pos
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return False
        if self.grid[x, y] == 1:
            return False
        return True

# --- Agent Class Using Simple Input ---
# The genome is a 4x3 weight matrix.
class Agent:
    def __init__(self, genome=None):
        # If no genome is provided, create a random one.
        if genome is None:
            self.genome = np.random.uniform(-1, 1, (4, 3))
        else:
            self.genome = genome

    def decide_move(self, dx, dy):
        # Build input vector [dx, dy, 1] (1 is the bias)
        input_vector = np.array([dx, dy, 1])
        scores = np.dot(self.genome, input_vector)
        return np.argmax(scores)

# --- Main Game Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Hide and Seek Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Load the trained genome for the seeker.
    try:
        genome = np.load("best_seeker_genome.npy")
    except Exception as e:
        print("Error loading best_seeker_genome.npy:", e)
        return

    # Create the environment.
    env = Environment()

    # Initialize the AI seeker position.
    while True:
        seeker_pos = (np.random.randint(0, env.grid_size), np.random.randint(0, env.grid_size))
        if env.is_valid_position(seeker_pos):
            break

    # Initialize the human-controlled hider position.
    while True:
        hider_pos = (np.random.randint(0, env.grid_size), np.random.randint(0, env.grid_size))
        if env.is_valid_position(hider_pos) and hider_pos != seeker_pos:
            break

    # Create the AI seeker using the loaded genome.
    seeker = Agent(genome=genome)

    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not game_over:
            # --- Hider Movement (Human-Controlled) ---
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dx = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dx = 1
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dy = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dy = 1
            new_hider_pos = (hider_pos[0] + dx, hider_pos[1] + dy)
            if env.is_valid_position(new_hider_pos):
                hider_pos = new_hider_pos

            # --- Seeker Movement (Using Simple Perception) ---
            # Calculate relative differences
            dx_seeker = hider_pos[0] - seeker_pos[0]
            dy_seeker = hider_pos[1] - seeker_pos[1]
            move = seeker.decide_move(dx_seeker, dy_seeker)
            delta = DIRECTIONS[move]
            new_seeker_pos = (seeker_pos[0] + delta[0], seeker_pos[1] + delta[1])
            if env.is_valid_position(new_seeker_pos):
                seeker_pos = new_seeker_pos

            # --- Check for Capture ---
            distance = np.linalg.norm(np.array(seeker_pos) - np.array(hider_pos))
            if distance <= CAPTURE_THRESHOLD:
                game_over = True

        # --- Drawing the Environment ---
        screen.fill(COLOR_BG)
        # Draw grid and obstacles.
        for i in range(env.grid_size):
            for j in range(env.grid_size):
                rect = pygame.Rect(j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if env.grid[i, j] == 1:
                    pygame.draw.rect(screen, COLOR_OBSTACLE, rect)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)
        # Draw the hider (green).
        hider_rect = pygame.Rect(hider_pos[1] * CELL_SIZE, hider_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, COLOR_HIDER, hider_rect)
        # Draw the seeker (red).
        seeker_rect = pygame.Rect(seeker_pos[1] * CELL_SIZE, seeker_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, COLOR_SEEKER, seeker_rect)

        if game_over:
            text = font.render("Caught!", True, (255, 255, 255))
            screen.blit(text, ((WINDOW_SIZE - text.get_width()) // 2, (WINDOW_SIZE - text.get_height()) // 2))

        pygame.display.flip()
        clock.tick(10)  # Adjust FPS as needed

    pygame.quit()

if __name__ == "__main__":
    main()
