from behavior_gene import BehaviorGene
from enemy.enemy_bullet import get_bullet_size_from_bias

def calculate_behavior_stats(population):
    stats = {}
    for i in range(20):
        stats[BehaviorGene(i).name] = sum(e.chromosome.get(i, 0) for e in population)
    return stats

def calculate_bullet_distribution(population, bins=5):
    # We'll bucket the sampled bullet sizes into 5 size ranges
    dist = [0] * bins
    size_ranges = [(0.5, 0.8), (0.8, 1.1), (1.1, 1.4), (1.4, 1.7), (1.7, 2.0)]
    samples_per_enemy = 10

    for e in population:
        bias = e.chromosome.get(47, 0.5)
        for _ in range(samples_per_enemy):
            size = get_bullet_size_from_bias(bias)
            for i, (low, high) in enumerate(size_ranges):
                if low <= size < high:
                    dist[i] += 1
                    break

    total_samples = len(population) * samples_per_enemy
    return [v / total_samples for v in dist]

def calculate_group_dynamics(population):
    avg_size = sum(e.chromosome.get(54, 5) for e in population) / len(population)
    avg_prox = sum(e.chromosome.get(55, 100) for e in population) / len(population)
    role_counts = [0, 0, 0]
    pattern_counts = [0, 0, 0, 0]

    for e in population:
        val = e.chromosome.get(56, 0.5)
        if val <= 0.3:
            role_counts[0] += 1
        elif val <= 0.7:
            role_counts[1] += 1
        else:
            role_counts[2] += 1

        p = int(e.chromosome.get(57, 0))
        if 0 <= p < 4:
            pattern_counts[p] += 1

    return avg_size, avg_prox, role_counts, pattern_counts
