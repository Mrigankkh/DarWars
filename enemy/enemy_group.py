import random
import math
from constants import *

# def apply_group_behavior(enemy, all_enemies):
    # """Apply group behavior based on group genes"""
    # # Get group genes
    # group_size_pref = enemy.chromosome[54]  # Preferred group size (1-10)
    # optimal_proximity = enemy.chromosome[55]  # Optimal distance to allies (30-200)
    # formation_role = enemy.chromosome[56]  # Role in formation (0=edge, 0.5=middle, 1=leader)
    # formation_pattern = int(enemy.chromosome[57]) % 4  # Pattern (0=line, 1=circle, 2=triangle, 3=grid)
    # group_sync = enemy.chromosome[58]  # Synchronization level (0-1)
    
    # # Find nearby enemies
    # nearby_enemies = []
    # for other in all_enemies:
    #     if other != enemy and other.alive:
    #         dx = other.x - enemy.x
    #         dy = other.y - enemy.y
    #         distance = math.sqrt(dx * dx + dy * dy)
    #         if distance < 250:  # Consider enemies within 250 pixels
    #             nearby_enemies.append((other, distance))
    
    # # If no nearby enemies, no group behavior to apply
    # if not nearby_enemies:
    #     return 0, 0
    
    # # Sort by distance
    # nearby_enemies.sort(key=lambda x: x[1])
    
    # # Determine move direction based on group dynamics
    # move_x, move_y = 0, 0
    
    # # Group size adjustment
    # current_group_size = len(nearby_enemies)
    # if current_group_size > group_size_pref:
    #     # Too many nearby enemies, move away from group center
    #     avg_x = sum(enemy[0].x for enemy in nearby_enemies) / current_group_size
    #     avg_y = sum(enemy[0].y for enemy in nearby_enemies) / current_group_size
        
    #     # Direction away from group center
    #     away_x = enemy.x - avg_x
    #     away_y = enemy.y - avg_y
        
    #     # Normalize
    #     distance = max(0.1, math.sqrt(away_x * away_x + away_y * away_y))
    #     move_x += (away_x / distance) * 0.5
    #     move_y += (away_y / distance) * 0.5
    
    # # Proximity adjustment
    # for other, distance in nearby_enemies[:int(group_size_pref)]:
    #     if distance < optimal_proximity * 0.7:  # Too close
    #         # Move away from this enemy
    #         dx = enemy.x - other.x
    #         dy = enemy.y - other.y
            
    #         # Normalize
    #         dist = max(0.1, math.sqrt(dx * dx + dy * dy))
    #         move_x += (dx / dist) * 0.3
    #         move_y += (dy / dist) * 0.3
    #     elif distance > optimal_proximity * 1.3:  # Too far
    #         # Move toward this enemy
    #         dx = other.x - enemy.x
    #         dy = other.y - enemy.y
            
    #         # Normalize
    #         dist = max(0.1, math.sqrt(dx * dx + dy * dy))
    #         move_x += (dx / dist) * 0.3
    #         move_y += (dy / dist) * 0.3
    
    # # Apply formation patterns
    # if current_group_size >= 3:  # Need at least 3 enemies for formations
    #     # Calculate group center
    #     center_x = sum(enemy[0].x for enemy in nearby_enemies) / current_group_size
    #     center_y = sum(enemy[0].y for enemy in nearby_enemies) / current_group_size
        
    #     # Leader behavior - move toward the front (player side) of the formation
    #     if formation_role > 0.7:  # Leader role
    #         # Move toward player but maintain group center x-position
    #         leader_x = center_x
    #         leader_y = center_y - 50  # Leader is in front (higher up the screen)
            
    #         leader_dx = leader_x - enemy.x
    #         leader_dy = leader_y - enemy.y
            
    #         # Normalize
    #         dist = max(0.1, math.sqrt(leader_dx * leader_dx + leader_dy * leader_dy))
    #         move_x += (leader_dx / dist) * 0.4
    #         move_y += (leader_dy / dist) * 0.4
        
    #     # Edge/perimeter behavior
    #     elif formation_role < 0.3:  # Edge role
    #         if formation_pattern == 0:  # Line formation
    #             # Position at the edge of a horizontal line
    #             edge_x = center_x + (optimal_proximity * (-1 if enemy.x < center_x else 1))
    #             edge_y = center_y
                
    #             edge_dx = edge_x - enemy.x
    #             edge_dy = edge_y - enemy.y
                
    #             # Normalize
    #             dist = max(0.1, math.sqrt(edge_dx * edge_dx + edge_dy * edge_dy))
    #             move_x += (edge_dx / dist) * 0.4
    #             move_y += (edge_dy / dist) * 0.4
            
    #         elif formation_pattern == 1:  # Circle formation
    #             # Position on the circle perimeter
    #             angle = math.atan2(enemy.y - center_y, enemy.x - center_x)
    #             edge_x = center_x + math.cos(angle) * optimal_proximity
    #             edge_y = center_y + math.sin(angle) * optimal_proximity
                
    #             edge_dx = edge_x - enemy.x
    #             edge_dy = edge_y - enemy.y
                
    #             # Normalize
    #             dist = max(0.1, math.sqrt(edge_dx * edge_dx + edge_dy * edge_dy))
    #             move_x += (edge_dx / dist) * 0.4
    #             move_y += (edge_dy / dist) * 0.4
                
    #         elif formation_pattern == 2:  # Triangle formation
    #             # Position on one of three points of triangle
    #             angle_offset = (enemy.id % 3) * (2 * math.pi / 3)
    #             angle = angle_offset
    #             edge_x = center_x + math.cos(angle) * optimal_proximity
    #             edge_y = center_y + math.sin(angle) * optimal_proximity
                
    #             edge_dx = edge_x - enemy.x
    #             edge_dy = edge_y - enemy.y
                
    #             # Normalize
    #             dist = max(0.1, math.sqrt(edge_dx * edge_dx + edge_dy * edge_dy))
    #             move_x += (edge_dx / dist) * 0.4
    #             move_y += (edge_dy / dist) * 0.4
                
    #         elif formation_pattern == 3:  # Grid formation
    #             # Position on grid point based on ID
    #             grid_size = max(2, int(math.sqrt(current_group_size)))
    #             grid_x = (enemy.id % grid_size) - (grid_size // 2)
    #             grid_y = (enemy.id // grid_size) - (grid_size // 2)
                
    #             edge_x = center_x + grid_x * (optimal_proximity * 0.8)
    #             edge_y = center_y + grid_y * (optimal_proximity * 0.8)
                
    #             edge_dx = edge_x - enemy.x
    #             edge_dy = edge_y - enemy.y
                
    #             # Normalize
    #             dist = max(0.1, math.sqrt(edge_dx * edge_dx + edge_dy * edge_dy))
    #             move_x += (edge_dx / dist) * 0.4
    #             move_y += (edge_dy / dist) * 0.4
        
    #     # Middle/support behavior
    #     else:  # Middle role (0.3 to 0.7)
    #         middle_x = center_x + random.uniform(-20, 20)  # Slight randomization
    #         middle_y = center_y + random.uniform(-20, 20)
            
    #         middle_dx = middle_x - enemy.x
    #         middle_dy = middle_y - enemy.y
            
    #         # Normalize
    #         dist = max(0.1, math.sqrt(middle_dx * middle_dx + middle_dy * middle_dy))
    #         move_x += (middle_dx / dist) * 0.4
    #         move_y += (middle_dy / dist) * 0.4
    
    # # Apply group synchronization - match velocity of nearby enemies
    # if group_sync > 0.3:  # Only if synchronization gene is high enough
    #     avg_dx = 0
    #     avg_dy = 0
    #     count = 0
        
    #     # Get average movement direction of group
    #     for other, _ in nearby_enemies[:int(group_size_pref)]:
    #         if hasattr(other, 'last_pos'):
    #             enemy_dx = other.x - other.last_pos[0]
    #             enemy_dy = other.y - other.last_pos[1]
    #             avg_dx += enemy_dx
    #             avg_dy += enemy_dy
    #             count += 1
        
    #     if count > 0:
    #         avg_dx /= count
    #         avg_dy /= count
            
    #         # Apply synchronization based on gene
    #         move_x = move_x * (1 - group_sync) + avg_dx * group_sync
    #         move_y = move_y * (1 - group_sync) + avg_dy * group_sync
    
    # # Return the calculated group movement direction
    # return move_x, move_y


