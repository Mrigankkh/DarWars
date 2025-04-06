import math
from behavior_gene import BehaviorGene
from enemy.gene_index import GeneIndex
def calculate_enemy_fitness(enemy):
    """Calculate fitness for an enemy based on various performance metrics"""
    
    time_factor = enemy.time_alive * 0.1
    damage_factor = enemy.damage_dealt * 5
    print("damage factor",damage_factor)
    hit_accuracy = (enemy.hits_scored / max(1, enemy.shots_fired)) * 100
    survival_bonus = 50 if enemy.alive else 0
    movement_factor = min(100, enemy.distance_moved * 0.01)  # Reward for movement
    
    # Factor in behavior variety
    BEHAVIOR_GENE_INDICES = [0, 1, 3, 4, 5, 10, 11, 12, 13, 14, 15, 16, 17, 18]

    behavior_count = sum(1 for i in BEHAVIOR_GENE_INDICES if enemy.chromosome.get(i, 0) == 1)
    behavior_variety = behavior_count * 5  # 5 points per active behavior
    
    # Calculate bullet size diversity - reward having a balanced distribution
    bullet_bias = enemy.chromosome.get(GeneIndex.BULLET_SIZE_PROBABILITY, 0.5)
    diversity_factor = (1 - abs(bullet_bias - 0.5) * 2) * 50  # Max reward when bias ≈ 0.5

    
    # Group dynamic bonus - encourage formation behavior if it works well
    group_bonus = 0
    if enemy.chromosome[BehaviorGene.GROUP.value] == 1:  # If GROUP behavior gene is active
        # Reward is proportional to damage dealt (successful group behavior)
        group_bonus = enemy.damage_dealt * 0.5
    
    # Final fitness formula
    enemy.fitness = time_factor + damage_factor + hit_accuracy + survival_bonus + movement_factor + behavior_variety + diversity_factor + group_bonus
    enemy.chromosome[59] = enemy.fitness  # Update fitness in chromosome
    
    return enemy.fitness