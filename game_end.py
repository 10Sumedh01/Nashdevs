import pygame
import sys
import math  # Added standard math library

def game_end(screen):
    """
    Display a game win screen and wait for any key press to exit.
    
    Args:
        screen: The game screen to display the win message.
    """
    # Setup fonts
    title_font = pygame.font.SysFont("Arial", 60)
    message_font = pygame.font.SysFont("Arial", 36)
    
    # Create the win messages
    title_text = title_font.render("CONGRATULATIONS!", True, (255, 215, 0))
    message1 = message_font.render("You've found the antidote and saved humanity!", True, (255, 255, 255))
    message2 = message_font.render("The infection has been cured.", True, (255, 255, 255))
    message3 = message_font.render("Press any key to exit.", True, (200, 200, 200))
    
    # Position the text
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
    msg1_rect = message1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    msg2_rect = message2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
    msg3_rect = message3.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 150))
    
    # Create pulsing effect variables
    start_time = pygame.time.get_ticks()
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                pygame.quit()
                sys.exit()
                
        # Calculate pulsing alpha for the "press any key" message
        elapsed = pygame.time.get_ticks() - start_time
        alpha = int(155 + 100 * abs(math.sin(elapsed / 500)))  # Using math.sin instead of pygame.math.sin
        message3.set_alpha(alpha)
                
        # Draw the victory screen
        # Fill with a gradient background (dark blue to black)
        screen.fill((0, 0, 0))
        for y in range(screen.get_height()):
            alpha = 1.0 - (y / screen.get_height()) * 0.7
            color = (0, int(20 * alpha), int(60 * alpha))
            pygame.draw.line(screen, color, (0, y), (screen.get_width(), y))
            
        # Draw celebratory particles
        current_time = pygame.time.get_ticks()
        for i in range(50):
            x = (current_time // 20 + i * 73) % screen.get_width()
            y = (current_time // 30 + i * 37) % screen.get_height()
            size = 2 + int(3 * abs(math.sin((current_time + i * 100) / 1000)))  # Using math.sin
            
            # Ensure RGB values are within valid range (0-255)
            r = min(255, max(0, int(200 + 55 * math.sin((current_time + i * 100) / 1000))))
            g = min(255, max(0, int(200 + 55 * math.sin((current_time + i * 300) / 1000))))
            b = min(255, max(0, int(100 + 155 * math.sin((current_time + i * 200) / 1000))))
            
            pygame.draw.circle(screen, (r, g, b), (x, y), size)
        
        # Blit the text elements
        screen.blit(title_text, title_rect)
        screen.blit(message1, msg1_rect)
        screen.blit(message2, msg2_rect)
        screen.blit(message3, msg3_rect)
        
        pygame.display.flip()
        pygame.time.delay(10)  # Small delay to reduce CPU usage

if __name__ == "__main__":
    # Test the game_end function if run directly
    pygame.init()
    test_screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Game End Test")
    game_end(test_screen)
    pygame.quit()
    sys.exit()
