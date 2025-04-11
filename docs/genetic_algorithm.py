import random
from enemy import Enemy

def select_parents(population):
    # Calculate total fitness
    total_fitness = sum(enemy.chromosome[59] for enemy in population)
    
    # If total fitness is 0, select randomly
    if total_fitness == 0:
        return random.choice(population), random.choice(population)
    
    # Tournament selection
    tournament_size = min(4, len(population))
    tournament1 = random.sample(population, tournament_size)
    tournament2 = random.sample(population, tournament_size)
    
    parent1 = max(tournament1, key=lambda x: x.chromosome[59])
    parent2 = max(tournament2, key=lambda x: x.chromosome[59])
    
    return parent1, parent2

def crossover(parent1, parent2):
    child_chromosome = {}

    for i in range(59):  
        if random.random() < 0.5:
            child_chromosome[i] = parent1.chromosome.get(i, 0)
        else:
            child_chromosome[i] = parent2.chromosome.get(i, 0)

    child_chromosome[59] = 0.0 
    return child_chromosome

def mutate(chromosome, mutation_rate):
    mutated = chromosome.copy()

    for i in range(0, 20):  
        if random.random() < mutation_rate:
            mutated[i] = 1 - mutated.get(i, 0)

    for i in range(20, 40):  
        if random.random() < mutation_rate:
            mutated[i] = random.randint(30, 180)

    ranges = {
        40: (0.5, 3.0),     
        41: (0.5, 2.0),     
        42: (0.5, 1.0),     # Accuracy
        43: (0.5, 1.0),     # Evasion
        45: (0.8, 1.5),     # Bullet speed
        46: (0.8, 2.0),     # Bullet damage
        47: (0.0, 1.0),     # Bullet size bias
        52: (-100, 100),    # Spawn X offset
        53: (0.1, 1.0),     # Pattern variance
        54: (1, 10),        # Group size
        55: (30, 200),      # Proximity
        56: (0.0, 1.0),     # Role
        58: (0.0, 1.0),     # Group sync
    }

    for i, (low, high) in ranges.items():
        if random.random() < mutation_rate:
            delta = (high - low) * 0.2
            mutated[i] = max(low, min(high, mutated.get(i, low) + random.uniform(-delta, delta)))

    # Special mutation for pattern (int)
    if random.random() < mutation_rate:
        mutated[57] = random.randint(0, 3)

    mutated[59] = 0.0  # Reset fitness
    return mutated

def evolve_population(population, population_size, mutation_rate):
    best = max(population, key=lambda e: e.chromosome.get(59, 0))
    new_population = [Enemy(best.screen, best.chromosome.copy())]

    while len(new_population) < population_size:
        p1, p2 = select_parents(population)
        child = crossover(p1, p2)
        child = mutate(child, mutation_rate)
        new_population.append(Enemy(p1.screen, child))

    return new_population
