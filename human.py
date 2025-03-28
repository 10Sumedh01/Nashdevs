import pygame
import math
from constants import ZOMBIE_SIZE

class Human:
    def __init__(self, pos, speed_multiplier=1.0):
        self.pos = pygame.Vector2(pos)
        self.size = ZOMBIE_SIZE*0.5
        self.speed = 100 * speed_multiplier
        self.max_health = 500
        self.health = self.max_health
        self.is_special = False
        
        # Load human sprite (you'll need to create this asset)
        try:
            self.sprite = pygame.image.load('assets/knifeplayer.png').convert_alpha()
        except:
            # Fallback if sprite not found
            self.sprite = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite, (255, 0, 0), (self.size, self.size), self.size)
        
        self.sprite = pygame.transform.scale(self.sprite, (self.size*2, self.size*2))

    def update(self, player_pos, collision_rects, map_manager):
        # Simple chase behavior
        direction = (player_pos - self.pos).normalize()
        movement = direction * self.speed * 0.016  # Assuming 60 FPS
        
        # Check for collision before moving
        proposed_pos = self.pos + movement
        
        # Basic collision detection
        human_rect = pygame.Rect(proposed_pos.x - self.size, 
                                 proposed_pos.y - self.size, 
                                 self.size*2, self.size*2)
        
        can_move = True
        for rect in collision_rects:
            if human_rect.colliderect(rect):
                can_move = False
                break
        
        if can_move:
            self.pos = proposed_pos

    def draw(self, screen, offset):
        screen.blit(self.sprite, self.pos - offset - pygame.Vector2(self.size, self.size))
        self.draw_health_bar(screen, offset)

    def take_damage(self, damage, bullet_pos):
        """
        Handles damage to the human enemy.
        Returns True if the enemy is destroyed, False otherwise.
        """
        self.health -= damage
        return self.health <= 0

    def get_rect(self):
        """
        Returns a rect for collision detection.
        """
        return pygame.Rect(self.pos.x - self.size, 
                           self.pos.y - self.size, 
                           self.size*2, self.size*2)
    
    def draw_health_bar(self, screen, offset):
        """
        Draw the health bar above the human.
        :param screen: The game screen.
        :param offset: The camera offset.
        """
        bar_width = self.size * 2  # Width of the health bar (same as human size)
        bar_height = 5  # Height of the health bar
        health_ratio = self.health / self.max_health  # Health percentage

        # Calculate the position of the health bar
        bar_x = self.pos.x - offset.x - bar_width // 2
        bar_y = self.pos.y - offset.y - self.size - 10  # Above the human

        # Draw the background (red) and foreground (green) of the health bar
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))  # Red background
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))  # Green foreground