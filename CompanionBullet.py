import pygame
from constants import BULLET_COLOR

class CompanionBullet:
    def __init__(self, pos, direction):
        self.pos = pygame.Vector2(pos)
        self.direction = direction.normalize()
        self.speed = 10
        self.size = 5
        self.distance_traveled = 0
        self.max_distance = 500

    def update(self):
        self.pos += self.direction * self.speed
        self.distance_traveled += self.speed

    def draw(self, surface, offset):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.pos.x - offset.x), int(self.pos.y - offset.y)), self.size)