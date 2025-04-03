def show_generation_summary(screen, population, font, large_font, generation, enemies_defeated, mutation_rate, game_difficulty):
    screen.fill(BLACK)
    
    title_text = large_font.render(f"Generation {generation} Summary", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Sort population by fitness
    sorted_population = sorted(population, key=lambda x: x.chromosome[54], reverse=True)
    
    # Display top 5 enemies
    y_offset = 120
    header = font.render("Top Performers (Fitness, Dominant Traits)", True, WHITE)
    screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, y_offset))
    y_offset += 40
    
    for i, enemy in enumerate(sorted_population[:5]):
        # Determine dominant traits
        traits = []
        for j, gene_value in enumerate(enemy.chromosome[:20]):
            if gene_value == 1:
                traits.append(BehaviorGene(j).name)
        
        # Keep only up to 5 traits to avoid overflow
        if len(traits) > 5:
            traits = traits[:4] + ["..."]
        
        if not traits:
            traits = ["NONE"]
        
        traits_str = ", ".join(traits)
        
        # Color gradient from green (best) to yellow (5th best)
        color_factor = 1 - (i / 5)
        text_color = (int(255 * (1 - color_factor)), 255, 0)
        
        # Split display into multiple lines if needed
        text = font.render(f"{i+1}. Fitness: {enemy.chromosome[54]:.1f}", True, text_color)
        screen.blit(text, (SCREEN_WIDTH // 2 - 300, y_offset))
        
        # Render traits with text wrapping
        if len(traits_str) > 40:
            traits_1 = traits_str[:40]
            traits_2 = traits_str[40:]
            text1 = font.render(f"Traits: {traits_1}", True, text_color)
            text2 = font.render(f"       {traits_2}", True, text_color)
            screen.blit(text1, (SCREEN_WIDTH // 2 - 150, y_offset))
            screen.blit(text2, (SCREEN_WIDTH // 2 - 150, y_offset + 20))
            y_offset += 45
        else:
            text = font.render(f"Traits: {traits_str}", True, text_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - 150, y_offset))
            y_offset += 25
    
    # Display behavior statistics
    y_offset += 20
    behavior_stats = {}
    for j in range(20):
        behavior_stats[BehaviorGene(j).name] = sum(1 for enemy in population if enemy.chromosome[j] == 1)
    
    # Sort behaviors by frequency
    sorted_behaviors = sorted(behavior_stats.items(), key=lambda x: x[1], reverse=True)
    
    stats_header = font.render("Most Common Behaviors", True, YELLOW)
    screen.blit(stats_header, (SCREEN_WIDTH // 2 - stats_header.get_width() // 2, y_offset))
    y_offset += 25
    
    # Display top 5 most common behaviors
    for i, (behavior, count) in enumerate(sorted_behaviors[:5]):
        percentage = (count / len(population)) * 100
        behavior_text = font.render(f"{behavior}: {percentage:.1f}% of population", True, WHITE)
        screen.blit(behavior_text, (SCREEN_WIDTH // 2 - behavior_text.get_width() // 2, y_offset))
        y_offset += 20
    
    # Display bullet size distribution statistics
    y_offset += 20
    bullet_stats_header = font.render("Bullet Size Distribution", True, YELLOW)
    screen.blit(bullet_stats_header, (SCREEN_WIDTH // 2 - bullet_stats_header.get_width() // 2, y_offset))
    y_offset += 25
    
    # Calculate average distribution across population
    size_names = ["Very Small", "Small", "Medium", "Large", "Very Large"]
    avg_distribution = [0, 0, 0, 0, 0]
    
    for enemy in population:
        weights = enemy.chromosome[47:52]
        total = sum(weights)
        if total > 0:  # Avoid division by zero
            normalized = [w / total for w in weights]
            for i in range(5):
                avg_distribution[i] += normalized[i]
    
    # Normalize to get average percentage
    for i in range(5):
        avg_distribution[i] /= len(population)
        
    # Display average distribution
    for i, (name, pct) in enumerate(zip(size_names, avg_distribution)):
        bar_width = int(200 * pct)
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH // 2 - 100, y_offset, bar_width, 15))
        
        pct_text = font.render(f"{name}: {pct*100:.1f}%", True, WHITE)
        screen.blit(pct_text, (SCREEN_WIDTH // 2 - 200, y_offset))
        y_offset += 20
    
    # Display game statistics
    y_offset += 20
    stats_text = font.render(f"Enemies Defeated: {enemies_defeated} | Mutation Rate: {mutation_rate:.1f} | Difficulty: {game_difficulty}", True, WHITE)
    screen.blit(stats_text, (SCREEN_WIDTH // 2 - stats_text.get_width() // 2, y_offset))
    
    # Continue button
    continue_y = SCREEN_HEIGHT - 100
    continue_text = font.render("Press SPACE to continue to next generation", True, WHITE)
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, continue_y))
    
    pygame.display.flip()
    
    # Wait for space key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    return False  # Exit game
        
        clock.tick(30)
    
    return True  # Continue gameimport pygame
import sys
from constants import *
from behavior_gene import BehaviorGene

def show_enemy_info(screen, enemy, mouse_pos, font):
    # Draw info box at mouse position
    box_width, box_height = 350, 280
    box_x = min(mouse_pos[0], SCREEN_WIDTH - box_width)
    box_y = min(mouse_pos[1], SCREEN_HEIGHT - box_height)
    
    # Background
    pygame.draw.rect(screen, BLACK, (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 2)
    
    # Title
    title_text = font.render("Enemy DNA", True, WHITE)
    screen.blit(title_text, (box_x + 10, box_y + 10))
    
    # Current behavior
    current_behavior = enemy.get_current_behavior()
    behavior_name = BehaviorGene(current_behavior['behavior']).name
    
    current_text = font.render(f"Current: {behavior_name} ({enemy.behavior_timer}/{current_behavior['duration']})", True, YELLOW)
    screen.blit(current_text, (box_x + 10, box_y + 40))
    
    # Behavior genes (show 10 per column)
    y_offset = box_y + 70
    
    # First column: Behavior genes 0-9
    for i in range(10):
        gene_name = BehaviorGene(i).name
        gene_value = "ON" if enemy.chromosome[i] == 1 else "OFF"
        gene_color = GREEN if enemy.chromosome[i] == 1 else RED
        gene_text = font.render(f"{gene_name[:8]}: {gene_value}", True, gene_color)
        screen.blit(gene_text, (box_x + 10, y_offset))
        y_offset += 16
    
    # Second column: Behavior genes 10-19
    y_offset = box_y + 70
    for i in range(10, 20):
        gene_name = BehaviorGene(i).name
        gene_value = "ON" if enemy.chromosome[i] == 1 else "OFF"
        gene_color = GREEN if enemy.chromosome[i] == 1 else RED
        gene_text = font.render(f"{gene_name[:8]}: {gene_value}", True, gene_color)
        screen.blit(gene_text, (box_x + 180, y_offset))
        y_offset += 16
    
    # Attribute genes
    y_offset += 10
    stat_text = font.render(f"SPD: {enemy.chromosome[40]:.1f} | FR: {enemy.chromosome[41]:.1f}", True, WHITE)
    screen.blit(stat_text, (box_x + 10, y_offset))
    y_offset += 16
    
    acc_text = font.render(f"ACC: {enemy.chromosome[42]:.1f} | EVA: {enemy.chromosome[43]:.1f}", True, WHITE)
    screen.blit(acc_text, (box_x + 10, y_offset))
    y_offset += 16
    
    other_text = font.render(f"DMG: {enemy.chromosome[46]:.1f}", True, WHITE)
    screen.blit(other_text, (box_x + 10, y_offset))
    y_offset += 20
    
    # Bullet size probability distribution
    bullet_weights = enemy.chromosome[47:52]
    total_weight = sum(bullet_weights)
    if total_weight > 0:
        normalized_weights = [w / total_weight for w in bullet_weights]
    else:
        normalized_weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    
    bullet_text = font.render("Bullet Size Probabilities:", True, YELLOW)
    screen.blit(bullet_text, (box_x + 10, y_offset))
    y_offset += 20
    
    size_names = ["V.Small", "Small", "Medium", "Large", "V.Large"]
    for i, (name, weight) in enumerate(zip(size_names, normalized_weights)):
        # Create a bar graph showing probability
        bar_width = int(150 * weight)
        pygame.draw.rect(screen, BLUE, (box_x + 80, y_offset + i*16, bar_width, 12))
        
        # Display name and percentage
        size_text = font.render(f"{name}: {weight*100:.1f}%", True, WHITE)
        screen.blit(size_text, (box_x + 10, y_offset + i*16))

def show_info_overlay(screen, player, enemies, font, generation):
    # Display generation and enemy count
    gen_text = font.render(f"Generation: {generation}", True, WHITE)
    screen.blit(gen_text, (10, 10))
    
    enemy_text = font.render(f"Enemies: {len([e for e in enemies if e.alive])}/{len(enemies)}", True, WHITE)
    screen.blit(enemy_text, (10, 40))
    
    # Display player health
    health_text = font.render(f"Health: {player.health}/{player.max_health}", True, WHITE)
    screen.blit(health_text, (SCREEN_WIDTH - health_text.get_width() - 10, 10))

def show_generation_summary(screen, population, font, large_font, generation, enemies_defeated, mutation_rate, game_difficulty):
    screen.fill(BLACK)
    
    title_text = large_font.render(f"Generation {generation} Summary", True, WHITE)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
    
    # Sort population by fitness
    sorted_population = sorted(population, key=lambda x: x.chromosome[50], reverse=True)
    
    # Display top 5 enemies
    y_offset = 120
    header = font.render("Top Performers (Fitness, Dominant Traits)", True, WHITE)
    screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, y_offset))
    y_offset += 40
    
    for i, enemy in enumerate(sorted_population[:5]):
        # Determine dominant traits
        traits = []
        for j, gene_value in enumerate(enemy.chromosome[:20]):
            if gene_value == 1:
                traits.append(BehaviorGene(j).name)
        
        # Keep only up to 5 traits to avoid overflow
        if len(traits) > 5:
            traits = traits[:4] + ["..."]
        
        if not traits:
            traits = ["NONE"]
        
        traits_str = ", ".join(traits)
        
        # Color gradient from green (best) to yellow (5th best)
        color_factor = 1 - (i / 5)
        text_color = (int(255 * (1 - color_factor)), 255, 0)
        
        # Split display into multiple lines if needed
        text = font.render(f"{i+1}. Fitness: {enemy.chromosome[50]:.1f}", True, text_color)
        screen.blit(text, (SCREEN_WIDTH // 2 - 300, y_offset))
        
        # Render traits with text wrapping
        if len(traits_str) > 40:
            traits_1 = traits_str[:40]
            traits_2 = traits_str[40:]
            text1 = font.render(f"Traits: {traits_1}", True, text_color)
            text2 = font.render(f"       {traits_2}", True, text_color)
            screen.blit(text1, (SCREEN_WIDTH // 2 - 150, y_offset))
            screen.blit(text2, (SCREEN_WIDTH // 2 - 150, y_offset + 20))
            y_offset += 45
        else:
            text = font.render(f"Traits: {traits_str}", True, text_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - 150, y_offset))
            y_offset += 25
    
    # Display behavior statistics
    y_offset += 20
    behavior_stats = {}
    for j in range(20):
        behavior_stats[BehaviorGene(j).name] = sum(1 for enemy in population if enemy.chromosome[j] == 1)
    
    # Sort behaviors by frequency
    sorted_behaviors = sorted(behavior_stats.items(), key=lambda x: x[1], reverse=True)
    
    stats_header = font.render("Most Common Behaviors", True, YELLOW)
    screen.blit(stats_header, (SCREEN_WIDTH // 2 - stats_header.get_width() // 2, y_offset))
    y_offset += 25
    
    # Display top 5 most common behaviors
    for i, (behavior, count) in enumerate(sorted_behaviors[:5]):
        percentage = (count / len(population)) * 100
        behavior_text = font.render(f"{behavior}: {percentage:.1f}% of population", True, WHITE)
        screen.blit(behavior_text, (SCREEN_WIDTH // 2 - behavior_text.get_width() // 2, y_offset))
        y_offset += 20
    
    # Display game statistics
    y_offset += 20
    stats_text = font.render(f"Enemies Defeated: {enemies_defeated} | Mutation Rate: {mutation_rate:.1f} | Difficulty: {game_difficulty}", True, WHITE)
    screen.blit(stats_text, (SCREEN_WIDTH // 2 - stats_text.get_width() // 2, y_offset))
    
    # Continue button
    continue_y = SCREEN_HEIGHT - 100
    continue_text = font.render("Press SPACE to continue to next generation", True, WHITE)
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, continue_y))
    
    pygame.display.flip()
    
    # Wait for space key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    return False  # Exit game
        
        clock.tick(30)
    
    return True  # Continue game

def show_game_over(screen, victory, font, large_font, generation, enemies_defeated):
    screen.fill(BLACK)
    
    if victory:
        title_text = large_font.render("VICTORY!", True, GREEN)
    else:
        title_text = large_font.render("GAME OVER", True, RED)
    
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
    
    stats_text = font.render(f"Generations Survived: {generation} | Enemies Defeated: {enemies_defeated}", True, WHITE)
    screen.blit(stats_text, (SCREEN_WIDTH // 2 - stats_text.get_width() // 2, SCREEN_HEIGHT // 2))
    
    restart_text = font.render("Press R to restart or ESC to quit", True, WHITE)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    
    pygame.display.flip()
    
    # Wait for key
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Restart game
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        clock.tick(30)