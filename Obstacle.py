import pygame
from constants import DESTRUCTIBLE_COLOR,OBSTACLE_COLOR

class Obstacle:
    def __init__(self, pos, size, destructible=False):
        self.pos = pygame.Vector2(pos)
        self.size = size
        self.destructible = destructible
        self.hp = 100 if destructible else None

    def get_rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size[0], self.size[1])

    def draw(self, surface, offset):
        rect = self.get_rect().move(-offset.x, -offset.y)
        color = DESTRUCTIBLE_COLOR if self.destructible else OBSTACLE_COLOR
        pygame.draw.rect(surface, color, rect)

    def update(self):
        pass