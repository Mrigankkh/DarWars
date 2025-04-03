import pygame
import random
import numpy as np
import pickle

# --- Game Settings ---
GRID_SIZE = 20
CELL_SIZE = 30
WIDTH = HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 10
TRAINING_EPISODES = 1000
NUM_POWERUPS = 5

# RL Settings
ALPHA = 0.1
GAMMA = 0.9
EPSILON_START = 1.0
EPSILON_MIN = 0.05
EPSILON_DECAY = 0.995

epsilon = EPSILON_START

# Initialize Q-table
Q_FILE = "q_table.pkl"
try:
    with open(Q_FILE, 'rb') as f:
        q_table = pickle.load(f)
except:
    q_table = {}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

obstacles = [(random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)) for _ in range(30)]

# --- Helper Functions ---
def draw_grid():
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (WIDTH, y))

def get_state(agent_pos, player_pos, has_powerup, sees_player):
    return (*agent_pos, *player_pos, int(has_powerup), int(sees_player))

def choose_action(state):
    global epsilon
    if random.random() < epsilon or state not in q_table:
        return random.randint(0, 3)
    return int(np.argmax(q_table[state]))

def update_q_table(state, action, reward, next_state):
    if state not in q_table:
        q_table[state] = [0] * 4
    if next_state not in q_table:
        q_table[next_state] = [0] * 4
    old_value = q_table[state][action]
    next_max = max(q_table[next_state])
    q_table[state][action] = old_value + ALPHA * (reward + GAMMA * next_max - old_value)

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def generate_powerups():
    powerups = []
    while len(powerups) < NUM_POWERUPS:
        p = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if p not in powerups and p not in obstacles:
            powerups.append(p)
    return powerups

def train():
    global epsilon
    visited = set()
    for _ in range(TRAINING_EPISODES):
        agent_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
        player_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
        powerups = generate_powerups()
        has_powerup = False

        for _ in range(150):
            sees_player = manhattan(agent_pos, player_pos) <= 5
            state = get_state(agent_pos, player_pos, has_powerup, sees_player)
            action = choose_action(state)
            new_pos = agent_pos[:]
            if action == 0: new_pos[1] = max(0, new_pos[1] - 1)
            elif action == 1: new_pos[1] = min(GRID_SIZE - 1, new_pos[1] + 1)
            elif action == 2: new_pos[0] = max(0, new_pos[0] - 1)
            elif action == 3: new_pos[0] = min(GRID_SIZE - 1, new_pos[0] + 1)

            if tuple(new_pos) not in obstacles:
                agent_pos = new_pos

            reward = 1
            dist = manhattan(agent_pos, player_pos)
            reward += dist * 0.5

            if tuple(agent_pos) not in visited:
                reward += 2  # Encourage exploring new tiles
                visited.add(tuple(agent_pos))

            if agent_pos == player_pos:
                reward = -100
                break

            if tuple(agent_pos) in powerups:
                reward += 50
                powerups.remove(tuple(agent_pos))
                has_powerup = True

            next_state = get_state(agent_pos, player_pos, has_powerup, sees_player)
            update_q_table(state, action, reward, next_state)

        epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY)

# --- Main Game Loop ---
def main():
    train()

    agent_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
    player_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
    has_powerup = False
    running = True
    total_reward = 0
    powerups = generate_powerups()

    while running:
        screen.fill((30, 30, 30))
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player_pos[0] = max(0, player_pos[0] - 1)
        if keys[pygame.K_RIGHT]: player_pos[0] = min(GRID_SIZE - 1, player_pos[0] + 1)
        if keys[pygame.K_UP]: player_pos[1] = max(0, player_pos[1] - 1)
        if keys[pygame.K_DOWN]: player_pos[1] = min(GRID_SIZE - 1, player_pos[1] + 1)

        sees_player = manhattan(agent_pos, player_pos) <= 5
        state = get_state(agent_pos, player_pos, has_powerup, sees_player)
        action = choose_action(state)
        new_pos = agent_pos[:]
        if action == 0: new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 1: new_pos[1] = min(GRID_SIZE - 1, new_pos[1] + 1)
        elif action == 2: new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 3: new_pos[0] = min(GRID_SIZE - 1, new_pos[0] + 1)

        if tuple(new_pos) not in obstacles:
            agent_pos = new_pos

        reward = 1
        dist = manhattan(agent_pos, player_pos)
        reward += dist * 0.5

        if agent_pos == player_pos:
            reward = -100
            agent_pos = [random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)]
            has_powerup = False

        if tuple(agent_pos) in powerups:
            reward += 50
            powerups.remove(tuple(agent_pos))
            has_powerup = True

        next_state = get_state(agent_pos, player_pos, has_powerup, sees_player)
        update_q_table(state, action, reward, next_state)
        total_reward += reward

        for obs in obstacles:
            pygame.draw.rect(screen, (100, 100, 100), (*[x * CELL_SIZE for x in obs], CELL_SIZE, CELL_SIZE))

        for p in powerups:
            pygame.draw.rect(screen, (0, 0, 255), (*[x * CELL_SIZE for x in p], CELL_SIZE, CELL_SIZE))

        pygame.draw.rect(screen, (200, 0, 0), (*[x * CELL_SIZE for x in agent_pos], CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, (0, 200, 0), (*[x * CELL_SIZE for x in player_pos], CELL_SIZE, CELL_SIZE))

        score_text = font.render(f"Reward: {int(total_reward)}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    with open(Q_FILE, 'wb') as f:
        pickle.dump(q_table, f)
    pygame.quit()

if __name__ == '__main__':
    main()