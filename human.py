import pygame
import math
from constants import ZOMBIE_SIZE

class Human:
    def __init__(self, pos, speed_multiplier=1.0):
        self.pos = pygame.Vector2(pos)
        self.size = ZOMBIE_SIZE
        self.speed = 100 * speed_multiplier
        self.health = 100
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