import pygame
import math
from Bullet import Bullet
from constants import PLAYER_MAX_HEALTH, WIDTH, HEIGHT, PLAYER_SPEED, PLAYER_SIZE, PLAYER_START_AMMO, PLAYER_IMAGE_PATH

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
        self.speed = PLAYER_SPEED
        self.size = PLAYER_SIZE
        self.health = PLAYER_MAX_HEALTH
        self.ammo = PLAYER_START_AMMO
        self.last_hit = 0
        self.invincible = False
        self.invincible_duration = 1000
        self.flashlight = True
        self.angle = 0

        # Knife acquisition flag (default: not acquired)
        self.has_knife = False

        # Load images: default gun image and knife image.
        self.gun_image = pygame.image.load(PLAYER_IMAGE_PATH).convert_alpha()
        self.gun_image = pygame.transform.scale(self.gun_image, (self.size, self.size))
        self.knife_image = pygame.image.load("assets/knifeplayer.png").convert_alpha()
        self.knife_image = pygame.transform.scale(self.knife_image, (self.size, self.size))
        # Start with gun image
        self.current_image = self.gun_image

    def take_damage(self, damage):
        if not self.invincible:
            self.health = max(0, self.health - damage)
            self.invincible = True
            self.last_hit = pygame.time.get_ticks()

    def update_invincibility(self):
        if self.invincible and pygame.time.get_ticks() - self.last_hit > self.invincible_duration:
            self.invincible = False

    def shoot(self, target_pos):
        if self.ammo > 0:
            self.ammo -= 1
            direction = (target_pos - self.pos).normalize()
            return Bullet(self.pos.copy(), direction)
        return None

    def knife_attack(self, zombies):
    # Increase the knife attack range
        attack_range = 80  # Changed from 50 to 80
        attacked = []
        for zombie in zombies:
            if (self.pos - zombie.pos).length() < attack_range:
                attacked.append(zombie)
        return attacked


    def update(self, obstacles):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move.y += self.speed

        if move.length() > 0:
            move = move.normalize() * self.speed

        old_pos = self.pos.copy()
        self.pos += move
        for obs in obstacles:
            # Use obs directly since obstacles are pygame.Rect objects.
            if self.get_rect().colliderect(obs):
                self.pos = old_pos
                break

    def update_rotation(self, target_pos):
        direction = target_pos - self.pos
        if direction.length() > 0:
            self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.size//2,
                           self.pos.y - self.size//2,
                           self.size, self.size)

    def draw(self, surface, offset, current_level=1):
        # Use knife image if player has knife, otherwise use gun image.
        if self.has_knife:
            self.current_image = self.knife_image
        else:
            self.current_image = self.gun_image

        rotated_image = pygame.transform.rotate(self.current_image, self.angle)
        img_rect = rotated_image.get_rect(center=(self.pos.x - offset.x, self.pos.y - offset.y))
        surface.blit(rotated_image, img_rect)
        
        # Flashlight effect
        flashlight_radius = 300
        mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 200))
        pygame.draw.circle(mask, (0, 0, 0, 0), 
                           (int(self.pos.x - offset.x), int(self.pos.y - offset.y)), 
                           flashlight_radius)
        surface.blit(mask, (0, 0))
