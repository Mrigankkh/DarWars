import pygame
import sys
from constants import *
from behavior_gene import BehaviorGene
from ui.utils.gene_utils import get_dominant_traits
from ui.utils.stat_utils import (
    calculate_behavior_stats,
    calculate_bullet_distribution,
    calculate_group_dynamics,
)
def show_generation_summary(screen, population, font, small_font, generation, enemies_defeated, mutation_rate, game_difficulty):
    screen.fill(BLACK)

    sorted_population = sorted(population, key=lambda x: x.chromosome[59], reverse=True)
    top_enemies = sorted_population[:5]

    title = font.render(f"Gen {generation} Summary", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

    y = 70

    # === Top performers ===
    for i, enemy in enumerate(top_enemies):
        traits = get_dominant_traits(enemy.chromosome)
        trait_str = ", ".join(traits)
        trait_text = small_font.render(f"{i+1}. Fit: {enemy.chromosome[59]:.0f} | {trait_str}", True, WHITE)
        screen.blit(trait_text, (60, y))
        y += 20

    y += 10
    screen.blit(font.render("Common Behaviors:", True, YELLOW), (60, y))
    y += 20
    for behavior, count in sorted(calculate_behavior_stats(population).items(), key=lambda x: x[1], reverse=True)[:3]:
        pct = (count / len(population)) * 100
        b_text = small_font.render(f"{behavior}: {pct:.1f}%", True, WHITE)
        screen.blit(b_text, (80, y))
        y += 15

    y += 10
    screen.blit(font.render("Bullet Sizes:", True, YELLOW), (60, y))
    y += 20
    for name, pct in list(zip(["Tiny", "Small", "Medium", "Large", "XL"], calculate_bullet_distribution(population)))[:5]:
        b = small_font.render(f"{name}: {pct*100:.1f}%", True, WHITE)
        screen.blit(b, (80, y))
        y += 15

    y += 10
    screen.blit(font.render("Group Dynamics:", True, YELLOW), (60, y))
    y += 20

    avg_size, avg_prox, role_counts, pattern_counts = calculate_group_dynamics(population)
    g1 = small_font.render(f"Avg Size Pref: {avg_size:.1f} | Prox: {avg_prox:.0f}", True, WHITE)
    screen.blit(g1, (80, y))
    y += 15

    roles = ["Edge", "Middle", "Leader"]
    role_str = ", ".join(f"{r}: {role_counts[i]}" for i, r in enumerate(roles))
    screen.blit(small_font.render(role_str, True, WHITE), (80, y))
    y += 15

    patterns = ["Line", "Circle", "Tri", "Grid"]
    pattern_str = ", ".join(f"{p}: {pattern_counts[i]}" for i, p in enumerate(patterns[:3]))
    screen.blit(small_font.render(f"Patterns: {pattern_str}", True, WHITE), (80, y))
    y += 20

    # Footer
    summary = small_font.render(
        f"Defeated: {enemies_defeated} | Mutation: {mutation_rate:.2f} | Difficulty: {game_difficulty}", True, GRAY
    )
    screen.blit(summary, (SCREEN_WIDTH // 2 - summary.get_width() // 2, SCREEN_HEIGHT - 50))

    continue_text = small_font.render("Press SPACE to continue", True, WHITE)
    screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - 30))

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
                    return True  # Indicate that the user pressed SPACE to continue
