import numpy as np
import random

# --- Training Parameters ---
GRID_SIZE = 50             # Grid dimensions for training
NUM_OBSTACLES = 100        # Number of obstacles
PERCEPTION_RANGE = 5       # Group "sees" the hider if |dx| and |dy| (from the centroid) are <= 5
CAPTURE_THRESHOLD = 2      # Capture occurs if any seeker is within 2 cells of the hider
MAX_STEPS = 5000           # Maximum steps per simulation

# Population sizes:
SEEKER_POP_SIZE = 20       # 20 seeker candidates
HIDER_POP_SIZE = 6         # 6 hider candidates

NUM_GENERATIONS = 30       # Number of generations to evolve
NUM_MATCHES = 5            # Matches per evaluation (to average fitness)
GROUP_SIZE = 3             # Number of seekers in the group (shared perception)

# Reward parameters:
PROGRESS_WEIGHT = 5.0      # Amplification for progress reward
BONUS_MULTIPLIER = 10.0    # Bonus multiplier for early capture

# --- Directions: 0: Up, 1: Down, 2: Left, 3: Right ---
DIRECTIONS = {
    0: (-1, 0),
    1: (1, 0),
    2: (0, -1),
    3: (0, 1),
}

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
# The candidate "brain" is a weight matrix of shape (4, 3) that uses input [dx, dy, 1].
class Agent:
    def __init__(self, genome=None):
        if genome is None:
            self.genome = np.random.uniform(-1, 1, (4, 3))
        else:
            self.genome = genome
            
    def decide_move(self, dx, dy):
        # Input vector: relative difference from group centroid to hider plus bias.
        input_vector = np.array([dx, dy, 1])
        scores = np.dot(self.genome, input_vector)
        return np.argmax(scores)

# --- Helper Function ---
def compute_centroid(positions):
    # Compute the average of x and y coordinates.
    xs = [pos[0] for pos in positions]
    ys = [pos[1] for pos in positions]
    centroid = (np.mean(xs), np.mean(ys))
    return centroid

# --- Group Match Simulation with Shared Perception ---
def simulate_match_group(seeker_candidate, hider_candidate, env):
    """
    Simulate one match in a 1v3 setting with shared perception among the three seekers.
    
    - Spawn GROUP_SIZE seekers (all clones of seeker_candidate) at random valid positions.
    - Spawn one hider from the hider_candidate.
    - At each step, compute the centroid of the seeker positions.
    - Use the relative difference between the hider and the centroid as input to the candidate's decide_move.
    - Apply the same move to all seekers (if valid).
    - Reward is computed based on the reduction in the minimum distance from any seeker to the hider,
      multiplied by PROGRESS_WEIGHT, plus a bonus for early capture.
    - The match stops as soon as any seeker is within CAPTURE_THRESHOLD of the hider, or after MAX_STEPS.
    """
    # Initialize hider position.
    while True:
        hider_pos = (np.random.randint(0, env.grid_size), np.random.randint(0, env.grid_size))
        if env.is_valid_position(hider_pos):
            break
    
    # Initialize GROUP_SIZE seeker positions.
    seeker_positions = []
    for _ in range(GROUP_SIZE):
        while True:
            pos = (np.random.randint(0, env.grid_size), np.random.randint(0, env.grid_size))
            if env.is_valid_position(pos) and pos != hider_pos:
                seeker_positions.append(pos)
                break

    # Compute initial group distance (minimum distance from any seeker to hider).
    distances = [np.linalg.norm(np.array(pos) - np.array(hider_pos)) for pos in seeker_positions]
    initial_distance = min(distances)
    total_progress = 0.0
    previous_distance = initial_distance

    for step in range(1, MAX_STEPS + 1):
        # Compute group centroid.
        centroid = compute_centroid(seeker_positions)
        # Compute relative difference from centroid to hider.
        dx = hider_pos[0] - centroid[0]
        dy = hider_pos[1] - centroid[1]
        
        # Use shared perception: if the hider is within PERCEPTION_RANGE (from centroid), use decision; else random.
        if abs(dx) <= PERCEPTION_RANGE and abs(dy) <= PERCEPTION_RANGE:
            move = seeker_candidate.decide_move(dx, dy)
        else:
            move = random.choice(list(DIRECTIONS.keys()))
        delta = DIRECTIONS[move]
        
        # All seekers move using the same move if possible.
        new_positions = []
        for pos in seeker_positions:
            new_pos = (pos[0] + delta[0], pos[1] + delta[1])
            if env.is_valid_position(new_pos):
                new_positions.append(new_pos)
            else:
                new_positions.append(pos)
        seeker_positions = new_positions

        # --- Hider Moves ---
        # For hider, use its own decision function if the closest seeker is within perception.
        distances = [np.linalg.norm(np.array(pos) - np.array(hider_pos)) for pos in seeker_positions]
        min_distance = min(distances)
        closest_index = np.argmin(distances)
        closest_seeker = seeker_positions[closest_index]
        dx_hider = hider_pos[0] - closest_seeker[0]
        dy_hider = hider_pos[1] - closest_seeker[1]
        if abs(dx_hider) <= PERCEPTION_RANGE and abs(dy_hider) <= PERCEPTION_RANGE:
            # With 30% chance, hider moves randomly.
            if random.random() < 0.3:
                move_hider = random.choice(list(DIRECTIONS.keys()))
            else:
                move_hider = hider_candidate.decide_move(-dx_hider, -dy_hider)
        else:
            move_hider = random.choice(list(DIRECTIONS.keys()))
        delta_hider = DIRECTIONS[move_hider]
        new_hider_pos = (hider_pos[0] + delta_hider[0], hider_pos[1] + delta_hider[1])
        if env.is_valid_position(new_hider_pos):
            hider_pos = new_hider_pos

        # --- Update Progress ---
        distances = [np.linalg.norm(np.array(pos) - np.array(hider_pos)) for pos in seeker_positions]
        current_distance = min(distances)
        progress = max(0, previous_distance - current_distance)
        total_progress += progress * PROGRESS_WEIGHT
        previous_distance = current_distance

        # --- Check for Capture ---
        if current_distance <= CAPTURE_THRESHOLD:
            bonus = (MAX_STEPS - step) * BONUS_MULTIPLIER
            return step, total_progress + bonus

    return MAX_STEPS, total_progress

