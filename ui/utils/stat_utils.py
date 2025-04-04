from behavior_gene import BehaviorGene

def calculate_behavior_stats(population):
    stats = {}
    for i in range(20):
        stats[BehaviorGene(i).name] = sum(e.chromosome[i] for e in population)
    return stats

def calculate_bullet_distribution(population):
    dist = [0] * 5
    for e in population:
        weights = e.chromosome[47:52]
        total = sum(weights)
        if total > 0:
            norm = [w / total for w in weights]
            for i in range(5):
                dist[i] += norm[i]
    return [v / len(population) for v in dist]

def calculate_group_dynamics(population):
    avg_size = sum(e.chromosome[54] for e in population) / len(population)
    avg_prox = sum(e.chromosome[55] for e in population) / len(population)
    role_counts = [0, 0, 0]
    pattern_counts = [0, 0, 0, 0]

    for e in population:
        val = e.chromosome[56]
        if val <= 0.3:
            role_counts[0] += 1
        elif val <= 0.7:
            role_counts[1] += 1
        else:
            role_counts[2] += 1

        p = int(e.chromosome[57])
        if 0 <= p < 4:
            pattern_counts[p] += 1

    return avg_size, avg_prox, role_counts, pattern_counts
