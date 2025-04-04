import pygame
from constants import *
from behavior_gene import BehaviorGene
from ui.utils.gene_utils import get_dominant_traits
from ui.utils.stat_utils import (
    calculate_behavior_stats,
    calculate_bullet_distribution,
    calculate_group_dynamics,
)

def show_generation_summary(screen, population, font, large_font, generation, enemies_defeated, mutation_rate, game_difficulty):
    screen.fill(BLACK)
    
    title = large_font.render(f"Generation {generation} Summary", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

    sorted_population = sorted(population, key=lambda x: x.chromosome[59], reverse=True)
    
    y_offset = 120
    header = font.render("Top Performers (Fitness, Dominant Traits)", True, WHITE)
    screen.blit(header, (SCREEN_WIDTH // 2 - header.get_width() // 2, y_offset))
    y_offset += 40

    for i, enemy in enumerate(sorted_population[:5]):
        traits = get_dominant_traits(enemy.chromosome)
        traits_str = ", ".join(traits)
        color_factor = 1 - (i / 5)
        text_color = (int(255 * (1 - color_factor)), 255, 0)

        fit_text = font.render(f"{i+1}. Fitness: {enemy.chromosome[59]:.1f}", True, text_color)
        screen.blit(fit_text, (SCREEN_WIDTH // 2 - 300, y_offset))

        if len(traits_str) > 40:
            text1 = font.render(f"Traits: {traits_str[:40]}", True, text_color)
            text2 = font.render(f"       {traits_str[40:]}", True, text_color)
            screen.blit(text1, (SCREEN_WIDTH // 2 - 150, y_offset))
            screen.blit(text2, (SCREEN_WIDTH // 2 - 150, y_offset + 20))
            y_offset += 45
        else:
            text = font.render(f"Traits: {traits_str}", True, text_color)
            screen.blit(text, (SCREEN_WIDTH // 2 - 150, y_offset))
            y_offset += 25

    y_offset += 20
    behavior_counts = calculate_behavior_stats(population)
    sorted_behaviors = sorted(behavior_counts.items(), key=lambda x: x[1], reverse=True)
    
    behavior_header = font.render("Most Common Behaviors", True, YELLOW)
    screen.blit(behavior_header, (SCREEN_WIDTH // 2 - behavior_header.get_width() // 2, y_offset))
    y_offset += 25

    for behavior, count in sorted_behaviors[:5]:
        pct = (count / len(population)) * 100
        b_text = font.render(f"{behavior}: {pct:.1f}%", True, WHITE)
        screen.blit(b_text, (SCREEN_WIDTH // 2 - b_text.get_width() // 2, y_offset))
        y_offset += 20

    y_offset += 20
    bullet_header = font.render("Bullet Size Distribution", True, YELLOW)
    screen.blit(bullet_header, (SCREEN_WIDTH // 2 - bullet_header.get_width() // 2, y_offset))
    y_offset += 25

    size_names = ["Very Small", "Small", "Medium", "Large", "Very Large"]
    dist = calculate_bullet_distribution(population)
    for name, pct in zip(size_names, dist):
        bar_width = int(200 * pct)
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH // 2 - 100, y_offset, bar_width, 15))
        text = font.render(f"{name}: {pct*100:.1f}%", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - 200, y_offset))
        y_offset += 20

    y_offset += 20
    group_header = font.render("Group Dynamics", True, YELLOW)
    screen.blit(group_header, (SCREEN_WIDTH // 2 - group_header.get_width() // 2, y_offset))
    y_offset += 25

    avg_size, avg_prox, role_counts, pattern_counts = calculate_group_dynamics(population)
    
    text1 = font.render(f"Avg Group Size Preference: {avg_size:.1f} enemies", True, WHITE)
    screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, y_offset))
    y_offset += 20

    text2 = font.render(f"Avg Optimal Proximity: {avg_prox:.1f} pixels", True, WHITE)
    screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, y_offset))
    y_offset += 20

    roles = ["Edge", "Middle", "Leader"]
    role_text = font.render("Formation Roles:", True, WHITE)
    screen.blit(role_text, (SCREEN_WIDTH // 2 - 200, y_offset))
    for i, (role, count) in enumerate(zip(roles, role_counts)):
        pct = (count / len(population)) * 100
        role_t = font.render(f"{role}: {pct:.1f}%", True, WHITE)
        screen.blit(role_t, (SCREEN_WIDTH // 2 - 50 + i * 120, y_offset))
    y_offset += 20

    pattern_names = ["Line", "Circle", "Triangle", "Grid"]
    pattern_text = font.render("Formation Patterns:", True, WHITE)
    screen.blit(pattern_text, (SCREEN_WIDTH // 2 - 200, y_offset))
    for i, (name, count) in enumerate(zip(pattern_names, pattern_counts)):
        pct = (count / len(population)) * 100
        p_text = font.render(f"{name}: {pct:.1f}%", True, WHITE)
        screen.blit(p_text, (SCREEN_WIDTH // 2 - 50 + (i % 2) * 120, y_offset + (i // 2) * 20))
    y_offset += 40

    final_stats = font.render(f"Enemies Defeated: {enemies_defeated} | Mutation Rate: {mutation_rate:.1f} | Difficulty: {game_difficulty}", True, WHITE)
    screen.blit(final_stats, (SCREEN_WIDTH // 2 - final_stats.get_width() // 2, y_offset))

    continue_text = font.render("Press SPACE to continue", True, WHITE)
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 100))

    pygame.display.flip()

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
                    return False
    return True
