# train.py
import random
import math

# ===============================================
# GAME / GA CONFIG
# ===============================================

GRID_SIZE = 15          # 15x15 grid for training
N_ITEMS = 8             # Number of collectible items
SIM_STEPS = 100         # Steps per simulation
POP_SIZE = 20           # GA population size
N_GENERATIONS = 15      # Number of generations
TOURNAMENT_SIZE = 3
MUTATION_RATE = 0.3
ELITISM = 1

BEST_GENES_FILE = "best_genes.txt"

"""
We define the AI's "genes" with a small param set controlling:
  1) detection_radius (float)
  2) base_speed      (int)   - how fast it moves in chase mode
  3) search_speed    (int)   - how fast it moves in search mode
  4) search_turn_prob(float) - random turn probability in search
  5) search_threshold(int)   - how many steps of no LOS before searching
You can add more if you want partial knowledge or health trade-offs, etc.
"""

DETECT_RAD_MIN, DETECT_RAD_MAX       = 2.0, 3.0
BASE_SPEED_MIN,  BASE_SPEED_MAX      = 1, 1
SEARCH_SPEED_MIN,SEARCH_SPEED_MAX    = 1, 1
TURN_PROB_MIN,   TURN_PROB_MAX       = 0.0, 1.0
SEARCH_THR_MIN,  SEARCH_THR_MAX      = 5, 20

# We'll make the "dummy player" move randomly while collecting items, to 
# approximate some challenge for the AI.

# ===============================================
# HELPER FUNCTIONS
# ===============================================

def clamp(v, mn, mx):
    return max(mn, min(v, mx))

def distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def create_random_chromosome():
    """
    Return a list of 5 genes:
    [ detection_radius, base_speed, search_speed, search_turn_prob, search_threshold ]
    """
    dr = random.uniform(DETECT_RAD_MIN, DETECT_RAD_MAX)
    bs = random.randint(BASE_SPEED_MIN, BASE_SPEED_MAX)
    ss = random.randint(SEARCH_SPEED_MIN, SEARCH_SPEED_MAX)
    tp = random.uniform(TURN_PROB_MIN, TURN_PROB_MAX)
    sth= random.randint(SEARCH_THR_MIN, SEARCH_THR_MAX)
    return [dr, bs, ss, tp, sth]

def mutate(genes):
    """
    With probability MUTATION_RATE, slightly alter each gene.
    """
    # detection_radius
    if random.random() < MUTATION_RATE:
        shift = random.choice([-0.5, 0.5])
        genes[0] += shift
        genes[0] = clamp(genes[0], DETECT_RAD_MIN, DETECT_RAD_MAX)
    # base_speed
    if random.random() < MUTATION_RATE:
        shift = random.choice([-1,1])
        genes[1] += shift
        genes[1] = clamp(genes[1], BASE_SPEED_MIN, BASE_SPEED_MAX)
    # search_speed
    if random.random() < MUTATION_RATE:
        shift = random.choice([-1,1])
        genes[2] += shift
        genes[2] = clamp(genes[2], SEARCH_SPEED_MIN, SEARCH_SPEED_MAX)
    # search_turn_prob
    if random.random() < MUTATION_RATE:
        shift = random.choice([-0.1,0.1])
        genes[3] += shift
        genes[3] = clamp(genes[3], TURN_PROB_MIN, TURN_PROB_MAX)
    # search_threshold
    if random.random() < MUTATION_RATE:
        shift = random.choice([-1,1])
        genes[4] += shift
        genes[4] = clamp(genes[4], SEARCH_THR_MIN, SEARCH_THR_MAX)

def crossover(p1, p2):
    """Uniform crossover."""
    child = []
    for g1,g2 in zip(p1, p2):
        if random.random() < 0.5:
            child.append(g1)
        else:
            child.append(g2)
    return child

# ===============================================
# SIMULATION FOR FITNESS
# ===============================================

