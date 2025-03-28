import pygame

def pause(screen):
    """
    Pause the game and display a "Paused" message until the player resumes.
    :param screen: The game screen to display the pause message.
    :param font: The font to render the pause text.
    """
    font = pygame.font.SysFont("Arial", 24)
    paused = True
    pause_text = font.render("Game Paused. Press any key to resume.", True, (255, 255, 255))
    text_rect = pause_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:  # Resume on any key press
                paused = False

        # Fill the screen with a semi-transparent overlay
        screen.fill((0, 0, 0, 128))
        screen.blit(pause_text, text_rect)
        pygame.display.flip()
        pygame.time.delay(100)  # Add a small delay to reduce CPU usage