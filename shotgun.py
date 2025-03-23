import math
import pygame
from constants import BULLET_SPEED
from Bullet import Bullet

class Shotgun:
    def __init__(self):
        self.num_bullets = 3
        self.spread_angle = 30  # Total spread (in degrees) over which bullets are fired

    def fire(self, pos, target_pos):
        bullets = []
        # Calculate base angle from the shooter to target.
        direction = target_pos - pos
        base_angle = math.degrees(math.atan2(direction.y, direction.x))
        # For a 3-bullet spread, compute angle offsets.
        # e.g. center bullet: 0 offset; left bullet: -spread/2; right bullet: +spread/2
        angle_offsets = [0, -self.spread_angle / 2, self.spread_angle / 2]
        for offset in angle_offsets:
            angle = math.radians(base_angle + offset)
            dir_vector = pygame.Vector2(math.cos(angle), math.sin(angle))
            bullet = Bullet(pos.copy(), dir_vector)
            bullets.append(bullet)
        return bullets
