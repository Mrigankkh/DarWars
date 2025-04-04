import pygame
import random
import math
from constants import *
from behavior_gene import BehaviorGene
from enemy.enemy_behavior import apply_shooting_behavior
from enemy.enemy_group import apply_group_behavior
from enemy.gene_index import GeneIndex
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
         
            self.chromosome = [
                # 20 behavior genes (binary on/off)
                random.randint(0, 1),  # Gene 0: Aggressive behavior
                random.randint(0, 1),  # Gene 1: Defensive behavior
                random.randint(0, 1),  # Gene 2: Erratic movement
                random.randint(0, 1),  # Gene 3: Tactical positioning
                random.randint(0, 1),  # Gene 4: Kamikaze behavior
                random.randint(0, 1),  # Gene 5: Adaptive behavior
                random.randint(0, 1),  # Gene 6: Move left
                random.randint(0, 1),  # Gene 7: Move right
                random.randint(0, 1),  # Gene 8: Move up
                random.randint(0, 1),  # Gene 9: Move down
                random.randint(0, 1),  # Gene 10: Zigzag pattern
                random.randint(0, 1),  # Gene 11: Circle pattern
                random.randint(0, 1),  # Gene 12: Stop temporarily
                random.randint(0, 1),  # Gene 13: Shoot straight
                random.randint(0, 1),  # Gene 14: Shoot spread
                random.randint(0, 1),  # Gene 15: Shoot burst
                random.randint(0, 1),  # Gene 16: Dodge
                random.randint(0, 1),  # Gene 17: Group with other enemies
                random.randint(0, 1),  # Gene 18: Ambush
                random.randint(0, 1),  # Gene 19: Retreat
                
                # 20 behavior durations (number of frames to perform each behavior)
                random.randint(30, 180),  # Gene 20: Duration for Aggressive
                random.randint(30, 180),  # Gene 21: Duration for Defensive
                random.randint(30, 180),  # Gene 22: Duration for Erratic
                random.randint(30, 180),  # Gene 23: Duration for Tactical
                random.randint(30, 180),  # Gene 24: Duration for Kamikaze
                random.randint(30, 180),  # Gene 25: Duration for Adaptive
                random.randint(30, 180),  # Gene 26: Duration for Move left
                random.randint(30, 180),  # Gene 27: Duration for Move right
                random.randint(30, 180),  # Gene 28: Duration for Move up
                random.randint(30, 180),  # Gene 29: Duration for Move down
                random.randint(30, 180),  # Gene 30: Duration for Zigzag
                random.randint(30, 180),  # Gene 31: Duration for Circle
                random.randint(30, 180),  # Gene 32: Duration for Stop
                random.randint(30, 180),  # Gene 33: Duration for Shoot straight
                random.randint(30, 180),  # Gene 34: Duration for Shoot spread
                random.randint(30, 180),  # Gene 35: Duration for Shoot burst
                random.randint(30, 180),  # Gene 36: Duration for Dodge
                random.randint(30, 180),  # Gene 37: Duration for Group
                random.randint(30, 180),  # Gene 38: Duration for Ambush
                random.randint(30, 180),  # Gene 39: Duration for Retreat
                
                # Attribute modifiers
                random.uniform(0.5, 3.0),    # Gene 40: Speed modifier
                random.uniform(0.5, 2.0),    # Gene 41: Fire rate modifier
                random.uniform(0.5, 1.0),    # Gene 42: Accuracy modifier
                random.uniform(0.5, 1.0),    # Gene 43: Evasion modifier
                random.uniform(0.8, 1.2),    # Gene 44: Health modifier
                random.uniform(0.8, 1.5),    # Gene 45: Bullet speed modifier
                random.uniform(0.8, 2.0),    # Gene 46: Bullet damage modifier
                
                # Gene 47-51: Bullet size probabilities (5 weights for different size categories)
                # These weights will determine the probability of shooting different sized bullets
                # The weights are for: Very Small, Small, Medium, Large, Very Large
                random.uniform(0, 1),        # Gene 47: Weight for Very Small bullets
                random.uniform(0, 1),        # Gene 48: Weight for Small bullets
                random.uniform(0, 1),        # Gene 49: Weight for Medium bullets
                random.uniform(0, 1),        # Gene 50: Weight for Large bullets
                random.uniform(0, 1),        # Gene 51: Weight for Very Large bullets
                
                random.uniform(-50, 50),     # Gene 52: Spawn X offset
                random.uniform(0.1, 1.0),    # Gene 53: Pattern variance
                
                # Group dynamics genes
                random.uniform(1, 10),       # Gene 54: Group size preference (1-10 enemies)
                random.uniform(30, 200),     # Gene 55: Optimal proximity (distance to other enemies)
                random.uniform(0, 1),        # Gene 56: Formation role (0=edge, 0.5=middle, 1=leader)
                random.randint(0, 3),        # Gene 57: Formation pattern (0=line, 1=circle, 2=triangle, 3=grid)
                random.uniform(0, 1),        # Gene 58: Group synchronization (0=independent, 1=highly coordinated)
                
                0.0  # Gene 59: Fitness (initialized to 0)
            ]
        else:
            self.chromosome = chromosome
        
        # Apply genetic traits to enemy attributes
        self.speed *= self.chromosome[40]
        self.bullet_cooldown_max = int(self.bullet_cooldown_max / self.chromosome[41])
        self.bullet_speed *= self.chromosome[45]
       
        self.max_health = self.health
        
        # Apply spawn offset for formation variety
        self.x += self.chromosome[52]
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        
        # Create a color based on the primary behaviors
        r = int(min(255, 128 + (self.chromosome[0] + self.chromosome[4]) * 30))
        g = int(min(255, 128 + (self.chromosome[1] + self.chromosome[16]) * 30))
        b = int(min(255, 128 + (self.chromosome[2] + self.chromosome[11]) * 30))
        self.color = (r, g, b)
        
        # Initialize behavior sequence
        # self.behavior_sequence = []
        # self.create_behavior_sequence()
    
    # def create_behavior_sequence(self):
    #     self.behavior_sequence = []
        
    #     # For each behavior gene that is active, add it to the sequence with its duration
    #     for i in range(20):
    #         if self.chromosome[i] == 1:
    #             self.behavior_sequence.append({
    #                 'behavior': i,
    #                 'duration': self.chromosome[i + 20],  # Corresponding duration
    #                 'variance': self.chromosome[53]  # Pattern variance affects timing
    #             })
        
    #     # If no behaviors are active, add a default "aggressive" behavior
    #     if not self.behavior_sequence:
    #         self.behavior_sequence.append({
    #             'behavior': BehaviorGene.AGGRESSIVE.value,
    #             'duration': 60,
    #             'variance': 0.5
    #         })
    
    # def get_current_behavior(self):
    #     if not self.behavior_sequence:
    #         # Default behavior if sequence is empty
    #         return {
    #             'behavior': BehaviorGene.AGGRESSIVE.value,
    #             'duration': 60,
    #             'variance': 0.5
    #         }
        
    #     if self.current_behavior_index >= len(self.behavior_sequence):
    #         self.current_behavior_index = 0  # Reset if index is out of bounds
            
    #     return self.behavior_sequence[self.current_behavior_index]
    
    def get_random_bullet_size(self):
        # Get the weights for different bullet sizes
        weights = self.chromosome[47:52]  # Genes 47-51 are the size weights
        
        # Normalize weights to sum to 1.0 (convert to probabilities)
        total_weight = sum(weights)
        if total_weight == 0:
            # If all weights are 0, use equal probabilities
            probabilities = [0.2, 0.2, 0.2, 0.2, 0.2]
        else:
            probabilities = [w / total_weight for w in weights]
        
        # Define size ranges for each category
        size_ranges = [
            (0.5, 0.7),    # Very Small
            (0.8, 0.9),    # Small
            (1.0, 1.2),    # Medium
            (1.3, 1.5),    # Large
            (1.6, 2.0)     # Very Large
        ]
        
        # Choose a size category based on probabilities
        category_index = random.choices(range(5), probabilities)[0]
        
        # Get a random size within the selected range
        min_size, max_size = size_ranges[category_index]
        return random.uniform(min_size, max_size)
    
    def move(self, player, all_enemies=None):
        previous_x, previous_y = self.x, self.y
        
        # Update behavior sequence timer
        self.behavior_timer -= 1
        
        # If current behavior duration has expired, move to next behavior
        # current_behavior = self.get_current_behavior()
        # if self.behavior_timer >= current_behavior['duration']:
        #     self.behavior_timer = 0
        #     self.current_behavior_index = (self.current_behavior_index + 1) % len(self.behavior_sequence)
        #     current_behavior = self.get_current_behavior()  # Get the new current behavior
        # Pick new behavior if timer is up
        # if self.behavior_timer <= 0:
        #     self.current_behavior_id = self.decide_behavior(player, all_enemies)
        #     duration_index = GeneIndex.DURATION_START + self.current_behavior_id
        #     self.behavior_timer = int(self.chromosome[duration_index])

        # behavior_id = self.current_behavior_id
        # self.behavior_timer -= 1
        if self.behavior_timer <= 0:
            new_behavior_id = self.decide_behavior(player, all_enemies)

            if new_behavior_id != getattr(self, "current_behavior_id", None):
                self.behavior_log.append({
                    "frame": self.time_alive,
                    "enemy_id": self.id,
                    "from": BehaviorGene(self.current_behavior_id).name if hasattr(self, "current_behavior_id") else "NONE",
                    "to": BehaviorGene(new_behavior_id).name
                })
                print(f"[Enemy {self.id}] Switching from {BehaviorGene(self.current_behavior_id).name} to {BehaviorGene(new_behavior_id).name}")


            self.current_behavior_id = new_behavior_id
            duration_index = GeneIndex.DURATION_START + self.current_behavior_id
            self.behavior_timer = int(self.chromosome[duration_index])


        # Calculate direction vector to player
        dx = player.x - self.x
        dy = player.y - self.y
        distance = max(1, math.sqrt(dx * dx + dy * dy))  # Avoid division by zero
        dx /= distance
        dy /= distance
        
        # Default movement is a slight downward drift
        move_x, move_y = 0, 0.5
        
        # Execute the current behavior in the sequence
        # behavior_id = current_behavior['behavior']
        # variance = current_behavior['variance']
        behavior_id = self.current_behavior_id
        variance = self.chromosome[GeneIndex.BEHAVIOR_VARIANCE]
        # Apply variance to movement for unpredictability
        variance_factor = random.uniform(1 - variance, 1 + variance)
        
        # Group behavior - evaluate group dynamics if Group behavior is active and we have all_enemies
        if behavior_id == BehaviorGene.GROUP.value and all_enemies:
            group_move_x, group_move_y = apply_group_behavior(self, all_enemies)
            move_x += group_move_x * variance_factor
            move_y += group_move_y * variance_factor
        
        # Standard behaviors (0-5)
        elif behavior_id == BehaviorGene.AGGRESSIVE.value:  # Aggressive - chase player
            move_x += dx * variance_factor
            move_y += dy * variance_factor
            
        elif behavior_id == BehaviorGene.DEFENSIVE.value:  # Defensive - maintain distance
            ideal_distance = 200
            if distance < ideal_distance:
                move_x -= dx * 0.5 * variance_factor
                move_y -= dy * 0.5 * variance_factor
            elif distance > ideal_distance + 50:
                move_x += dx * 0.3 * variance_factor
                move_y += dy * 0.3 * variance_factor
                
        elif behavior_id == BehaviorGene.ERRATIC.value:  # Erratic - random movement
            move_x += random.uniform(-1, 1) * 0.8 * variance_factor
            move_y += random.uniform(-1, 1) * 0.8 * variance_factor
            
        elif behavior_id == BehaviorGene.TACTICAL.value:  # Tactical - flank player
            perpendicular_x = -dy
            perpendicular_y = dx
            move_x += perpendicular_x * 0.6 * variance_factor
            move_y += perpendicular_y * 0.6 * variance_factor
            
        elif behavior_id == BehaviorGene.KAMIKAZE.value:  # Kamikaze - direct rush
            move_x = dx * 1.5 * variance_factor
            move_y = dy * 1.5 * variance_factor
            
        elif behavior_id == BehaviorGene.ADAPTIVE.value:  # Adaptive - based on health
            health_percent = self.health / self.max_health
            if health_percent < 0.3:  # Low health - retreat
                move_x = -dx * variance_factor
                move_y = -dy * variance_factor
            elif health_percent > 0.7:  # High health - aggressive
                move_x = dx * 1.2 * variance_factor
                move_y = dy * 1.2 * variance_factor
                
        # Extended behaviors (6-19)
        elif behavior_id == BehaviorGene.MOVE_LEFT.value:  # Move left
            move_x = -1.0 * variance_factor
            move_y = 0.2
            
        elif behavior_id == BehaviorGene.MOVE_RIGHT.value:  # Move right
            move_x = 1.0 * variance_factor
            move_y = 0.2
            
        elif behavior_id == BehaviorGene.MOVE_UP.value:  # Move up
            move_x = 0
            move_y = -0.8 * variance_factor
            
        elif behavior_id == BehaviorGene.MOVE_DOWN.value:  # Move down
            move_x = 0
            move_y = 1.0 * variance_factor
            
        elif behavior_id == BehaviorGene.ZIGZAG.value:  # Zigzag pattern
            # Use time to create zigzag motion
            zigzag_x = math.sin(self.time_alive * 0.1) * variance_factor
            move_x = zigzag_x
            move_y = 0.5
            
        elif behavior_id == BehaviorGene.CIRCLE.value:  # Circle pattern
            # Use time to create circular motion
            angle = self.time_alive * 0.05
            circle_x = math.cos(angle) * variance_factor
            circle_y = math.sin(angle) * variance_factor
            move_x = circle_x
            move_y = circle_y + 0.2  # Slight downward drift
            
        elif behavior_id == BehaviorGene.STOP.value:  # Stop temporarily
            move_x = 0
            move_y = 0
            
        elif behavior_id == BehaviorGene.DODGE.value:  # Try to dodge player bullets
            # Find closest player bullet
            closest_bullet = None
            closest_dist = float('inf')
            for bullet in player.bullets:
                bullet_dx = bullet['x'] - self.x
                bullet_dy = bullet['y'] - self.y
                bullet_dist = math.sqrt(bullet_dx**2 + bullet_dy**2)
                if bullet_dist < closest_dist:
                    closest_dist = bullet_dist
                    closest_bullet = bullet
            
            # If a bullet is nearby, try to dodge
            if closest_bullet and closest_dist < 150:
                bullet_dx = closest_bullet['x'] - self.x
                bullet_dy = closest_bullet['y'] - self.y
                # Move perpendicular to bullet trajectory
                dodge_x = -bullet_dy
                dodge_y = bullet_dx
                move_x = dodge_x * variance_factor
                move_y = dodge_y * variance_factor
            else:
                # Default slight movement
                move_x += random.uniform(-0.3, 0.3)
                move_y += 0.3
        
        elif behavior_id == BehaviorGene.AMBUSH.value:  # Set up ambush
            # Try to position above the player
            if self.y < player.y - 150:
                move_x = dx * 0.5 * variance_factor
                move_y = 0.1  # Very slow vertical movement
            else:
                move_y = -0.5  # Move up if too close
                
        elif behavior_id == BehaviorGene.RETREAT.value:  # Retreat from player
            move_x = -dx * variance_factor
            move_y = -dy * variance_factor
        
        # Apply shooting behaviors here based on the current behavior
        apply_shooting_behavior(self, player, behavior_id)
                
        # Normalize movement vector to maintain consistent speed
        move_length = max(0.1, math.sqrt(move_x * move_x + move_y * move_y))
        move_x = (move_x / move_length) * self.speed
        move_y = (move_y / move_length) * self.speed
        
        # Update position
        self.x += move_x
        self.y += move_y
        
        # Keep enemy within screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))
        
        # Calculate distance moved for fitness
        self.distance_moved += math.sqrt((self.x - previous_x) ** 2 + (self.y - previous_y) ** 2)
        self.last_pos = (self.x, self.y)
    
    def shoot(self, player):
        # Check if we're in a specific shooting behavior
        #current_behavior = self.get_current_behavior()
        behavior_id = self.current_behavior_id

        #behavior_id = current_behavior['behavior']
        
        # Skip if we're in a dedicated shooting behavior (handled in move method)
        if behavior_id in [BehaviorGene.SHOOT_STRAIGHT.value, 
                          BehaviorGene.SHOOT_SPREAD.value, 
                          BehaviorGene.SHOOT_BURST.value]:
            return
        
        # Regular shooting behavior
        if self.bullet_cooldown <= 0:
            # Calculate direction to player
            dx = player.x - self.x
            dy = player.y - self.y
            distance = max(1, math.sqrt(dx * dx + dy * dy))
            dx /= distance
            dy /= distance
            
            # Apply accuracy modifier
            accuracy = self.chromosome[42]
            dx += random.uniform(-0.5, 0.5) * (1 - accuracy)
            dy += random.uniform(-0.5, 0.5) * (1 - accuracy)
            
            # Normalize direction
            direction_length = math.sqrt(dx * dx + dy * dy)
            dx = (dx / direction_length) * self.bullet_speed
            dy = (dy / direction_length) * self.bullet_speed
            
            # Get random bullet size based on probability distribution in genes
            bullet_size = self.get_random_bullet_size()
            
            # Size affects speed (smaller = faster)
            speed_multiplier = max(0.5, 1.0 + (1.0 - bullet_size))  # Ensure minimum speed
            
            self.bullets.append({
                'x': self.x + self.width / 2,
                'y': self.y + self.height / 2,
                'dx': dx * speed_multiplier,
                'dy': dy * speed_multiplier,
                'width': 5 * bullet_size,
                'height': 5 * bullet_size
            })
            
            # Reset cooldown - larger bullets take longer to reload
            reload_multiplier = 0.7 + (bullet_size * 0.6)  # 0.7 to 1.3 based on size
            self.bullet_cooldown = int(self.bullet_cooldown_max * reload_multiplier)
            self.shots_fired += 1
        else:
            self.bullet_cooldown -= 1
    
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
            export_behavior_log(self)
    
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
        from enemy.enemy_fitness import calculate_enemy_fitness
        return calculate_enemy_fitness(self)
    
    def decide_behavior(self, player, enemies):
        chrom = self.chromosome
        scores = {}
        
        dist = math.hypot(player.x - self.x, player.y - self.y)
        
        if chrom[GeneIndex.AGGRESSIVE]:
            scores["AGGRESSIVE"] = max(0, 1.0 - dist / 300)

        if chrom[GeneIndex.RETREAT] and dist < 200:
            scores["RETREAT"] = 1.0

        if chrom[GeneIndex.DODGE] and any(
            math.hypot(b['x'] - self.x, b['y'] - self.y) < 120 for b in player.bullets
        ):
            scores["DODGE"] = chrom[GeneIndex.EVASION]

        if chrom[GeneIndex.SHOOT_SPREAD] and 100 < dist < 500:
            scores["SHOOT_SPREAD"] = chrom[GeneIndex.ACCURACY]

        if chrom[GeneIndex.GROUP] and enemies:
            nearby = sum(
                1 for e in enemies if e.alive and e != self and math.hypot(e.x - self.x, e.y - self.y) < 250
            )
            if nearby >= chrom[GeneIndex.GROUP_SIZE_PREFERENCE]:
                scores["GROUP"] = chrom[GeneIndex.FORMATION_SYNC]

        if not scores:
            return BehaviorGene.AGGRESSIVE.value  # Fallback

        best_behavior = max(scores.items(), key=lambda item: item[1])[0]
        return BehaviorGene[best_behavior].value


import json

def export_behavior_log(self):
    return
    # if self.behavior_log:
    #     with open(f"logs/behavior_log_enemy_{self.id}.json", "w") as f:
    #         json.dump(self.behavior_log, f, indent=2)
