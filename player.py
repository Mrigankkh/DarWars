import pygame
import math
import random
from constants import *

class Player:
    def __init__(self, screen):
        self.screen = screen
        self.width = 30
        self.height = 30
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 50
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.bullets = []
        self.bullet_cooldown = 0
        self.bullet_cooldown_max = 15
        self.alive = True
        # Special weapon: Ring of Fire
        self.has_special_weapon = True
        self.special_weapon_radius = 150
        self.special_weapon_frames = 0
        self.special_weapon_active = False
    
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # Keep player within screen bounds
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))
    
    def shoot(self, keys):
        if (keys[pygame.K_SPACE] and self.bullet_cooldown <= 0):
            # Create bullet
            self.bullets.append({
                'x': self.x + self.width / 2 - 2.5,
                'y': self.y,
                'width': 5,
                'height': 10,
                'speed': 10
            })
            
            # Reset cooldown
            self.bullet_cooldown = self.bullet_cooldown_max
        else:
            self.bullet_cooldown -= 1
    
    def update_bullets(self, enemies):
        bullets_to_remove = []
        
        for i, bullet in enumerate(self.bullets):
            # Move bullet
            bullet['y'] -= bullet['speed']
            
            # Check if bullet is out of bounds
            if bullet['y'] < 0:
                bullets_to_remove.append(i)
                continue
            
            # Check collision with enemies
            for enemy in enemies:
                if not enemy.alive:
                    continue
                
                if (bullet['x'] < enemy.x + enemy.width and
                    bullet['x'] + bullet['width'] > enemy.x and
                    bullet['y'] < enemy.y + enemy.height and
                    bullet['y'] + bullet['height'] > enemy.y):
                    
                    # Hit enemy - enemies only have 1 HP
                    enemy.take_damage(1)
                    bullets_to_remove.append(i)
                    break
        
        # Remove bullets marked for deletion (in reverse order to avoid index issues)
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.bullets):
                self.bullets.pop(i)
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def use_special_weapon(self, enemies):
        if self.has_special_weapon and not self.special_weapon_active:
            self.special_weapon_active = True
            self.special_weapon_frames = 30  # Animation will last for 30 frames
            self.has_special_weapon = False  # One-time use
            
            # Destroy enemies within radius
            enemies_destroyed = 0
            for enemy in enemies:
                if not enemy.alive:
                    continue
                
                # Calculate distance to enemy
                dx = enemy.x + enemy.width / 2 - (self.x + self.width / 2)
                dy = enemy.y + enemy.height / 2 - (self.y + self.height / 2)
                distance = math.sqrt(dx * dx + dy * dy)
                
                # If enemy is within radius, destroy it
                if distance <= self.special_weapon_radius:
                    enemy.take_damage(enemy.health)  # Kill instantly
                    enemies_destroyed += 1
            
            return enemies_destroyed
        
        return 0
    
    def update_special_weapon(self):
        if self.special_weapon_active:
            self.special_weapon_frames -= 1
            if self.special_weapon_frames <= 0:
                self.special_weapon_active = False
    
    def draw_special_weapon(self):
        if self.special_weapon_active:
            # Calculate alpha (transparency) based on remaining frames
            alpha = int(255 * (self.special_weapon_frames / 30))
            
            # Create a surface for the ring
            ring_surface = pygame.Surface((self.special_weapon_radius * 2, self.special_weapon_radius * 2), pygame.SRCALPHA)
            
            # Calculate center position for the fire ring
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            
            # Draw pulsing ring of fire with particles
            for i in range(20):  # Draw 20 fire particles
                angle = random.uniform(0, math.pi * 2)
                radius = self.special_weapon_radius * random.uniform(0.7, 1.0)
                particle_x = self.special_weapon_radius + math.cos(angle) * radius
                particle_y = self.special_weapon_radius + math.sin(angle) * radius
                size = random.randint(5, 15)
                
                # Gradient from yellow to red
                color_mix = random.uniform(0, 1)
                r = int(255)
                g = int(255 * (1 - color_mix))
                b = 0
                
                pygame.draw.circle(ring_surface, (r, g, b, alpha), (particle_x, particle_y), size)
            
            # Draw main ring
            pygame.draw.circle(ring_surface, (255, 100, 0, alpha), (self.special_weapon_radius, self.special_weapon_radius), self.special_weapon_radius, 3)
            
            # Draw to screen
            self.screen.blit(ring_surface, (center_x - self.special_weapon_radius, center_y - self.special_weapon_radius))
    
    def draw_special_weapon_indicator(self):
        # Draw indicator to show if special weapon is available
        if self.has_special_weapon:
            pygame.draw.circle(self.screen, (255, 200, 0), (30, SCREEN_HEIGHT - 30), 10)
            text = pygame.font.SysFont('Arial', 20).render("F/Q", True, BLACK)
            self.screen.blit(text, (20, SCREEN_HEIGHT - 36))
    
    def draw(self):
        # Draw player
        pygame.draw.rect(self.screen, BLUE, (self.x, self.y, self.width, self.height))
        
        # Draw health bar
        health_percentage = self.health / self.max_health
        health_bar_width = self.width * health_percentage
        pygame.draw.rect(self.screen, RED, (self.x, self.y - 15, self.width, 10))
        pygame.draw.rect(self.screen, GREEN, (self.x, self.y - 15, health_bar_width, 10))
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.rect(self.screen, GREEN, 
                            (bullet['x'], bullet['y'], bullet['width'], bullet['height']))
        
        # Draw special weapon effect
        self.draw_special_weapon()
        
        # Draw special weapon indicator
        self.draw_special_weapon_indicator()