def apply_group_behavior(enemy, all_enemies):
    """
    Calculate movement influence based on nearby allies.
    Takes into account group size preference, proximity, formation role, and synchronization.
    """

    if not all_enemies:
        return 0.0, 0.0

    group_size_pref = enemy.chromosome[54]
    optimal_proximity = enemy.chromosome[55]
    formation_role = enemy.chromosome[56]
    group_sync = enemy.chromosome[58]

    # Get nearby allies
    nearby = [
        e for e in all_enemies if e != enemy and e.alive
        and math.hypot(e.x - enemy.x, e.y - enemy.y) < optimal_proximity * 1.5
    ]

    if not nearby:
        return 0.0, 0.0

    # Compute average position of the group
    center_x = sum(e.x for e in nearby) / len(nearby)
    center_y = sum(e.y for e in nearby) / len(nearby)

    dx = center_x - enemy.x
    dy = center_y - enemy.y

    dist = math.sqrt(dx ** 2 + dy ** 2)
    dist = max(dist, 1.0)  # Prevent division by zero

    move_x, move_y = 0.0, 0.0

    # Leader Role: Move toward group center
    if formation_role > 0.7:
        move_x += (dx / dist) * group_sync
        move_y += (dy / dist) * group_sync

    # Edge Role: Spread slightly away from center
    elif formation_role < 0.3:
        move_x += (-dx / dist) * 0.4
        move_y += (-dy / dist) * 0.4

    # Middle Role: Stabilize near optimal distance
    else:
        deviation = dist - optimal_proximity
        move_x += (dx / dist) * (deviation / 100.0)
        move_y += (dy / dist) * (deviation / 100.0)

    # Smooth factor
    move_x *= min(1.0, group_sync + 0.2)
    move_y *= min(1.0, group_sync + 0.2)

    return move_x, move_y