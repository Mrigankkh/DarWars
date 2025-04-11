# import pygame
# import random
# import math
# from constants import *
# from player import Player
# from enemy import ( Enemy)
# from genetic_algorithm import evolve_population
# from ui import (show_generation_summary, show_game_over, show_info_overlay, show_enemy_info)
# from menu import show_main_menu, show_help_screen, show_settings_screen
# #
# # from visibility.visibility_logger import log_generation
# # Initialize pygame
# pygame.init()

# # Screen settings
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("Adaptive Enemy AI - Genetic Algorithm")

# # Font settings
# font = pygame.font.SysFont('Arial', 16)
# large_font = pygame.font.SysFont('Arial', 20)

# # Global game variables
# generation = 1
# population_size = 10
# current_enemies = 0
# enemies_defeated = 0
# mutation_rate = 0.1
# game_difficulty = 1

# def reset_game():
#     global generation, enemies_defeated, current_enemies
#     generation = 1
#     enemies_defeated = 0
#     current_enemies = 0
#     player = Player(screen)
#     enemies = [Enemy(screen) for _ in range(population_size)]
#     return player, enemies

# def main():
#     global generation, enemies_defeated, current_enemies, mutation_rate, game_difficulty
    
#     running = True
#     game_state = "playing"
    
  
#     player = Player(screen)
#     enemies = [Enemy(screen) for _ in range(population_size)]
#     current_enemies = len(enemies)
    
#     selected_enemy = None
    
#     special_message = ""
#     special_message_time = 0
    
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             elif event.type == pygame.MOUSEBUTTONDOWN:
#                 mouse_pos = pygame.mouse.get_pos()
#                 for enemy in enemies:
#                     if (enemy.alive and
#                         mouse_pos[0] >= enemy.x and mouse_pos[0] <= enemy.x + enemy.width and
#                         mouse_pos[1] >= enemy.y and mouse_pos[1] <= enemy.y + enemy.height):
#                         selected_enemy = enemy
#                         break
#                 else:
#                     selected_enemy = None
#             elif event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_ESCAPE:
#                     running = False
#                 elif event.key == pygame.K_m:
#                     # Increase mutation rate
#                     mutation_rate = min(1.0, mutation_rate + 0.1)
#                 elif event.key == pygame.K_n:
#                     # Decrease mutation rate
#                     mutation_rate = max(0.0, mutation_rate - 0.1)
#                 elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
#                     # Increase difficulty
#                     game_difficulty = min(3, game_difficulty + 1)
#                 elif event.key == pygame.K_MINUS:
#                     # Decrease difficulty
#                     game_difficulty = max(1, game_difficulty - 1)
        
#         if game_state == "playing":
#             # Clear screen
#             screen.fill(BLACK)
            
#             # Get keyboard state
#             keys = pygame.key.get_pressed()
            
#             # Update player
#             player.move(keys)
#             player.shoot(keys)
#             player.update_bullets(enemies)
            
#             # Check for special weapon activation
#             if (keys[pygame.K_f] or keys[pygame.K_q]) and player.has_special_weapon:
#                 enemies_destroyed = player.use_special_weapon(enemies)
#                 if enemies_destroyed > 0:
#                     # Display message about enemies destroyed
#                     special_message = f"Ring of Fire destroyed {enemies_destroyed} enemies!"
#                     special_message_time = 120  # Display for 2 seconds
            
#             # Update special weapon animation
#             player.update_special_weapon()
            
#             player.draw()
            
#             # Update enemies
#             alive_enemies = [enemy for enemy in enemies if enemy.alive]
#             for enemy in alive_enemies:
#                 enemy.time_alive += 1
#                 enemy.move(player, alive_enemies)  # Pass all enemies for group behavior
#                 enemy.shoot(player)
#                 enemy.update_bullets(player)
#                 enemy.draw()
            
#             # Draw selected enemy info
#             if selected_enemy and selected_enemy.alive:
#                 mouse_pos = pygame.mouse.get_pos()
#                 show_enemy_info(screen, selected_enemy, mouse_pos, font)
            
#             # Show game info
#             show_info_overlay(screen, player, enemies, font, generation)
            
#             # Show special weapon message if active
#             if special_message_time > 0:
#                 message_text = font.render(special_message, True, YELLOW)
#                 screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, 100))
#                 special_message_time -= 1
            
#             # Check game state
#             if not player.alive:
#                 game_state = "game_over"
            
#             # Check if all enemies defeated
#             if not alive_enemies:
#                 # Calculate fitness for all enemies
#                 for enemy in enemies:
#                     enemy.calculate_fitness()
                
#                 # Move to next generation
#                 if show_generation_summary(screen, enemies, font, large_font, generation, enemies_defeated, mutation_rate, game_difficulty):
#                     # Evolve population
#                     enemies = evolve_population(enemies, population_size, mutation_rate)
                    
#                     generation += 1
#                     enemies_defeated += current_enemies
#                     current_enemies = len(enemies)
#                     #log_generation(enemies, generation)

#                     # Reset player position and health
#                     player = Player(screen)
            
#             # Update display
#             pygame.display.flip()
#             clock.tick(FPS)
        
