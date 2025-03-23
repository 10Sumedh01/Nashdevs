import math
import pygame
from constants import BULLET_SPEED
from Bullet import Bullet

class AKM:
    def __init__(self):
        self.num_bullets = 5

    def fire(self, pos, target_pos):
        bullets = []
        # Calculate the direction from pos to target.
        direction = target_pos - pos
        if direction.length() != 0:
            direction = direction.normalize()
        # Fire 5 bullets in a straight line.
        for i in range(self.num_bullets):
            bullet = Bullet(pos.copy(), direction)
            bullets.append(bullet)
        return bullets
