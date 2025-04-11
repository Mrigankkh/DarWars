import pygame
import sys
from constants import *
import asyncio
async def show_main_menu(screen, mutation_rate, game_difficulty, font, large_font):
    menu_running = True
    
    menu_options = [
        {"text": "Play Game", "action": "play"},
        {"text": "How to Play", "action": "help"},
        {"text": "Settings", "action": "settings"},
        {"text": "Quit", "action": "quit"}
    ]
    
    selected_option = 0
    
    while menu_running:
        screen.fill(BLACK)
        
        # Title
        title_text = large_font.render("Adaptive Enemy AI - Genetic Algorithm", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Menu options
        y_offset = 250
        for i, option in enumerate(menu_options):
            if i == selected_option:
                text = large_font.render(f"> {option['text']} <", True, GREEN)
            else:
                text = large_font.render(option['text'], True, WHITE)
            
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 60
        
        # Update display
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    action = menu_options[selected_option]["action"]
                    
                    if action == "play":
                        menu_running = False
                    elif action == "help":
                        show_help_screen(screen, font)
                    # elif action == "settings":
                    #     mutation_rate, game_difficulty = show_settings_screen(screen, mutation_rate, game_difficulty, font, large_font)
                    elif action == "quit":
                        pygame.quit()
                        sys.exit()
        
        #clock.tick(30)
        asyncio.sleep(0)
    
    return mutation_rate, game_difficulty

def show_help_screen(screen, font):
    help_running = True
    
    help_text = [
        "How to Play",
        "",
        "Controls:",
        "WASD or Arrow Keys - Move player",
        "SPACE - Shoot (in the direction shown by the yellow line)",
        "F or Q - Use Ring of Fire special weapon (one-time use)",
        "Mouse Click - Select enemy to view its genes",
        "ESC - Pause / Exit",
        "",
        "Game Rules:",
        "- Each generation has a single random shooting direction",
        "- Your shooting angle is shown by the yellow line from the player",
        "- Defeat all enemies to advance to the next generation",
        "- Each generation, enemies evolve based on their performance",
        "- Enemies have different genes that determine their behavior",
        "- Each enemy now has a sequence of up to 20 different behaviors",
        "- Behaviors include: aggressive pursuit, defensive positioning,",
        "  erratic movement, tactical flanking, kamikaze rushing,",
        "  adaptive strategies, directional movement, special shooting patterns,",
        "  dodging, grouping, ambushing, and retreating",
        "- Each behavior has an associated duration that determines",
        "  how long the enemy will perform that action",
        "- Enemies have attributes like speed, accuracy, bullet size,",
        "  and damage that also evolve over generations",
        "- The Ring of Fire special weapon destroys all nearby enemies",
        "",
        "Group Dynamics:",
        "- Enemies can evolve coordinated group behaviors",
        "- They have genes for optimal group size and spacing",
        "- Different enemies can take different roles in formations",
        "- Some prefer to be leaders, others at the edges",
        "- They can synchronize movements and form different patterns",
        "- These behaviors can make them more effective at attacking",
        "- Watch for formations like lines, circles, triangles, and grids",
        "",
        "Bullet Size Strategy:",
        "- Enemies evolve probability distributions for bullet sizes",
        "- Smaller bullets are faster and shoot more frequently",
        "- Larger bullets are slower but do more damage",
        "- Watch for enemies that have evolved optimal distributions",
        "",
        "Press ESC to return to the main menu"
    ]
    
    while help_running:
        screen.fill(BLACK)
        
        # Display help text
        y_offset = 50
        for line in help_text:
            if not line:  # Empty line
                y_offset += 20
                continue
                
            if line.endswith(":"):  # Section header
                text = font.render(line, True, YELLOW)
            else:
                text = font.render(line, True, WHITE)
            
            screen.blit(text, (50, y_offset))
            y_offset += 30
        
        # Update display
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    help_running = False
        
        clock.tick(30)

def show_settings_screen(screen, mutation_rate, game_difficulty, font, large_font):
    settings_running = True
    
    settings = [
        {"name": "Mutation Rate", "value": mutation_rate, "min": 0.0, "max": 1.0, "step": 0.1, "format": "{:.1f}"},
        {"name": "Game Difficulty", "value": game_difficulty, "min": 1, "max": 3, "step": 1, "format": "{:d}"}
    ]
    
    selected_setting = 0
    
    while settings_running:
        screen.fill(BLACK)
        
        # Title
        title_text = large_font.render("Settings", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
        
        # Settings options
        y_offset = 200
        for i, setting in enumerate(settings):
            # Format setting name and value
            setting_text = f"{setting['name']}: {setting['format'].format(setting['value'])}"
            
            # Highlight selected setting
            if i == selected_setting:
                text = font.render(f"> {setting_text} <", True, GREEN)
            else:
                text = font.render(setting_text, True, WHITE)
            
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 50
        
        # Instructions
        instructions_text = font.render("Use LEFT/RIGHT to adjust values, UP/DOWN to navigate, ESC to return", True, WHITE)
        screen.blit(instructions_text, (SCREEN_WIDTH // 2 - instructions_text.get_width() // 2, SCREEN_HEIGHT - 100))
        
        # Update display
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_setting = (selected_setting - 1) % len(settings)
                elif event.key == pygame.K_DOWN:
                    selected_setting = (selected_setting + 1) % len(settings)
                elif event.key == pygame.K_LEFT:
                    # Decrease value
                    setting = settings[selected_setting]
                    setting["value"] = max(setting["min"], setting["value"] - setting["step"])
                elif event.key == pygame.K_RIGHT:
                    # Increase value
                    setting = settings[selected_setting]
                    setting["value"] = min(setting["max"], setting["value"] + setting["step"])
                elif event.key == pygame.K_ESCAPE:
                    settings_running = False
        
        clock.tick(30)
    
    # Return updated settings
    mutation_rate = settings[0]["value"]
    game_difficulty = int(settings[1]["value"])
    
    return mutation_rate, game_difficulty