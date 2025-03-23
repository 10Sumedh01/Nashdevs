# Pickup.py

import pygame
from constants import HEALTH_KIT_IMAGE, AMMO_KIT_IMAGE

class Pickup:
    def __init__(self, pos, pickup_type):
        """
        pickup_type: 'health' or 'ammo'
        """
        self.pos = pygame.Vector2(pos)
        self.type = pickup_type
        if self.type == "health":
            self.image = pygame.image.load(HEALTH_KIT_IMAGE).convert_alpha()
        else:
            self.image = pygame.image.load(AMMO_KIT_IMAGE).convert_alpha()
        self.size = self.image.get_width()  # Assume square image
        self.rect = self.image.get_rect(center=self.pos)

    def draw(self, surface, offset):
        surface.blit(self.image, (self.rect.x - offset.x, self.rect.y - offset.y))
