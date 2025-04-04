import pygame
from constants import *

def show_info_overlay(screen, player, enemies, font, generation):
    screen.blit(font.render(f"Generation: {generation}", True, WHITE), (10, 10))
    alive = len([e for e in enemies if e.alive])
    screen.blit(font.render(f"Enemies: {alive}/{len(enemies)}", True, WHITE), (10, 40))
    health = f"{player.health}/{player.max_health}"
    h_text = font.render(f"Health: {health}", True, WHITE)
    screen.blit(h_text, (SCREEN_WIDTH - h_text.get_width() - 10, 10))
