import pygame
from constants import *

def show_game_over(screen, victory, font, large_font, generation, enemies_defeated):
    screen.fill(BLACK)
    title = "VICTORY!" if victory else "GAME OVER"
    color = GREEN if victory else RED
    text = large_font.render(title, True, color)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 3))

    stats = font.render(f"Generations Survived: {generation} | Enemies Defeated: {enemies_defeated}", True, WHITE)
    screen.blit(stats, (SCREEN_WIDTH // 2 - stats.get_width() // 2, SCREEN_HEIGHT // 2))

    restart = font.render("Press R to restart or ESC to quit", True, WHITE)
    screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
