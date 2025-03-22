import pygame

class Pickup:
    def __init__(self, pos, pickup_type):
        self.pos = pos
        self.type = pickup_type
        self.size = 20
        self.colors = {'health': (0, 255, 0), 'ammo': (255, 165, 0)}

    def draw(self, surface, offset):
        color = self.colors.get(self.type, (255, 255, 255))
        pygame.draw.rect(surface, color, (self.pos.x - offset.x - self.size//2,
                                        self.pos.y - offset.y - self.size//2,
                                        self.size, self.size))