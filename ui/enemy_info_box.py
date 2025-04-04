import pygame
from constants import *
from behavior_gene import BehaviorGene
from ui.utils.gene_utils import get_role_name, get_pattern_name

def show_enemy_info(screen, enemy, mouse_pos, font):
    box_w, box_h = 350, 350
    x, y = min(mouse_pos[0], SCREEN_WIDTH - box_w), min(mouse_pos[1], SCREEN_HEIGHT - box_h)
    
    pygame.draw.rect(screen, BLACK, (x, y, box_w, box_h))
    pygame.draw.rect(screen, WHITE, (x, y, box_w, box_h), 2)

    screen.blit(font.render("Enemy DNA", True, WHITE), (x + 10, y + 10))

    behavior = enemy.get_current_behavior()
    name = BehaviorGene(behavior['behavior']).name
    behavior_text = font.render(f"Current: {name} ({enemy.behavior_timer}/{behavior['duration']})", True, YELLOW)
    screen.blit(behavior_text, (x + 10, y + 40))

    for i in range(10):
        g_name = BehaviorGene(i).name
        val = enemy.chromosome[i]
        color = GREEN if val else RED
        text = font.render(f"{g_name[:8]}: {'ON' if val else 'OFF'}", True, color)
        screen.blit(text, (x + 10, y + 70 + i * 16))

    for i in range(10, 20):
        g_name = BehaviorGene(i).name
        val = enemy.chromosome[i]
        color = GREEN if val else RED
        text = font.render(f"{g_name[:8]}: {'ON' if val else 'OFF'}", True, color)
        screen.blit(text, (x + 180, y + 70 + (i - 10) * 16))

    y_off = y + 240
    screen.blit(font.render(f"SPD: {enemy.chromosome[40]:.1f} | FR: {enemy.chromosome[41]:.1f}", True, WHITE), (x + 10, y_off))
    y_off += 16
    screen.blit(font.render(f"ACC: {enemy.chromosome[42]:.1f} | EVA: {enemy.chromosome[43]:.1f}", True, WHITE), (x + 10, y_off))
    y_off += 16
    screen.blit(font.render(f"DMG: {enemy.chromosome[46]:.1f}", True, WHITE), (x + 10, y_off))