def simulate_chase(genes):
    """
    We'll do a quick simulation:
    - Place dummy player & items in a GRID_SIZE x GRID_SIZE
    - AI tries to find/catch the player before the player collects too many items
    - Return a fitness. Higher = better for AI (faster catch / fewer items collected)

    Genes = [detection_radius, base_speed, search_speed, turn_prob, search_thr]
    """
    detection_radius, base_spd, search_spd, turn_prob, search_thr = genes

    # 1) Generate random item locations
    items = set()
    while len(items) < N_ITEMS:
        x = random.randint(0, GRID_SIZE-1)
        y = random.randint(0, GRID_SIZE-1)
        items.add((x,y))

    # 2) Dummy player starts somewhere random
    player = [ random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1) ]

    # 3) AI starts at another random location
    ai_pos = [ random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1) ]
    while ai_pos == player:
        ai_pos = [ random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1) ]

    # 4) AI State
    time_since_seen = 999
    last_seen_pos = ai_pos[:]
    state = 'search'
    current_speed = 0

    # search direction for random walk
    sdx, sdy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])

    # 5) Run simulation for SIM_STEPS
    items_collected = 0
    for step in range(SIM_STEPS):
        # dummy player random move
        p_dir = random.choice([(1,0),(-1,0),(0,1),(0,-1),(0,0)]) # can stand still
        new_px = clamp(player[0] + p_dir[0], 0, GRID_SIZE-1)
        new_py = clamp(player[1] + p_dir[1], 0, GRID_SIZE-1)
        player = [new_px, new_py]

        # check if player collects item
        if tuple(player) in items:
            items.remove(tuple(player))
            items_collected += 1

        # AI line-of-sight check
        dist = distance(ai_pos, player)
        if dist <= detection_radius:
            # we "see" the player => chase
            last_seen_pos = player[:]
            time_since_seen = 0
            state = 'chase'
        else:
            time_since_seen += 1
            if time_since_seen > search_thr:
                state = 'search'

        # AI movement
        if state == 'chase':
            # accelerate up to base_spd
            current_speed = base_spd  # or you can ramp up if you want
            # single-step approach
            dx = last_seen_pos[0] - ai_pos[0]
            dy = last_seen_pos[1] - ai_pos[1]
            for _ in range(current_speed):
                # move 1 step in major axis
                if abs(dx) > abs(dy):
                    step_x = 1 if dx>0 else -1
                    step_y = 0
                else:
                    step_x = 0
                    step_y = 1 if dy>0 else -1

                ai_pos[0] = clamp(ai_pos[0] + step_x, 0, GRID_SIZE-1)
                ai_pos[1] = clamp(ai_pos[1] + step_y, 0, GRID_SIZE-1)

                # check if caught
                if ai_pos == player:
                    # Great for AI. We'll do a big bonus for catching early
                    return 2000 - step*10 - items_collected*50
        else:
            # search
            current_speed = search_spd
            # maybe random turn
            if random.random() < turn_prob:
                # turn left or right
                if random.random() < 0.5:
                    sdx, sdy = (-sdy, sdx)
                else:
                    sdx, sdy = (sdy, -sdx)
            for _ in range(current_speed):
                nx = ai_pos[0] + sdx
                ny = ai_pos[1] + sdy
                nx = clamp(nx, 0, GRID_SIZE-1)
                ny = clamp(ny, 0, GRID_SIZE-1)
                ai_pos = [nx, ny]

                if ai_pos == player:
                    return 2000 - step*10 - items_collected*50

    # if we never caught the player
    # The fewer items the player collects, the better for the AI
    # The faster it was discovered -> the higher the score
    # We'll do a negative penalty for items_collected
    # We'll also do a small penalty for each step not catching
    fitness = 500 - items_collected*50
    return max(0, fitness)

# ===============================================
# GA CORE
# ===============================================

def evaluate_population(pop):
    """Compute fitness for each chromosome in population."""
    return [simulate_chase(chrom) for chrom in pop]

def tournament_selection(pop, fits):
    idx = random.sample(range(len(pop)), TOURNAMENT_SIZE)
    best_i = idx[0]
    best_f = fits[best_i]
    for i in idx[1:]:
        if fits[i] > best_f:
            best_i = i
            best_f = fits[i]
    return pop[best_i]

def run_ga():
    population = [create_random_chromosome() for _ in range(POP_SIZE)]

    for gen in range(N_GENERATIONS):
        fits = evaluate_population(population)
        best_fit = max(fits)
        avg_fit = sum(fits)/len(fits)
        print(f"[GEN {gen}] Best={best_fit:.2f}, Avg={avg_fit:.2f}")

        # Next gen
        new_pop = []
        # elitism
        sorted_idx = sorted(range(len(population)), key=lambda i: fits[i], reverse=True)
        for e in range(ELITISM):
            new_pop.append(population[sorted_idx[e]][:])

        while len(new_pop) < POP_SIZE:
            p1 = tournament_selection(population, fits)
            p2 = tournament_selection(population, fits)
            child = crossover(p1, p2)
            mutate(child)
            new_pop.append(child)

        population = new_pop

    # final
    final_fits = evaluate_population(population)
    best_i = max(range(len(population)), key=lambda i: final_fits[i])
    best_chrom = population[best_i]
    best_score = final_fits[best_i]
    print("\n=== GA COMPLETE ===")
    print("Best Chromosome:", best_chrom)
    print("Best Fitness=", best_score)
    return best_chrom

if __name__=="__main__":
    best = run_ga()
    # Save best to file
    with open(BEST_GENES_FILE, "w") as f:
        f.write(" ".join(map(str, best)))
    print(f"\nSaved best genes to {BEST_GENES_FILE}.")
