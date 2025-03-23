import pygame
import math
from constants import ZOMBIE_COLOR, ZOMBIE_SIZE, ZOMBIE_SPEED, COLLISION_THRESHOLD
from MapManager import line_of_sight_clear

class Zombie:
    def __init__(self, spawn_pos, speed_multiplier=1.0):
        self.pos = pygame.Vector2(spawn_pos)
        self.speed = ZOMBIE_SPEED * speed_multiplier
        self.size = ZOMBIE_SIZE
        self.is_special = False
        self.health = 100
        self.angle = 0
        self.path = []
        self.path_index = 0
        self.last_path_update = pygame.time.get_ticks()
        ZOMBIE_IMAGE_PATH = "assets/zombie.png"
        self.original_image = pygame.image.load(ZOMBIE_IMAGE_PATH).convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, (self.size, self.size))
        self.image = self.original_image

    def take_damage(self, damage, game=None):
        self.health -= damage
        return self.health <= 0

    def update(self, player_pos, obstacles, map_manager):
        current_time = pygame.time.get_ticks()
        # Try direct approach if line-of-sight is clear.
        if line_of_sight_clear(self.pos, player_pos, obstacles):
            direction = player_pos - self.pos
            if direction.length() > 0:
                self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
                direction = direction.normalize()
                candidate_pos = self.pos + direction * self.speed
                candidate_rect = pygame.Rect(candidate_pos.x - self.size // 2,
                                             candidate_pos.y - self.size // 2,
                                             self.size, self.size)
                collision = any(candidate_rect.colliderect(obs) for obs in obstacles)
                if not collision:
                    self.pos = candidate_pos
                    self.path = []
                    self.path_index = 0
                    self.last_path_update = current_time
                else:
                    if current_time - self.last_path_update > 500 and map_manager:
                        self.path = map_manager.astar(self.pos, player_pos)
                        self.path_index = 0
                        self.last_path_update = current_time
        else:
            if (not self.path or self.path_index >= len(self.path)) and (current_time - self.last_path_update > 500) and map_manager:
                self.path = map_manager.astar(self.pos, player_pos)
                self.path_index = 0
                self.last_path_update = current_time
            if self.path and self.path_index < len(self.path):
                target = self.path[self.path_index]
                direction = target - self.pos
                if direction.length() < self.speed:
                    self.pos = target
                    self.path_index += 1
                else:
                    direction = direction.normalize()
                    candidate_pos = self.pos + direction * self.speed
                    candidate_rect = pygame.Rect(candidate_pos.x - self.size // 2,
                                                 candidate_pos.y - self.size // 2,
                                                 self.size, self.size)
                    collision = any(candidate_rect.colliderect(obs) for obs in obstacles)
                    if not collision:
                        self.pos = candidate_pos
                    else:
                        if current_time - self.last_path_update > 500 and map_manager:
                            self.path = map_manager.astar(self.pos, player_pos)
                            self.path_index = 0
                            self.last_path_update = current_time
                self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size // 2,
                           self.pos.y - self.size // 2,
                           self.size, self.size)

    def draw(self, surface, offset):
        rotated_image = pygame.transform.rotate(self.original_image, self.angle)
        img_rect = rotated_image.get_rect(center=(self.pos.x - offset.x, self.pos.y - offset.y))
        surface.blit(rotated_image, img_rect)
