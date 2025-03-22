import pygame
from Zombie import Zombie
from constants import ZOMBIE_SPEED,ZOMBIE_SIZE

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
        if current_time - self.spawn_time < self.immobile_duration:
            return
        super().update(player_pos, obstacles)

    def draw(self, surface, offset):
        img_rect = self.image.get_rect(center=(self.pos.x - offset.x, self.pos.y - offset.y))
        surface.blit(self.image, img_rect)
        
        # Handle flicker effect
        if self.flicker and (pygame.time.get_ticks() // 250) % 2 == 0:
            self.flicker_surface.fill((255, 200, 0, 128))
            surface.blit(self.flicker_surface, img_rect)
