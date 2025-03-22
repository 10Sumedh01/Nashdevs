import pygame
from constants import BULLET_SPEED


class Bullet:
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction
        self.speed = BULLET_SPEED
        self.distance_traveled = 0
        self.size = 5

    def update(self):
        self.pos += self.direction * self.speed
        self.distance_traveled += self.speed

    def draw(self, surface, offset):
        pygame.draw.circle(surface, (255, 255, 0), 
                          (int(self.pos.x - offset.x), int(self.pos.y - offset.y)), 
                          self.size)