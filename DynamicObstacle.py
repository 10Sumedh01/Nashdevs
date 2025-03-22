import pygame
from Obstacle import Obstacle
from constants import DYNAMIC_COLOR

class DynamicObstacle(Obstacle):
    def __init__(self, pos, size, path, speed):
        super().__init__(pos, size, destructible=False)
        self.path = path
        self.speed = speed
        self.current_target_index = 0

    def update(self):
        target = pygame.Vector2(self.path[self.current_target_index])
        direction = target - self.pos
        if direction.length() < self.speed:
            self.pos = target
            self.current_target_index = (self.current_target_index + 1) % len(self.path)
        else:
            self.pos += direction.normalize() * self.speed

    def draw(self, surface, offset):
        rect = self.get_rect().move(-offset.x, -offset.y)
        pygame.draw.rect(surface, DYNAMIC_COLOR, rect)