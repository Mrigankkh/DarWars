import random
from enemy import Enemy

def select_parents(population):
    # Calculate total fitness
    total_fitness = sum(enemy.chromosome[54] for enemy in population)
    
    # If total fitness is 0, select randomly
    if total_fitness == 0:
        return random.choice(population), random.choice(population)
    
    # Tournament selection
    tournament_size = min(4, len(population))
    tournament1 = random.sample(population, tournament_size)
    tournament2 = random.sample(population, tournament_size)
    
    parent1 = max(tournament1, key=lambda x: x.chromosome[54])
    parent2 = max(tournament2, key=lambda x: x.chromosome[54])
    
    return parent1, parent2

def crossover(parent1, parent2):
    # Single-point crossover for behavior genes (0-19)
    behavior_crossover_point = random.randint(1, 19)
    
    # Single-point crossover for behavior durations (20-39)
    duration_crossover_point = random.randint(20, 39)
    
    # Single-point crossover for attribute genes (40-46)
    attribute_crossover_point = random.randint(40, 46)
    
    # Single-point crossover for bullet size distribution (47-51)
    bullet_crossover_point = random.randint(47, 51)
    
    # Create child chromosome by combining parts from both parents
    child_chromosome = (
        parent1.chromosome[:behavior_crossover_point] + 
        parent2.chromosome[behavior_crossover_point:20] +
        parent1.chromosome[20:duration_crossover_point] + 
        parent2.chromosome[duration_crossover_point:40] +
        parent1.chromosome[40:attribute_crossover_point] + 
        parent2.chromosome[attribute_crossover_point:47] +
        parent1.chromosome[47:bullet_crossover_point] +
        parent2.chromosome[bullet_crossover_point:52] +
        parent1.chromosome[52:53] +  # Spawn offset
        parent2.chromosome[53:54] +  # Pattern variance
        [0.0]  # Reset fitness
    )
    
    return child_chromosome

def mutate(chromosome, mutation_rate):
    mutated_chromosome = chromosome.copy()
    
    # Mutate binary behavior genes (0-19)
    for i in range(20):
        if random.random() < mutation_rate:
            mutated_chromosome[i] = 1 - mutated_chromosome[i]  # Flip 0 to 1 or 1 to 0
    
    # Mutate behavior duration genes (20-39)
    for i in range(20, 40):
        if random.random() < mutation_rate:
            # Duration can be between 30 and 180 frames
            mutated_chromosome[i] = random.randint(30, 180)
    
    # Mutate continuous attribute genes (40-46)
    for i in range(40, 47):
        if random.random() < mutation_rate:
            # Mutation depends on gene index
            if i == 40:  # Speed
                mutated_chromosome[i] = max(0.5, min(3.0, mutated_chromosome[i] + random.uniform(-0.5, 0.5)))
            elif i == 41:  # Fire rate
                mutated_chromosome[i] = max(0.5, min(2.0, mutated_chromosome[i] + random.uniform(-0.3, 0.3)))
            elif i in [42, 43]:  # Accuracy, Evasion
                mutated_chromosome[i] = max(0.5, min(1.0, mutated_chromosome[i] + random.uniform(-0.2, 0.2)))
            elif i == 44:  # Health
                mutated_chromosome[i] = max(0.8, min(1.2, mutated_chromosome[i] + random.uniform(-0.1, 0.1)))
            elif i == 45:  # Bullet speed
                mutated_chromosome[i] = max(0.8, min(1.5, mutated_chromosome[i] + random.uniform(-0.2, 0.2)))
            elif i == 46:  # Bullet damage
                mutated_chromosome[i] = max(0.8, min(2.0, mutated_chromosome[i] + random.uniform(-0.2, 0.2)))
    
    # Mutate bullet size distribution genes (47-51)
    for i in range(47, 52):
        if random.random() < mutation_rate:
            # Shift weight between 0.0 and 2.0 (will be normalized when used)
            mutated_chromosome[i] = max(0.0, mutated_chromosome[i] + random.uniform(-0.5, 0.5))
    
    # Mutate other continuous genes (52-53)
    if random.random() < mutation_rate:  # Spawn offset
        mutated_chromosome[52] = max(-100, min(100, mutated_chromosome[52] + random.uniform(-20, 20)))
    
    if random.random() < mutation_rate:  # Pattern variance
        mutated_chromosome[53] = max(0.1, min(1.0, mutated_chromosome[53] + random.uniform(-0.1, 0.1)))
    
    # Reset fitness
    mutated_chromosome[54] = 0
    
    return mutated_chromosome

def evolve_population(population, population_size, mutation_rate):
    # Keep track of the best individual from previous generation for elitism
    best_individual = max(population, key=lambda x: x.chromosome[54]) if population else None
    
    new_population = []
    
    # Elitism: Add the best individual from previous generation
    if best_individual:
        new_population.append(Enemy(best_individual.screen, best_individual.chromosome.copy()))
    
    # Generate new individuals through selection, crossover, and mutation
    while len(new_population) < population_size:
        parent1, parent2 = select_parents(population)
        child_chromosome = crossover(parent1, parent2)
        child_chromosome = mutate(child_chromosome, mutation_rate)
        new_population.append(Enemy(parent1.screen, child_chromosome))
    
    return new_population