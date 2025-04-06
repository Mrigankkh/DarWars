import pygame
import random
import math
from constants import *
from behavior_gene import BehaviorGene
from enemy.enemy_group import apply_group_behavior
from enemy.gene_index import GeneIndex
from enemy.enemy_bullet import create_bullet,get_bullet_size_from_bias  # Make sure this import is at the top
from enemy.enemy_fitness import calculate_enemy_fitness

class Enemy:
    def __init__(self, screen, chromosome=None):
        
        ## Logging
        self.behavior_log = []  # Stores timestamped behavior changes

        self.screen = screen
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, 100)
        self.width = 25
        self.height = 25
        self.speed = 1.2  
        self.health = 1
        self.max_health = 1
        self.bullet_speed = 3  
        self.bullets = []
        self.bullet_cooldown = 0
        self.bullet_cooldown_max = 90 
        self.color = RED
        self.alive = True
        self.damage_dealt = 0
        self.time_alive = 0
        self.distance_moved = 0
        self.shots_fired = 0
        self.hits_scored = 0
        self.fitness = 0
        self.last_pos = (self.x, self.y)
        
        self.id = random.randint(0, 1000)
        
        self.current_behavior_index = 0
        self.behavior_timer = 0
        self.current_behavior_id = BehaviorGene.AGGRESSIVE.value 
        
        if chromosome is None:
            self.chromosome = {
    # Behavior genes (binary on/off)
    0: random.uniform(0, 1),  # Aggressive behavior
    1: random.uniform(0, 1),  # Defensive behavior
    3: random.uniform(0, 1),  # Tactical positioning
    4: 1,  # Kamikaze behavior
    5: random.uniform(0, 1),  # Adaptive behavior
    10: random.uniform(0, 1),  # Zigzag pattern
    11: random.uniform(0, 1),  # Circle pattern
    12: random.uniform(0, 1),  # Stop temporarily
    13: random.uniform(0, 1),  # Shoot straight
    14: random.uniform(0, 1),  # Shoot spread
    15: random.uniform(0, 1),  # Shoot burst
    16: random.uniform(0, 1),  # Dodge
    18: random.uniform(0, 1),  # Ambush

    # Attribute modifiers
    40: random.uniform(0.5, 3.0),  # Speed modifier
    41: random.uniform(0.5, 2.0),  # Fire rate modifier
    42: random.uniform(0.5, 1.0),  # Accuracy modifier
    43: random.uniform(0.5, 1.0),  # Evasion modifier
    45: random.uniform(0.8, 1.5),  # Bullet speed modifier
    46: random.uniform(0.8, 2.0),  # Bullet damage modifier

    # Bullet size (reduced to a single gene)
    47: random.uniform(0, 1),  # Bullet size probability

    # Formation / Pattern stuff
    52: random.uniform(-50, 50),  # Spawn X offset
    53: random.uniform(0.1, 1.0),  # Pattern variance

    # Group dynamics
    17: random.betavariate(2, 5),  # Group with other enemies

    54: random.uniform(1, 10),     # Group size preference (1-10 enemies)
    55: random.uniform(30, 200),   # Optimal proximity
    56: random.uniform(0, 1),      # Formation role
    57: random.randint(0, 3),      # Formation pattern
    58: random.uniform(0, 1),      # Group synchronization

    59: 0.0  # Fitness
}


        else:
            self.chromosome = chromosome
        
        # Apply genetic traits to enemy attributes
        self.speed *= self.chromosome[GeneIndex.SPEED]
        self.bullet_cooldown_max = int(self.bullet_cooldown_max / self.chromosome[41])
        self.bullet_speed *= self.chromosome[GeneIndex.BULLET_SPEED]
       
        self.max_health = self.health
        
        # Apply spawn offset for formation variety
        self.x += self.chromosome[52]
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        
        # Create a color based on the primary behaviors
        r = int(min(255, 128 + (self.chromosome[0] + self.chromosome[4]) * 30))
        g = int(min(255, 128 + (self.chromosome[1] + self.chromosome[16]) * 30))
        b = int(min(255, 128 + (self.chromosome[3] + self.chromosome[11]) * 30))
        self.color = (r, g, b)

    
    def get_random_bullet_size(self):
        bullet_bias = self.chromosome[47]  # Single gene for bullet size bias
        return get_bullet_size_from_bias(bullet_bias)
   
    def move(self, player, all_enemies=None):
        previous_x, previous_y = self.x, self.y

        # Step 1: Evaluate all active behaviors and their weights
        behavior_weights = self.evaluate_behavior_weights(player, all_enemies)

        # Step 2: Get the net movement vector based on weighted behaviors
        
        
        indiv_x, indiv_y = self.get_behavior_vector(player, all_enemies)
        group_x, group_y = apply_group_behavior(self, all_enemies)
        group_weight = self.chromosome.get(GeneIndex.GROUP, 0.0)  # Previously a binary flag, now interpreted as weight
        # Final blended movement vector
        final_x = indiv_x * (1 - group_weight) + group_x * group_weight
        final_y = indiv_y * (1 - group_weight) + group_y * group_weight
        variance = self.chromosome.get(GeneIndex.BEHAVIOR_VARIANCE, 0.5)
        variance_factor = random.uniform(1 - variance, 1 + variance)

        move_length = max(0.1, math.sqrt(final_x**2 + final_y**2))
        move_x = (final_x / move_length) * self.speed * variance_factor
        move_y = (final_y / move_length) * self.speed * variance_factor

      
        self.x += move_x
        self.y += move_y

        # Step 5: Clamp to screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))

        # Step 6: Track stats for fitness
        self.distance_moved += math.sqrt((self.x - previous_x) ** 2 + (self.y - previous_y) ** 2)
        self.last_pos = (self.x, self.y)

    
    def shoot(self, player):
        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1
            return

        behavior_id = self.current_behavior_id

        # Skip dedicated shooting behaviors (those handled in move)
        if behavior_id in [BehaviorGene.SHOOT_STRAIGHT.value, 
                        BehaviorGene.SHOOT_SPREAD.value, 
                        BehaviorGene.SHOOT_BURST.value]:
            return

        # Bullet size from gene bias
        bullet_size = get_bullet_size_from_bias(self.chromosome[47])

        # Adjust speed for large bullets
        speed_multiplier = max(0.5, 1.0 + (1.0 - bullet_size))

        # Accuracy penalty if moving
        base_accuracy = self.chromosome[42]
        if getattr(self, "is_moving", False):
            accuracy = base_accuracy * 0.8
        else:
            accuracy = base_accuracy

        # Create bullet and fire
        #todo: reduce acc whille moving
        bullet = create_bullet(self, player, bullet_size, speed_multiplier)
        self.bullets.append(bullet)

        # Reload time scaled by bullet size
        reload_multiplier = 0.7 + (bullet_size * 0.6)
        self.bullet_cooldown = int(self.bullet_cooldown_max * reload_multiplier)
        self.shots_fired += 1
   
    def update_bullets(self, player):
        bullets_to_remove = []
        
        for i, bullet in enumerate(self.bullets):
            # Move bullet
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            # Check if bullet is out of bounds
            if (bullet['x'] < 0 or bullet['x'] > SCREEN_WIDTH or
                bullet['y'] < 0 or bullet['y'] > SCREEN_HEIGHT):
                bullets_to_remove.append(i)
                continue
            
            # Check collision with player
            if (bullet['x'] < player.x + player.width and
                bullet['x'] + bullet['width'] > player.x and
                bullet['y'] < player.y + player.height and
                bullet['y'] + bullet['height'] > player.y):
                
                # Hit player
                player.take_damage(10 * self.chromosome[46])  # Apply bullet damage modifier
                bullets_to_remove.append(i)
                self.damage_dealt += 10 * self.chromosome[46]
                self.hits_scored += 1
        
        # Remove bullets marked for deletion (in reverse order to avoid index issues)
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.bullets):
                self.bullets.pop(i)
    
    def take_damage(self, amount):
        """Handle enemy taking damage"""
        self.health -= amount
        # Ensure enemies die with 1 hit regardless of health modifiers from genes
        if self.health <= 0:
            self.alive = False
            
  
    def draw(self):
        # Draw enemy
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))
        
        # Draw health bar
        health_percentage = self.health / self.max_health
        health_bar_width = self.width * health_percentage
        pygame.draw.rect(self.screen, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(self.screen, GREEN, (self.x, self.y - 10, health_bar_width, 5))
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.rect(self.screen, YELLOW, 
                           (bullet['x'], bullet['y'], bullet['width'], bullet['height']))
    
    def calculate_fitness(self):
        # Import the function to avoid circular imports
        return calculate_enemy_fitness(self)
    

    def evaluate_behavior_weights(self, player, all_enemies=None):
        weights = {}

        for i in range(20):
            if self.chromosome.get(i, 0) == 1:
                weight = 1.0  # default
                #if player is not None:
                    # if i == BehaviorGene.DEFENSIVE.value:
                    #     dx = player.x - self.x
                    #     dy = player.y - self.y
                    #     dist = math.sqrt(dx**2 + dy**2)
                    #     if dist < 200:
                    #         weight += 1.0  

                    

                weights[i] = weight

        return weights

    
    def get_behavior_vector(self, player, all_enemies=None):
        behavior_weights = self.evaluate_behavior_weights(player, all_enemies)
        
        total_weight = sum(behavior_weights.values())
        if total_weight == 0:
            return 0, 0  # No active behaviors

        move_x, move_y = 0, 0

        for behavior_id, weight in behavior_weights.items():
            influence_x, influence_y = self.get_movement_influence(behavior_id, player, all_enemies)
            move_x += influence_x * (weight / total_weight)
            move_y += influence_y * (weight / total_weight)

        return move_x, move_y
    
    
    def get_movement_influence(self, behavior_id, player, all_enemies=None):
        
        dx = player.x - self.x
        dy = player.y - self.y
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        dx /= distance
        dy /= distance

        variance = self.chromosome[53]  # Pattern variance gene
        variance_factor = random.uniform(1 - variance, 1 + variance)

        if behavior_id == BehaviorGene.AGGRESSIVE.value:
            return dx * variance_factor, dy * variance_factor

        elif behavior_id == BehaviorGene.DEFENSIVE.value:
            ideal_distance = 200
            if distance < ideal_distance:
                return -dx * 0.5 * variance_factor, -dy * 0.5 * variance_factor
            elif distance > ideal_distance + 50:
                return dx * 0.3 * variance_factor, dy * 0.3 * variance_factor
            else:
                return 0, 0.1  # Slight drift

        elif behavior_id == BehaviorGene.TACTICAL.value:
            # Perpendicular to player direction = flanking
            return -dy * 0.6 * variance_factor, dx * 0.6 * variance_factor

        elif behavior_id == BehaviorGene.KAMIKAZE.value:
            return dx * 1.5 * variance_factor, dy * 1.5 * variance_factor

        # elif behavior_id == BehaviorGene.ADAPTIVE.value:
        #     health_percent = self.health / self.max_health
        #     if health_percent < 0.3:
        #         return -dx * variance_factor, -dy * variance_factor
        #     elif health_percent > 0.7:
        #         return dx * 1.2 * variance_factor, dy * 1.2 * variance_factor
        #     else:
        #         return 0.5 * dx, 0.5 * dy

        elif behavior_id == BehaviorGene.ZIGZAG.value:
            zigzag_x = math.sin(self.time_alive * 0.1) * variance_factor
            return zigzag_x, 0.5

        elif behavior_id == BehaviorGene.CIRCLE.value:
            angle = self.time_alive * 0.05
            return math.cos(angle) * variance_factor, math.sin(angle) * variance_factor

        elif behavior_id == BehaviorGene.STOP.value:
            return 0, 0

        elif behavior_id == BehaviorGene.DODGE.value:
            closest_bullet = None
            closest_dist = float('inf')
            for bullet in player.bullets:
                bdx = bullet['x'] - self.x
                bdy = bullet['y'] - self.y
                dist = math.sqrt(bdx**2 + bdy**2)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_bullet = bullet
            if closest_bullet and closest_dist < 150:
                dodge_x = -bdy
                dodge_y = bdx
                return dodge_x * variance_factor, dodge_y * variance_factor
            else:
                return random.uniform(-0.3, 0.3), 0.3

        elif behavior_id == BehaviorGene.AMBUSH.value:
            if self.y < player.y - 150:
                return dx * 0.5 * variance_factor, 0.1
            else:
                return 0, -0.5

        # Default fallback
        return 0, 0.5  # Slight downward drift
   
    def get_shooting_influence(self, player, weights):
        """Blend shooting behaviors based on weighted influences."""
        total_weight = sum(weights.values())
        if total_weight == 0 or self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1
            return

        # Normalize weights
        norm_weights = {k: v / total_weight for k, v in weights.items()}

        # Accuracy penalty if moving
        moving_penalty = 0.0
        if self.speed > 0.1:  # optionally detect actual movement
            moving_penalty = 1 - self.chromosome[42]  # lower accuracy if moving

        # Shoot straight
        if BehaviorGene.SHOOT_STRAIGHT.value in norm_weights:
            prob = norm_weights[BehaviorGene.SHOOT_STRAIGHT.value]
            if random.random() < prob:
                self.fire_bullet(player, pattern="straight", penalty=moving_penalty)

        # Shoot spread
        if BehaviorGene.SHOOT_SPREAD.value in norm_weights:
            prob = norm_weights[BehaviorGene.SHOOT_SPREAD.value]
            if random.random() < prob:
                self.fire_bullet(player, pattern="spread", penalty=moving_penalty)

        # Shoot burst
        if BehaviorGene.SHOOT_BURST.value in norm_weights:
            prob = norm_weights[BehaviorGene.SHOOT_BURST.value]
            if random.random() < prob:
                for _ in range(3):  # fire 3 quick shots
                    self.fire_bullet(player, pattern="straight", penalty=moving_penalty * 1.2)