#         elif game_state == "game_over":
#             # Show game over screen
#             if show_game_over(screen, False, font, large_font, generation, enemies_defeated):
#                 # Reset game
#                 game_state = "playing"
#                 player = Player(screen)
#                 # Assign a new random shooting direction
#                 player.shooting_angle = random.uniform(0, 2 * math.pi)
#                 enemies = [Enemy(screen) for _ in range(population_size)]
#                 generation = 1
#                 enemies_defeated = 0
#                 current_enemies = len(enemies)
    
#     pygame.quit()

# # Start the game
# if __name__ == "__main__":
#     show_main_menu(screen, mutation_rate, game_difficulty, font, large_font)
#     main()
import pygame
import random
import math
import asyncio

from constants import *
from player import Player
from enemy import Enemy
from genetic_algorithm import evolve_population
from ui import (
    show_generation_summary,
    show_game_over,
    show_info_overlay,
    show_enemy_info
)
from menu import show_main_menu, show_help_screen, show_settings_screen

# Initialize pygame and set up the screen.
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Adaptive Enemy AI - Genetic Algorithm")

# Set up fonts.
font = pygame.font.SysFont('Arial', 16)
large_font = pygame.font.SysFont('Arial', 20)

# Global game variables.
generation = 1
population_size = 10
current_enemies = 0
enemies_defeated = 0
mutation_rate = 0.1
game_difficulty = 1

def reset_game():
    global generation, enemies_defeated, current_enemies
    generation = 1
    enemies_defeated = 0
    current_enemies = 0
    player = Player(screen)
    enemies = [Enemy(screen) for _ in range(population_size)]
    return player, enemies

async def main():
    global generation, enemies_defeated, current_enemies, mutation_rate, game_difficulty
    mutation_rate, game_difficulty   = await show_main_menu(screen, mutation_rate, game_difficulty, font, large_font)

    running = True
    game_state = "playing"

    clock = pygame.time.Clock()

    # Initialize player and enemies.
    player = Player(screen)
    enemies = [Enemy(screen) for _ in range(population_size)]
    current_enemies = len(enemies)

    selected_enemy = None
    special_message = ""
    special_message_time = 0

    # Main game loop.
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for enemy in enemies:
                    if (enemy.alive and
                        enemy.x <= mouse_pos[0] <= enemy.x + enemy.width and
                        enemy.y <= mouse_pos[1] <= enemy.y + enemy.height):
                        selected_enemy = enemy
                        break
                else:
                    selected_enemy = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    mutation_rate = min(1.0, mutation_rate + 0.1)
                elif event.key == pygame.K_n:
                    mutation_rate = max(0.0, mutation_rate - 0.1)
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    game_difficulty = min(3, game_difficulty + 1)
                elif event.key == pygame.K_MINUS:
                    game_difficulty = max(1, game_difficulty - 1)

        if game_state == "playing":
            # Clear the screen.
            screen.fill(BLACK)

            # Process keyboard input.
            keys = pygame.key.get_pressed()

            # Update player actions.
            player.move(keys)
            player.shoot(keys)
            player.update_bullets(enemies)

            if (keys[pygame.K_f] or keys[pygame.K_q]) and player.has_special_weapon:
                enemies_destroyed = player.use_special_weapon(enemies)
                if enemies_destroyed > 0:
                    special_message = f"Ring of Fire destroyed {enemies_destroyed} enemies!"
                    special_message_time = 120

            player.update_special_weapon()
            player.draw()

            # Update enemies.
            alive_enemies = [enemy for enemy in enemies if enemy.alive]
            for enemy in alive_enemies:
                enemy.time_alive += 1
                enemy.move(player, alive_enemies)
                enemy.shoot(player)
                enemy.update_bullets(player)
                enemy.draw()

            # If an enemy was selected, draw its info.
            if selected_enemy and selected_enemy.alive:
                mouse_pos = pygame.mouse.get_pos()
                await show_enemy_info(screen, selected_enemy, mouse_pos, font)

            # Overlay game info.
            await show_info_overlay(screen, player, enemies, font, generation)

            # Show a special weapon message if active.
            if special_message_time > 0:
                message_text = font.render(special_message, True, YELLOW)
                screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, 100))
                special_message_time -= 1

            # Update game state.
            if not player.alive:
                game_state = "game_over"

            if not alive_enemies:
                for enemy in enemies:
                    try:
                        enemy.calculate_fitness()
                    except Exception as e:
                        print("fitness crash:", e)
                 
                if await show_generation_summary(screen, enemies, font, large_font, generation, enemies_defeated, mutation_rate, game_difficulty):
                    enemies = evolve_population(enemies, population_size, mutation_rate)
                    generation += 1
                    enemies_defeated += current_enemies
                    current_enemies = len(enemies)
                    player = Player(screen)

            # Update the display.
            pygame.display.flip()
            # Yield control to allow the browser to process events.
            await asyncio.sleep(0)
            # Frame rate control.
            clock.tick(FPS)

        elif game_state == "game_over":
            if await show_game_over(screen, False, font, large_font, generation, enemies_defeated):
                game_state = "playing"
                player = Player(screen)
                player.shooting_angle = random.uniform(0, 2 * math.pi)
                enemies = [Enemy(screen) for _ in range(population_size)]
                generation = 1
                enemies_defeated = 0
                current_enemies = len(enemies)

    pygame.quit()

if __name__ == "__main__":
    # Show the main menu, then run the async game loop.
    asyncio.run(main())
