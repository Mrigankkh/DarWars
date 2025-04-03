import pygame
import json
import math
import random

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PLAYER_SPEED = 5
ENEMY_SIZE = 20
ENEMY_SPEED = 3
WAVE_DURATION = 600  # frames
SAVE_INTERVAL = 10   # must match training SAVE_INTERVAL

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# --- Obstacles ---
# Jail in top left with 2 entry/exits.
jail_walls = []
jail_walls.append(pygame.Rect(20, 20, 150, 10))         # Top wall
jail_walls.append(pygame.Rect(20, 20, 10, 150))         # Left wall
jail_walls.append(pygame.Rect(170, 20, 10, 55))         # Right wall, top segment
jail_walls.append(pygame.Rect(170, 115, 10, 55))        # Right wall, bottom segment
jail_walls.append(pygame.Rect(20, 170, 55, 10))         # Bottom wall, left segment
jail_walls.append(pygame.Rect(115, 170, 55, 10))        # Bottom wall, right segment

other_obstacles = [
    pygame.Rect(300, 200, 200, 20),
    pygame.Rect(100, 400, 150, 20),
    pygame.Rect(500, 300, 20, 150)
]

obstacles = jail_walls + other_obstacles

def is_valid_spawn(rect):
    return not any(rect.colliderect(ob) for ob in obstacles)

def line_of_sight_clear(start, end, obstacles):
    for ob in obstacles:
        if ob.clipline(start, end):
            return False
    return True

class Player:
    def __init__(self):
        self.rect = pygame.Rect(400, 300, 20, 20)
        self.health = 100

    def move(self, keys):
        original_rect = self.rect.copy()
        if keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_s]:
            self.rect.y += PLAYER_SPEED
        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        if any(self.rect.colliderect(ob) for ob in obstacles):
            self.rect = original_rect

    def draw(self):
        pygame.draw.rect(screen, (0, 255, 0), self.rect)

class Enemy:
    def __init__(self, genome, player):
        while True:
            spawn_rect = pygame.Rect(
                random.randint(0, SCREEN_WIDTH - ENEMY_SIZE),
                random.randint(0, SCREEN_HEIGHT - ENEMY_SIZE),
                ENEMY_SIZE, ENEMY_SIZE
            )
            if is_valid_spawn(spawn_rect):
                self.rect = spawn_rect
                break
        self.genome = genome
        self.player = player
        self.cooldown_timer = 0

    def try_move(self, dx, dy):
        future_rect = self.rect.move(dx, dy)
        if any(future_rect.colliderect(ob) for ob in obstacles):
            return False
        self.rect = future_rect
        return True

    def update(self):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            return

        enemy_center = self.rect.center
        player_center = self.player.rect.center
        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 0.1

        base_attraction_x = (dx / distance) * self.genome["aggression"]
        base_attraction_y = (dy / distance) * self.genome["aggression"]

        if not line_of_sight_clear(enemy_center, player_center, obstacles):
            attraction_multiplier = 0.5
            lateral = 0.2
            perp_x = -dy
            perp_y = dx
            perp_mag = math.hypot(perp_x, perp_y)
            if perp_mag != 0:
                perp_x = (perp_x / perp_mag) * lateral
                perp_y = (perp_y / perp_mag) * lateral
            else:
                perp_x, perp_y = 0, 0
            attraction_x = base_attraction_x * attraction_multiplier + perp_x
            attraction_y = base_attraction_y * attraction_multiplier + perp_y
        else:
            attraction_x = base_attraction_x
            attraction_y = base_attraction_y

        repulsion_x = 0
        repulsion_y = 0
        for ob in obstacles:
            ob_center = ob.center
            ex, ey = enemy_center
            ox, oy = ob_center
            dist_to_ob = math.hypot(ex - ox, ey - oy)
            threshold = 50
            if dist_to_ob < threshold and dist_to_ob > 0:
                rep = (threshold - dist_to_ob) / threshold * self.genome["repulsion"]
                repulsion_x += (ex - ox) / dist_to_ob * rep
                repulsion_y += (ey - oy) / dist_to_ob * rep

        force_x = attraction_x + repulsion_x
        force_y = attraction_y + repulsion_y
        magnitude = math.hypot(force_x, force_y)
        if magnitude == 0:
            move_x, move_y = 0, 0
        else:
            move_x = int(force_x / magnitude * ENEMY_SPEED)
            move_y = int(force_y / magnitude * ENEMY_SPEED)

        if not self.try_move(move_x, move_y):
            self.cooldown_timer = 5

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)

def load_generation(gen_num):
    with open(f"gen_{gen_num}.json") as f:
        return json.load(f)

def game():
    player = Player()
    wave = 1
    running = True
    while running:
        try:
            genomes = load_generation(wave * SAVE_INTERVAL)
        except Exception as e:
            print("No more saved generations. Game over!")
            break

        enemies = [Enemy(genome, player) for genome in genomes]
        frame = 0

        while frame < WAVE_DURATION and player.health > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            keys = pygame.key.get_pressed()
            player.move(keys)
            for enemy in enemies:
                enemy.update()
                if enemy.rect.colliderect(player.rect):
                    player.health -= 0.1

            screen.fill((30, 30, 30))
            player.draw()
            for ob in obstacles:
                pygame.draw.rect(screen, (100, 100, 100), ob)
            for enemy in enemies:
                enemy.draw()

            font = pygame.font.SysFont(None, 24)
            info = font.render(f"Wave {wave} | Health: {int(player.health)}", True, (255, 255, 255))
            screen.blit(info, (10, 10))

            pygame.display.flip()
            clock.tick(60)
            frame += 1

        if player.health <= 0:
            print("Player defeated.")
            break

        wave += 1
        pygame.time.wait(1000)

game()
pygame.quit()
