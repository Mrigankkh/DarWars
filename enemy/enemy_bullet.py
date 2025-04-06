"""
Handling bullet creation and management for enemies
"""

import random
import math
from constants import *
from enemy.gene_index import GeneIndex

def create_bullet(enemy, player, bullet_size, speed_multiplier):
    """Create a new bullet aimed at the player"""
    # Calculate direction to player
    dx = player.x - enemy.x
    dy = player.y - enemy.y
    distance = max(1, math.sqrt(dx * dx + dy * dy))
    dx /= distance
    dy /= distance
    
    # Apply accuracy modifier
    accuracy = enemy.chromosome[GeneIndex.ACCURACY] 
    dx += random.uniform(-0.5, 0.5) * (1 - accuracy)
    dy += random.uniform(-0.5, 0.5) * (1 - accuracy)
    
    # Normalize direction
    direction_length = math.sqrt(dx * dx + dy * dy)
    dx = (dx / direction_length) * enemy.bullet_speed * speed_multiplier
    dy = (dy / direction_length) * enemy.bullet_speed * speed_multiplier
    
    return {
        'x': enemy.x + enemy.width / 2,
        'y': enemy.y + enemy.height / 2,
        'dx': dx,
        'dy': dy,
        'width': 5 * bullet_size,
        'height': 5 * bullet_size
    }

def create_spread_bullets(enemy, player, bullet_size, speed_multiplier, angles=(-0.3, 0, 0.3)):
    """Create multiple bullets in a spread pattern"""
    bullets = []
    accuracy = enemy.chromosome[GeneIndex.ACCURACY]
    angle_deviation = random.uniform(-0.2, 0.2) * (1 - accuracy)

    for angle in angles:
        # Calculate direction to player with spread
        total_angle = angle + angle_deviation

        dx = player.x - enemy.x
        dy = player.y - enemy.y
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        dx /= distance
        dy /= distance
        
        # Apply rotation for spread
        rotated_dx = dx * math.cos(total_angle) - dy * math.sin(total_angle)
        rotated_dy = dx * math.sin(total_angle) + dy * math.cos(total_angle)
        
        # Apply accuracy and speed
        final_dx = rotated_dx * enemy.bullet_speed * speed_multiplier
        final_dy = rotated_dy * enemy.bullet_speed * speed_multiplier
        
        bullets.append({
            'x': enemy.x + enemy.width / 2,
            'y': enemy.y + enemy.height / 2,
            'dx': final_dx,
            'dy': final_dy,
            'width': 4 * bullet_size, 
            'height': 4 * bullet_size
        })
    
    return bullets


def get_bullet_size_from_bias(bias):
    """
    Generate a bullet size using a bias value.
    bias ≈ 0 → small bullets
    bias ≈ 1 → large bullets
    Output size is in the range [0.5, 2.0]
    """
    # Clamp bias slightly to avoid extremes in Beta distribution
    alpha = max(0.01, 1.0 - bias + 0.1)
    beta = max(0.01, bias + 0.1)
    raw = random.betavariate(alpha, beta)
    return raw * 1.5 + 0.5  # Scales result to [0.5, 2.0] range
