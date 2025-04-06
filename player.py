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
        
        # Random shooting direction for this round
        self.shooting_angle =  1.5 * math.pi
        self.direction_indicator_length = 30
    
    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))
    
    def shoot(self, keys):
        if (keys[pygame.K_SPACE] and self.bullet_cooldown <= 0):
           
            dx = math.cos(self.shooting_angle)
            dy = math.sin(self.shooting_angle)
            
            
            self.bullets.append({
                'x': self.x + self.width / 2 - 2.5,
                'y': self.y + self.height / 2,
                'width': 5,
                'height': 10,
                'dx': dx * 10,
                'dy': dy * 10
            })
            
            self.bullet_cooldown = self.bullet_cooldown_max
        else:
            self.bullet_cooldown -= 1
    
    def update_bullets(self, enemies):
        bullets_to_remove = []
        
        for i, bullet in enumerate(self.bullets):
          
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
           
            if (bullet['x'] < 0 or bullet['x'] > SCREEN_WIDTH or
                bullet['y'] < 0 or bullet['y'] > SCREEN_HEIGHT):
                bullets_to_remove.append(i)
                continue
            
            
            for enemy in enemies:
                if not enemy.alive:
                    continue
                
                if (bullet['x'] < enemy.x + enemy.width and
                    bullet['x'] + bullet['width'] > enemy.x and
                    bullet['y'] < enemy.y + enemy.height and
                    bullet['y'] + bullet['height'] > enemy.y):
                    
                 
                    enemy.take_damage(1)
                    bullets_to_remove.append(i)
                    break
        
        
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
            self.special_weapon_frames = 30 
            self.has_special_weapon = False  
            
           
            enemies_destroyed = 0
            for enemy in enemies:
                if not enemy.alive:
                    continue
                
                
                dx = enemy.x + enemy.width / 2 - (self.x + self.width / 2)
                dy = enemy.y + enemy.height / 2 - (self.y + self.height / 2)
                distance = math.sqrt(dx * dx + dy * dy)
                
              
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
          
            alpha = int(255 * (self.special_weapon_frames / 30))
            
           
            ring_surface = pygame.Surface((self.special_weapon_radius * 2, self.special_weapon_radius * 2), pygame.SRCALPHA)
            
         
            center_x = self.x + self.width / 2
            center_y = self.y + self.height / 2
            
            
            for i in range(20):  
                angle = random.uniform(0, math.pi * 2)
                radius = self.special_weapon_radius * random.uniform(0.7, 1.0)
                particle_x = self.special_weapon_radius + math.cos(angle) * radius
                particle_y = self.special_weapon_radius + math.sin(angle) * radius
                size = random.randint(5, 15)
                
                
                color_mix = random.uniform(0, 1)
                r = int(255)
                g = int(255 * (1 - color_mix))
                b = 0
                
                pygame.draw.circle(ring_surface, (r, g, b, alpha), (particle_x, particle_y), size)
            
            
            pygame.draw.circle(ring_surface, (255, 100, 0, alpha), (self.special_weapon_radius, self.special_weapon_radius), self.special_weapon_radius, 3)
            
           
            self.screen.blit(ring_surface, (center_x - self.special_weapon_radius, center_y - self.special_weapon_radius))
    
    def draw_special_weapon_indicator(self):
       
        if self.has_special_weapon:
            pygame.draw.circle(self.screen, (255, 200, 0), (30, SCREEN_HEIGHT - 30), 10)
            text = pygame.font.SysFont('Arial', 20).render("F/Q", True, BLACK)
            self.screen.blit(text, (20, SCREEN_HEIGHT - 36))
    
    def draw(self):
       
        pygame.draw.rect(self.screen, BLUE, (self.x, self.y, self.width, self.height))
        
       
        indicator_start_x = self.x + self.width // 2
        indicator_start_y = self.y + self.height // 2
        indicator_end_x = indicator_start_x + math.cos(self.shooting_angle) * self.direction_indicator_length
        indicator_end_y = indicator_start_y + math.sin(self.shooting_angle) * self.direction_indicator_length
        pygame.draw.line(self.screen, YELLOW, 
                        (indicator_start_x, indicator_start_y), 
                        (indicator_end_x, indicator_end_y), 
                        3)  
        
       
        health_percentage = self.health / self.max_health
        health_bar_width = self.width * health_percentage
        pygame.draw.rect(self.screen, RED, (self.x, self.y - 15, self.width, 10))
        pygame.draw.rect(self.screen, GREEN, (self.x, self.y - 15, health_bar_width, 10))
        
        for bullet in self.bullets:
            angle = math.atan2(bullet['dy'], bullet['dx'])
            
            bullet_surface = pygame.Surface((bullet['width'], bullet['height']), pygame.SRCALPHA)
            pygame.draw.rect(bullet_surface, GREEN, (0, 0, bullet['width'], bullet['height']))
            
            rotated_surface = pygame.transform.rotate(bullet_surface, -math.degrees(angle) + 90)
            
            bullet_rect = rotated_surface.get_rect(center=(bullet['x'] + bullet['width']//2, 
                                                          bullet['y'] + bullet['height']//2))
            
            self.screen.blit(rotated_surface, bullet_rect)
        
        self.draw_special_weapon()
        
        self.draw_special_weapon_indicator()