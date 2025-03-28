import pygame
import math
from Zombie import Zombie, astar_path  # Import the A* function
from constants import ZOMBIE_SPEED, ZOMBIE_SIZE

SPECIAL_ZOMBIE_IMAGE_PATH = "assets/special_zombie.png"

class SpecialZombie(Zombie):
    def __init__(self, spawn_pos, speed_multiplier=1.0, immobile_duration=3000, harmful=True, flicker=False):
        super().__init__(spawn_pos, speed_multiplier)
        self.is_special = True
        self.size = ZOMBIE_SIZE * 2
        self.speed = ZOMBIE_SPEED * speed_multiplier * 1.2
        self.spawn_time = pygame.time.get_ticks()
        self.immobile_duration = immobile_duration
        self.harmful = harmful
        self.flicker = flicker
        self.health = 200
        
        # Load special zombie image
        self.image = pygame.image.load(SPECIAL_ZOMBIE_IMAGE_PATH).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.original_image = self.image.copy()
        self.flicker_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)

    def update(self, player_pos, obstacles):
        current_time = pygame.time.get_ticks()
        
        # Remain immobile for the specified duration
        if current_time - self.spawn_time < self.immobile_duration:
            return
        
        # Use A* pathfinding to find the player
        if not self.path or self.path_index >= len(self.path):
            self.path = astar_path(self.pos, player_pos, obstacles, cell_size=50)
            self.path_index = 0

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
                    # Recalculate path if collision occurs
                    self.path = astar_path(self.pos, player_pos, obstacles, cell_size=50)
                    self.path_index = 0

        # Update the angle to face the player
        direction = player_pos - self.pos
        if direction.length() > 0:
            self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90

    def draw(self, surface, offset):
        img_rect = self.image.get_rect(center=(self.pos.x - offset.x, self.pos.y - offset.y))
        surface.blit(self.image, img_rect)
        
        # Handle flicker effect
        if self.flicker and (pygame.time.get_ticks() // 250) % 2 == 0:
            self.flicker_surface.fill((255, 200, 0, 128))
            surface.blit(self.flicker_surface, img_rect)