# --- Fitness Evaluation ---
def evaluate_population(seeker_population, hider_population, env, num_matches=NUM_MATCHES):
    seeker_fitness = np.zeros(len(seeker_population))
    hider_fitness = np.zeros(len(hider_population))
    
    # For each seeker candidate, simulate several 1v3 matches with shared perception.
    for i, seeker in enumerate(seeker_population):
        total_reward = 0.0
        for _ in range(num_matches):
            steps, reward = simulate_match_group(seeker, random.choice(hider_population), env)
            total_reward += reward
        seeker_fitness[i] = total_reward / num_matches
        
    # For each hider candidate, simulate matches and average survival steps.
    for i, hider in enumerate(hider_population):
        total_steps = 0.0
        for _ in range(num_matches):
            steps, _ = simulate_match_group(random.choice(seeker_population), hider, env)
            total_steps += steps
        hider_fitness[i] = total_steps / num_matches
        
    return seeker_fitness, hider_fitness

# --- Genetic Operators ---
def select_population(population, fitness, num_select):
    sorted_indices = np.argsort(-fitness)  # Higher fitness first
    return [population[i] for i in sorted_indices[:num_select]]

def crossover(genome1, genome2):
    child_genome = np.zeros_like(genome1)
    for i in range(genome1.shape[0]):
        for j in range(genome1.shape[1]):
            child_genome[i, j] = random.choice([genome1[i, j], genome2[i, j]])
    return child_genome

def mutate(genome, mutation_rate=0.15, mutation_strength=0.7):
    new_genome = genome.copy()
    for i in range(new_genome.shape[0]):
        for j in range(new_genome.shape[1]):
            if random.random() < mutation_rate:
                new_genome[i, j] += np.random.uniform(-mutation_strength, mutation_strength)
    return new_genome

def create_next_generation(selected, pop_size, mutation_rate=0.15, mutation_strength=0.7):
    next_gen = []
    while len(next_gen) < pop_size:
        parent1 = random.choice(selected)
        parent2 = random.choice(selected)
        child_genome = crossover(parent1.genome, parent2.genome)
        child_genome = mutate(child_genome, mutation_rate, mutation_strength)
        next_gen.append(Agent(genome=child_genome))
    return next_gen

# --- Co-Evolution Process ---
def coevolve(num_generations=NUM_GENERATIONS):
    env = Environment()
    
    # Initialize populations.
    seeker_population = [Agent() for _ in range(SEEKER_POP_SIZE)]
    hider_population = [Agent() for _ in range(HIDER_POP_SIZE)]
    
    for gen in range(num_generations):
        seeker_fitness, hider_fitness = evaluate_population(seeker_population, hider_population, env)
        best_seeker_fit = np.max(seeker_fitness)
        best_hider_fit = np.max(hider_fitness)
        print(f"Generation {gen}: Best Seeker Fitness: {best_seeker_fit:.2f}, Best Hider Fitness: {best_hider_fit:.2f}")
        
        # Selection: choose top half.
        num_select_seekers = SEEKER_POP_SIZE // 2
        num_select_hiders = HIDER_POP_SIZE // 2
        
        selected_seekers = select_population(seeker_population, seeker_fitness, num_select_seekers)
        selected_hiders = select_population(hider_population, hider_fitness, num_select_hiders)
        
        # Create next generation.
        seeker_population = create_next_generation(selected_seekers, SEEKER_POP_SIZE)
        hider_population = create_next_generation(selected_hiders, HIDER_POP_SIZE)
    
    # Final evaluation: select best seeker candidate.
    seeker_fitness, _ = evaluate_population(seeker_population, hider_population, env, num_matches=10)
    best_index = np.argmax(seeker_fitness)
    best_seeker = seeker_population[best_index]
    print("Training complete. Best seeker fitness:", seeker_fitness[best_index])
    return best_seeker

def main():
    best_seeker = coevolve(num_generations=NUM_GENERATIONS)
    # Save the best seeker's genome for later use in your game.
    np.save("best_seeker_genome.npy", best_seeker.genome)

if __name__ == "__main__":
    main()
